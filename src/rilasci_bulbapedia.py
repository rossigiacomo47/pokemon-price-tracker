"""Modo di rilascio di TUTTE le promo, dalla colonna "Promotion" delle liste di Bulbapedia.

Fonte: Bulbapedia (bulbapedia.bulbagarden.net), licenza CC BY-NC-SA. Le pagine sono salvate in
fonti/*.html (scaricate il 9/10/2026 rispettando robots.txt e la pausa di 5 secondi).
Per ogni promo si usa il PRIMO canale indicato, che e' quello della carta normale. Si ignorano
le versioni Staff, Jumbo e timbrate, che su TCGdex sono varianti separate.

Scrive tabelle/rilasci_bulbapedia.csv: set_id (come TCGdex), numero, testo originale, categoria.

Uso:
    Mac:     .venv/bin/python src/rilasci_bulbapedia.py
    Windows: .venv\\Scripts\\python src\\rilasci_bulbapedia.py
"""

import re
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

RADICE = Path(__file__).resolve().parent.parent
PAGINE = {  # file in fonti/ -> set_id usato nei nostri dati
    "smp": "smp", "swshp": "swshp", "svp": "svp", "mep": "mep",
    "sm-p": "SM-P", "s-p": "S-P", "sv-p": "SV-P", "m-p": "M-P",
}

# regole in ordine: vince la prima che corrisponde
REGOLE = [
    (r"unknown promotion", "da classificare"),
    (r"pok[eé]mon cent(er|re)|pok[eé]mon store|special delivery", "Pokemon Center"),
    (r"case file", "prodotto speciale"),
    # mostre, musei e collaborazioni artistiche (Munch, Van Gogh...): restano insieme in "altro"
    (r"retrospective|exhibition|museum|van gogh|munch|collaborat", "altro"),
    (r"build & battle|prerelease", "evento o torneo"),
    (r"battle deck|battle academy|deck build box|starter (set|deck)|theme deck|\bdeck\b", "prodotto speciale"),
    (r"prize|participation|championship|champion'?s league|tournament|\bgym\b|organizer|\bevent\b|league|play!|worlds|professor|regional|\bbattle\b",
     "evento o torneo"),
    (r"purchase campaign|pre-?order|early purchase|purchase bonus|get! campaign|campaign|friendly shop|gift with purchase|seven-eleven|7-eleven|bonus|giveaway|purchase",
     "campagna d'acquisto"),
    (r"corocoro|magazine|issue|mcdonald|happy meal|movie|film|cinema|theat|general mills|cereal|build-a-bear|collaborat|museum|insert",
     "altro"),
    (r"collection|box|tin\b|tins\b|blister|pack|\bset\b|chest|elite trainer|premium|bundle|album|kit|portfolio|figure|\bpin\b|poster|binder|calendar",
     "prodotto speciale"),
]


class Tabelle(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.stack, self.cell, self.row = [], [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.stack.append([])
        elif tag == "tr" and self.stack:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append(" || ")

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None and self.stack:
            self.stack[-1].append(self.row)
            self.row = None
        elif tag == "table" and self.stack:
            self.tables.append(self.stack.pop())

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)


def categoria(testo):
    canali = [c.strip() for c in str(testo).split("||") if c.strip()]
    utili = [c for c in canali if not re.search(r"staff|jumbo|stamp", c, re.I)] or canali
    primo = utili[0] if utili else ""
    for regex, cat in REGOLE:
        if re.search(regex, primo, re.I):
            return primo, cat
    return primo, "altro"


def numero_norm(set_id, num):
    s = str(num).split("/")[0].strip().upper()
    m = re.match(r"^([A-Z]*?)0*(\d+)$", s)
    return f"{m.group(1)}{int(m.group(2))}" if m else s


def main():
    righe = []
    for file, set_id in PAGINE.items():
        p = Tabelle()
        p.feed((RADICE / "fonti" / f"{file}.html").read_text(encoding="utf-8"))
        tab = max(p.tables, key=len)
        intest = tab[0]
        i_num, i_nome, i_prom = 0, intest.index("Card name"), intest.index("Promotion")
        for r in tab[1:]:
            if len(r) <= i_prom or not re.search(r"\d", r[i_num]):
                continue
            primo, cat = categoria(r[i_prom])
            righe.append({"set_id": set_id, "numero": r[i_num], "num": numero_norm(set_id, r[i_num]),
                          "nome": r[i_nome][:60], "canale_principale": primo, "rilascio": cat,
                          "promotion_bulbapedia": r[i_prom], "fonte": "Bulbapedia (CC BY-NC-SA), 9/10/2026"})
    t = pd.DataFrame(righe)
    t.to_csv(RADICE / "tabelle" / "rilasci_bulbapedia.csv", index=False)
    print(t.groupby(["set_id", "rilascio"]).size().unstack(fill_value=0).to_string())
    print("totale:", len(t))


if __name__ == "__main__":
    main()
