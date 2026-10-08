"""Blocco 3 - Genera le PROPOSTE delle tabelle di conversione in tabelle/.

    tabelle/set.csv      un set per riga: era, tipo di set, collegamento a TCGCSV
    tabelle/rarita.csv   nome originale della rarita' -> rarita' armonizzata e perimetro
    tabelle/rilasci.csv  indizi (timbri, set) -> modalita' di rilascio

Le tabelle sono pensate per essere corrette a mano da Giacomo: se esistono gia',
questo script NON le sovrascrive (serve --rigenera). La colonna `stato` dice se una
riga e' "proposta" o "approvata".

Uso:
    Mac:     .venv/bin/python src/tabelle.py [--rigenera]
    Windows: .venv\\Scripts\\python src\\tabelle.py [--rigenera]
Richiede la cache del download TCGdex (cache/AAAA-MM-GG/set) e data/riferimento/.
"""

import argparse
import json
import re
from pathlib import Path

import pandas as pd

RADICE = Path(__file__).resolve().parent.parent
TAB = RADICE / "tabelle"
RIF = RADICE / "data" / "riferimento"

# ------------------------------------------------------------------ set

SERIE_ERA = {
    "sm": "Sole e Luna", "SM": "Sole e Luna",
    "swsh": "Spada e Scudo", "S": "Spada e Scudo",
    "sv": "Scarlatto e Violetto", "SV": "Scarlatto e Violetto",
    "me": "Mega", "M": "Mega",
}

SET_PROMO = {"smp", "swshp", "svp", "mep", "SV-P", "M-P"}
SET_SOTTOSET = {"sma", "swsh4.5sv", "cel25cc", "30th-c"}  # + *tg, *gg
SET_SPECIALI = {
    # internazionali: set speciali, mezzi set, mazzi e prodotti particolari
    "sm3.5", "sm7.5", "sm115", "det1", "swsh3.5", "swsh4.5", "cel25", "swsh10.5", "swsh12.5",
    "sv03.5", "sv04.5", "sv06.5", "sv08.5", "sv10.5b", "sv10.5w", "me02.5", "30th",
    "fut2020", "mfb", "sve", "mee", "tk-sm-r", "tk-sm-l",
    "2017sm", "2018sm", "2019sm", "2021swsh", "2022swsh", "2023sv", "2024sv",
    # giapponesi: high class pack, set speciali e mazzi
    "SM8b", "SM12a", "S4a", "S6a", "S8a", "S8b", "S10b", "S12a", "SV2a", "SV4a", "SV8a",
    "M2a", "M6a", "SVK", "SVLS", "SVLN", "MC", "MF", "SMP2", "SM0",
}

# Collegamenti TCGdex -> TCGCSV scritti a mano (sigle e nomi diversi nelle due fonti).
GRUPPI_MANUALI = {
    ("en", "sm1"): 1863, ("en", "sm2"): 1919, ("en", "sm3"): 1957, ("en", "sm4"): 2071,
    ("en", "sm5"): 2178, ("en", "sm6"): 2209, ("en", "sm8"): 2328, ("en", "sm9"): 2377,
    ("en", "sm10"): 2420, ("en", "sm11"): 2464, ("en", "sm12"): 2534, ("en", "sma"): 2594,
    ("en", "smp"): 1861, ("en", "swshp"): 2545, ("en", "swsh1"): 2585, ("en", "swsh4.5sv"): 2781,
    ("en", "cel25cc"): 2931, ("en", "30th-c"): 24837, ("en", "2017sm"): 2148,
    ("en", "2018sm"): 2364, ("en", "2019sm"): 2555, ("en", "2021swsh"): 2782,
    ("en", "2022swsh"): 3150, ("en", "2023sv"): 23306, ("en", "2024sv"): 24163,
    ("en", "tk-sm-r"): 2069, ("en", "tk-sm-l"): 2069,
    ("ja", "SM1p"): 23692, ("ja", "SM2p"): 23693, ("ja", "SM3p"): 23694, ("ja", "SM4p"): 23707,
    ("ja", "SM5p"): 23695, ("ja", "MC"): 24567, ("ja", "SVLS"): 23793,
}


def tipo_set(lingua, sid):
    if sid in SET_PROMO:
        return "promo"
    if sid in SET_SOTTOSET or sid.endswith(("tg", "gg")):
        return "sottoset"
    if sid in SET_SPECIALI or sid.startswith("CS"):
        return "speciale"
    return "principale"


def era_di(serie_id, data):
    if serie_id in SERIE_ERA:
        return SERIE_ERA[serie_id]
    # McDonald's, trainer kit: era dalla data di uscita
    if data < "2019-11-15":
        return "Sole e Luna"
    if data < "2023-03-31":
        return "Spada e Scudo"
    if data < "2025-09-26":
        return "Scarlatto e Violetto"
    return "Mega"


def genera_set(cartella_cache):
    gruppi = {
        l: pd.read_parquet(RIF / f"tcgcsv_prodotti_{l}.parquet").drop_duplicates("gruppo_id")
        for l in ("en", "ja")
    }
    righe = []
    for p in sorted(cartella_cache.glob("*.json")):
        lingua = p.name.split("_", 1)[0]
        s = json.loads(p.read_text(encoding="utf-8"))
        serie = (s.get("serie") or {}).get("id")
        data = s.get("releaseDate") or ""
        moderne = {"en": {"sm", "swsh", "sv", "me"}, "ja": {"SM", "S", "SV", "M"}}[lingua]
        if serie == "tcgp" or not (serie in moderne or data >= "2016-12-01"):
            continue
        sid = s["id"]
        if sid.startswith("CS") and lingua == "ja":
            continue  # doppioni vuoti "Triplet Beat" su TCGdex
        g = gruppi[lingua]
        gid, metodo = GRUPPI_MANUALI.get((lingua, sid)), "manuale"
        if gid is None:
            sigla = sid if lingua == "ja" else ((s.get("abbreviation") or {}).get("official") or "")
            m = g[g.gruppo_sigla.fillna("").str.lower() == sigla.lower()] if sigla else g.iloc[0:0]
            if len(m) != 1 and lingua == "en":
                nome = s["name"].lower()
                m = g[g.gruppo_nome.str.lower().str.endswith(": " + nome) | g.gruppo_nome.str.lower().eq(nome)]
            gid, metodo = (int(m.iloc[0].gruppo_id), "sigla o nome") if len(m) == 1 else (None, "nessuno")
        righe.append({
            "lingua": lingua, "set_id": sid, "set_nome": s["name"], "serie_id": serie,
            "era": era_di(serie, data), "data_uscita": data,
            "carte_ufficiali": (s.get("cardCount") or {}).get("official"),
            "carte_su_tcgdex": len(s.get("cards") or []),
            "tipo_set": tipo_set(lingua, sid),
            "tcgcsv_gruppo_id": gid, "collegamento": metodo,
            "nome_tcgcsv": g[g.gruppo_id == gid].gruppo_nome.iloc[0] if gid else None,
            "note": "set vuoto su TCGdex: carte dal catalogo TCGCSV" if not s.get("cards") else "",
            "stato": "proposta",
        })
    return pd.DataFrame(righe).sort_values(["lingua", "data_uscita", "set_id"])


# ------------------------------------------------------------------ rarita'

# (lingua, rarita' originale) -> (rarita' armonizzata, perimetro, nota)
IR, SIR, CHR, GOLD, SHINY, PROMO = (
    "illustration rare", "special illustration rare", "character rare",
    "gold-hyper-rainbow", "shiny", "promo",
)
MAPPA_RARITA = {
    "Illustration rare": (IR, "dentro", ""),
    "Illustration Rare": (IR, "dentro", ""),
    "Art Rare": (IR, "dentro", "AR giapponese"),
    "Special illustration rare": (SIR, "dentro", ""),
    "Special Illustration Rare": (SIR, "dentro", ""),
    "Special Art Rare": (SIR, "dentro", "SAR giapponese"),
    "Character Rare": (CHR, "dentro", "CHR giapponese"),
    "Character Super Rare": (CHR, "dentro", "CSR giapponese"),
    "Hyper rare": (GOLD, "dentro", "SV: carte dorate"),
    "Hyper Rare": (GOLD, "dentro", "HR giapponese (arcobaleno) o hyper SV"),
    "Mega Hyper Rare": (GOLD, "dentro", ""),
    "Mega Ultra Rare": (GOLD, "dentro", ""),
    "Rainbow Rare": (GOLD, "dentro", ""),
    "Secret Rare": (GOLD, "dentro", "SM/SWSH: arcobaleno e dorate (alternate art riconosciute a parte)"),
    "Shiny rare": (SHINY, "dentro", ""),
    "Shiny Rare": (SHINY, "dentro", ""),
    "Shiny rare V": (SHINY, "dentro", ""),
    "Shiny rare VMAX": (SHINY, "dentro", ""),
    "Shiny Ultra Rare": (SHINY, "dentro", ""),
    "Shiny Holo Rare": (SHINY, "dentro", "Shiny Vault"),
    "Shiny Secret Rare": (SHINY, "dentro", "SSR giapponese"),
    "Promo": (PROMO, "dentro", ""),
    "Classic Collection": (PROMO, "dentro", "ristampe Classic Collection"),
    "Black White Rare": ("da verificare", "da verificare", "rarita' nuova (Black Bolt / White Flare)"),
    "Mega Attack Rare": ("da verificare", "da verificare", "rarita' nuova (era Mega)"),
    "RGB Rare": ("da verificare", "da verificare", "rarita' nuova"),
    "Futuristic Rare": ("da verificare", "da verificare", "rarita' nuova"),
}
FUORI = {
    "Common", "Uncommon", "Rare", "Holo Rare", "Rare Holo", "Double rare", "Double Rare",
    "Triple Rare", "Ultra Rare", "Super Rare", "Holo Rare V", "Holo Rare VMAX", "Holo Rare VSTAR",
    "Radiant Rare", "Kagayaku", "Amazing Rare", "ACE SPEC Rare", "ACE Rare", "Rare Ace",
    "Prism Rare", "Trainer Rare", "Pikachu Rare", "Shining", "Rare BREAK", "None", "Unconfirmed",
}


def genera_rarita():
    snap = sorted((RADICE / "data" / "mercato").glob("????-W??.parquet"))[-1]
    df = pd.read_parquet(snap, columns=["lingua", "categoria", "rarita_tcgdex"])
    df = df[df.categoria == "Pokemon"]
    righe = []
    for (lingua, r), n in df.groupby(["lingua", df.rarita_tcgdex.fillna("(vuota)")]).size().items():
        righe.append(("TCGdex", lingua, r, n))
    for lingua in ("en", "ja"):
        t = pd.read_parquet(RIF / f"tcgcsv_prodotti_{lingua}.parquet")
        t = t[t.numero.notna()]
        for r, n in t.rarita.fillna("(vuota)").value_counts().items():
            righe.append(("TCGplayer", lingua, r, n))
    out = []
    for fonte, lingua, r, n in righe:
        if r in MAPPA_RARITA:
            arm, per, nota = MAPPA_RARITA[r]
        elif r in FUORI:
            arm, per, nota = "fuori", "fuori", ""
        else:
            arm, per, nota = "mancante", "vedi nota", "rarita' assente: si cerca in TCGplayer (set + numero)"
        if r == "Ultra Rare":
            nota = ("giapponese: UR = dorata -> gold-hyper-rainbow" if lingua == "ja"
                    else "full art normale (fuori), tranne le alternate art di Spada e Scudo -> SIR")
            if lingua == "ja":
                arm, per = GOLD, "dentro"
        if r == "Secret Rare" and lingua == "ja":
            arm, per, nota = "da verificare", "da verificare", "Secret Rare giapponese su TCGdex: controllare caso per caso"
        out.append({"fonte": fonte, "lingua": lingua, "rarita_originale": r, "varianti_o_prodotti": int(n),
                    "rarita_armonizzata": arm, "perimetro": per, "nota": nota, "stato": "proposta"})
    return pd.DataFrame(out).sort_values(["fonte", "lingua", "varianti_o_prodotti"], ascending=[True, True, False])


# ------------------------------------------------------------------ rilasci

RILASCI = [
    # (tipo di indizio, valore, modalita' di rilascio, nota)
    ("famiglia", "carta da busta", "busta", ""),
    ("set", "cel25cc", "prodotto speciale", "Celebrations Classic Collection (CLAUDE.md sezione 2)"),
    ("set", "30th-c", "prodotto speciale", "30th Classic Collection"),
    ("set", "McDonald's", "altro", "promozione McDonald's (Happy Meal)"),
    ("timbro", "pokemon-center", "Pokemon Center", ""),
    ("timbro", "staff", "evento o torneo", "copie per lo staff di eventi"),
    ("timbro", "regional-championships", "evento o torneo", ""),
    ("timbro", "worlds-*", "evento o torneo", "Campionati mondiali"),
    ("timbro", "player-rewards-program", "evento o torneo", "premi Play! Pokemon"),
    ("timbro", "professor-program", "evento o torneo", ""),
    ("timbro", "gym-challenge", "evento o torneo", ""),
    ("timbro", "pre-release", "evento o torneo", "prerelease"),
    ("timbro", "prerelease", "evento o torneo", "prerelease"),
    ("timbro", "league", "evento o torneo", "Pokemon League"),
    ("timbro", "ultra-ball-league", "evento o torneo", ""),
    ("timbro", "illustration-contest-*", "evento o torneo", "concorso di illustrazione"),
    ("timbro", "set-logo", "prodotto speciale", "carte timbrate in box, poster e collezioni"),
    ("timbro", "25th-celebration", "prodotto speciale", ""),
    ("timbro", "30th-anniversary", "prodotto speciale", ""),
    ("timbro", "snowflake", "prodotto speciale", "calendario dell'Avvento"),
    ("timbro", "trick-or-trade", "prodotto speciale", "buste di Halloween"),
    ("timbro", "eb-games", "prodotto speciale", "esclusiva di un negozio"),
    ("timbro", "gamestop", "prodotto speciale", "esclusiva di un negozio"),
    ("timbro", "bulbasaur|charmander|squirtle|pikachu", "prodotto speciale", "timbri delle collezioni"),
    ("timbro", "(altro timbro)", "altro", "timbro non riconosciuto: da classificare"),
    ("promo senza timbro", "*", "da classificare", "nessun indizio automatico: revisione manuale sopra 20 €"),
]


def genera_rilasci():
    return pd.DataFrame(RILASCI, columns=["indizio", "valore", "modalita_rilascio", "nota"]).assign(stato="proposta")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rigenera", action="store_true")
    args = parser.parse_args()
    TAB.mkdir(exist_ok=True)
    cache = sorted((RADICE / "cache").glob("20??-??-??"))[-1] / "set"
    for nome, funzione in (("set.csv", lambda: genera_set(cache)), ("rarita.csv", genera_rarita),
                           ("rilasci.csv", genera_rilasci)):
        dest = TAB / nome
        if dest.exists() and not args.rigenera:
            print(f"{nome}: esiste gia', non la tocco (usa --rigenera)")
            continue
        tab = funzione()
        tab.to_csv(dest, index=False)
        print(f"{nome}: {len(tab)} righe")


if __name__ == "__main__":
    main()
