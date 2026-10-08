"""Blocco 1 - Riepilogo della fotografia del mercato.

Legge data/mercato/AAAA-Wnn.parquet e scrive riepiloghi/blocco1_AAAA-Wnn.md con:
perimetro PROVVISORIO (la classificazione definitiva arriva nel blocco 3 con
rarita.csv), conteggi per famiglia, lingua e rarita', copertura dei prezzi
giapponesi, effetto della soglia bulk, distribuzione dei prezzi e carte di controllo.

Uso:
    Mac:     .venv/bin/python src/riepilogo.py 2026-W41
    Windows: .venv\\Scripts\\python src\\riepilogo.py 2026-W41
"""

import json
import sys
from pathlib import Path

import pandas as pd

from prezzi import espandi_ambigui

RADICE = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RADICE / "config.json").read_text(encoding="utf-8"))
SOGLIA = CONFIG["soglia_bulk_eur"]

# ---------------------------------------------------------------- perimetro provvisorio
SET_PROMO = {"smp", "swshp", "svp", "mep", "SV-P", "M-P"}
SET_SPECIALI_PROMO = {"cel25cc"}  # Celebrations Classic Collection (CLAUDE.md sezione 2)
RARITA_DENTRO = {
    "Illustration rare", "Special illustration rare", "Hyper rare",
    "Shiny rare", "Shiny Ultra Rare", "Shiny rare V", "Shiny rare VMAX",
    "Character Rare", "Character Super Rare", "Mega Hyper Rare",
}
RARITA_DA_VERIFICARE = {
    "Black White Rare", "Mega Attack Rare", "RGB Rare", "Futuristic Rare",
}
RARITA_MANCANTE = {None, "None", ""}


def numero_oltre_ufficiale(riga):
    try:
        return int(str(riga["numero"]).lstrip("0") or 0) > int(riga["set_carte_ufficiali"] or 0)
    except (TypeError, ValueError):
        return False


def classifica(riga):
    """Restituisce (famiglia, perimetro, motivo). Provvisorio, da confermare nel blocco 3."""
    if riga["categoria"] != "Pokemon":
        return None, "fuori", "non e' una carta Pokemon"
    if riga["variante_formato"] == "jumbo":
        return None, "fuori", "formato jumbo"

    r = riga["rarita_tcgdex"]
    promo = (
        r == "Promo"
        or riga["set_id"] in SET_PROMO
        or riga["set_id"] in SET_SPECIALI_PROMO
        or "McDonald" in str(riga["set_nome"])
    )
    if promo:
        return "promo e rilascio speciale", "dentro", "promo"
    if pd.notna(riga["variante_timbro"]):
        # Decisione D5 (8/10/2026): stamped -> promo e rilascio speciale, dentro il perimetro.
        return "promo e rilascio speciale", "dentro", "variante stamped"

    fam = "carta da busta"
    if str(riga["set_id"]).endswith(("tg", "gg")):
        return fam, "dentro", "galleria"
    if r in RARITA_DENTRO:
        return fam, "dentro", r
    if r == "Ultra Rare":
        if riga["lingua"] == "ja":
            return fam, "dentro", "UR giapponese (gold)"
        if riga["serie_id"] == "swsh":
            return fam, "da verificare", "Ultra Rare SWSH: full art normale o alternate art?"
        return fam, "fuori", "full art normale"
    if r == "Secret Rare":
        if riga["lingua"] == "en":
            return fam, "dentro", "gold/rainbow (Secret Rare)"
        return fam, "da verificare", "Secret Rare giapponese: SR (full art) o altro?"
    if r in RARITA_DA_VERIFICARE:
        return fam, "da verificare", f"rarita' nuova: {r}"
    if r in RARITA_MANCANTE:
        if numero_oltre_ufficiale(riga):
            return fam, "da verificare", "rarita' mancante, numero oltre il totale del set"
        return fam, "fuori", "rarita' mancante, numero dentro il set (probabile comune)"
    return fam, "fuori", r


# ---------------------------------------------------------------- carte di controllo
# Corrispondenza nome+set del CSV -> (lingua, id TCGdex). Pikachu Munch non e' su TCGdex.
CONTROLLO_ID = {
    ("Charizard VSTAR", "SWSH Black Star Promos"): ("en", "swshp-SWSH262"),
    ("Pikachu VMAX", "VMAX Climax"): ("ja", "S8b-223"),
    ("Umbreon Gold Star", "Celebrations (Classic Collection)"): ("en", "cel25cc-CC015"),
    ("Pikachu ex", "Surging Sparks"): ("en", "sv08-238"),
    ("Pikachu with Grey Felt Hat", "SV Black Star Promos"): ("en", "svp-085"),
    ("Charmander", "151"): ("en", "sv03.5-168"),
    ("Eevee (Yu Nagaba)", "SV-P Promos"): ("ja", "SV-P-062"),
    ("Charmander", "Pokémon Card 151"): ("ja", "SV2a-168"),
    ("Squirtle", "151"): ("en", "sv03.5-170"),
    ("Charizard ex", "151"): ("en", "sv03.5-199"),
    ("Umbreon ex", "Terastal Festival ex"): ("ja", "SV8a-217"),
    ("Mewtwo V", "Pokémon GO"): ("en", "swsh10.5-072"),
    ("Mewtwo VSTAR", "Crown Zenith (Galarian Gallery)"): ("en", "swsh12.5gg-GG44"),
    ("Pikachu ex", "Super Electric Breaker"): ("ja", "SV8-132"),
}


def tabella_controllo(df, settimana):
    controllo = pd.read_csv(RADICE / "carte_controllo.csv")
    tcgcsv_file = RADICE / "data" / "mercato" / f"{settimana}_tcgcsv_promo_ja.parquet"
    tcgcsv = pd.read_parquet(tcgcsv_file) if tcgcsv_file.exists() else pd.DataFrame()
    da, a = CONFIG["fascia_nm_da_pct"] / 100, CONFIG["fascia_nm_a_pct"] / 100
    righe = []
    for _, c in controllo.iterrows():
        minimo = float(c["nm_offerta_min_eur"])
        fascia = (minimo * (1 + da), minimo * (1 + a))
        centro = sum(fascia) / 2
        chiave = CONTROLLO_ID.get((c["nome"], c["set"]))
        trend, campo, fonte_rif = None, "", ""
        if chiave:
            lingua, cid = chiave
            cand = df[(df.lingua == lingua) & (df.id == cid) & df.variante_timbro.isna()]
            validi = cand[cand.prezzo_rif_eur.notna()].sort_values("versione", na_position="first")
            if len(validi):
                trend, campo = validi.iloc[0].prezzo_rif_eur, validi.iloc[0].campo_prezzo
                fonte_rif = f"TCGdex `{cid}`"
            elif len(cand):
                campo = cand.iloc[0].campo_prezzo
                fonte_rif = f"TCGdex `{cid}`: nessun prezzo Cardmarket"
            else:
                fonte_rif = f"`{cid}` non trovata"
        else:
            fonte_rif = "non presente su TCGdex"
            if len(tcgcsv) and "288" in str(c["numero"]):
                usd = tcgcsv[tcgcsv.numero.astype(str).str.startswith("288/SM-P")].market_usd
                if usd.notna().any():
                    fonte_rif += f"; TCGplayer {usd.dropna().iloc[0]:.2f} $"
                else:
                    fonte_rif += "; TCGplayer: nessun prezzo"
        scarto = f"{(centro / trend - 1) * 100:+.0f}%" if trend else "—"
        righe.append({
            "Carta": f"{c['nome']} ({c['set']}, {c['lingua']})",
            "Minimo NM": f"{minimo:.2f} €",
            "Fascia NM (+5%, ipotesi)": f"{fascia[0]:.0f}–{fascia[1]:.0f} €",
            "Trend Cardmarket": f"{trend:.2f} €" if trend else "—",
            "Centro fascia / trend": scarto,
            "Fonte del trend": fonte_rif + (f" ({campo})" if trend else ""),
        })
    return pd.DataFrame(righe)


# ---------------------------------------------------------------- riepilogo

def md(tabella):
    """Tabella in formato Markdown (senza librerie aggiuntive)."""
    colonne = [str(c) for c in tabella.columns]
    righe = ["| " + " | ".join(colonne) + " |", "|" + "---|" * len(colonne)]
    for valori in tabella.itertuples(index=False):
        righe.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in valori) + " |")
    return "\n".join(righe)


def main():
    settimana = sys.argv[1] if len(sys.argv) > 1 else sorted((RADICE / "data" / "mercato").glob("????-W??.parquet"))[-1].stem
    df = espandi_ambigui(pd.read_parquet(RADICE / "data" / "mercato" / f"{settimana}.parquet"))
    classi = df.apply(classifica, axis=1, result_type="expand")
    df["famiglia"], df["perimetro"], df["motivo"] = classi[0], classi[1], classi[2]
    df["ha_prezzo"] = df.prezzo_rif_eur.notna()
    df["sopra_soglia"] = df.prezzo_rif_eur >= SOGLIA

    out = [f"# Blocco 1 — Riepilogo della fotografia {settimana}\n",
           f"Fonte: TCGdex (prezzi Cardmarket in EUR, `trend` o `trend-holo` secondo la regola di CLAUDE.md 4.1), "
           f"data {df.data_fotografia.iloc[0]}. Una riga = una variante. "
           f"**Perimetro provvisorio**: la classificazione definitiva arriva nel blocco 3.\n"]

    tot = df.groupby("lingua").agg(varianti=("id", "size"), carte=("id", "nunique"), con_prezzo=("ha_prezzo", "sum"))
    out += ["## 1. Totali della fotografia\n", md(tot.reset_index()), ""]

    per = df.groupby(["perimetro", "lingua"]).agg(varianti=("id", "size"), con_prezzo=("ha_prezzo", "sum"),
                                                  sopra_soglia=("sopra_soglia", "sum")).reset_index()
    out += [f"## 2. Perimetro provvisorio (soglia bulk {SOGLIA} €)\n", md(per), ""]

    dentro = df[df.perimetro == "dentro"]
    fam = dentro.groupby(["famiglia", "lingua"]).agg(varianti=("id", "size"), con_prezzo=("ha_prezzo", "sum"),
                                                     sopra_soglia=("sopra_soglia", "sum")).reset_index()
    out += ["## 3. Dentro il perimetro, per famiglia e lingua\n", md(fam), ""]

    mot = dentro.groupby(["lingua", "motivo"]).agg(varianti=("id", "size"), con_prezzo=("ha_prezzo", "sum"),
                                                   sopra_soglia=("sopra_soglia", "sum")).reset_index().sort_values(["lingua", "sopra_soglia"], ascending=[True, False])
    out += ["## 4. Dentro il perimetro, per rarità o motivo\n", md(mot), ""]

    dv = df[df.perimetro == "da verificare"].groupby(["lingua", "motivo"]).agg(
        varianti=("id", "size"), con_prezzo=("ha_prezzo", "sum"), sopra_soglia=("sopra_soglia", "sum")).reset_index()
    out += ["## 5. Da verificare (decisioni per te o per il blocco 3)\n", md(dv), ""]

    sens = []
    for s in (1, 2, 3, 5, 10, 15, 20):
        r = {"soglia": f"{s} €"}
        for l in ("en", "ja"):
            r[l] = int(((dentro.lingua == l) & (dentro.prezzo_rif_eur >= s)).sum())
        r["totale"] = r["en"] + r["ja"]
        sens.append(r)
    out += ["## 6. Effetto della soglia bulk (varianti del perimetro che restano)\n", md(pd.DataFrame(sens)), ""]

    usate = dentro[dentro.sopra_soglia]
    fasce = pd.cut(usate.prezzo_rif_eur, [SOGLIA, 10, 50, 200, 1e9], right=False,
                   labels=[f"{SOGLIA}–10 €", "10–50 €", "50–200 €", ">200 €"])
    dist = usate.groupby([fasce, usate.lingua], observed=False).size().unstack(fill_value=0).reset_index()
    perc = usate.prezzo_rif_eur.quantile([0.1, 0.25, 0.5, 0.75, 0.9]).round(2)
    out += ["## 7. Prezzi delle carte che entrerebbero nel modello\n", md(dist), "",
            "Percentili (10°, 25°, mediana, 75°, 90°): " + ", ".join(f"{v:.2f} €" for v in perc), ""]

    ja = df[(df.lingua == "ja") & (df.categoria == "Pokemon")]
    cop = ja.groupby("serie_id").agg(varianti=("id", "size"), con_prezzo=("ha_prezzo", "sum"))
    cop["copertura"] = (cop.con_prezzo / cop.varianti * 100).round(0).astype(int).astype(str) + "%"
    out += ["## 8. Giapponesi: copertura dei prezzi Cardmarket su TCGdex (solo carte Pokémon)\n", md(cop.reset_index()), ""]

    divise = dentro[dentro.versione.notna()]
    amb = divise.groupby(["lingua", "set_id"]).size().sort_values(ascending=False).head(10)
    out += ["## 9. Prezzi ambigui divisi in versione normale e foil (decisione D4)\n",
            f"Nel perimetro: {int((divise.versione == 'normale').sum())} varianti ambigue → "
            f"{len(divise)} righe (normale + foil). Set principali:\n",
            md(amb.reset_index(name="righe")), ""]

    out += ["## 10. Carte di controllo\n",
            "Fascia NM = minimo → minimo +5% (ipotesi dichiarata, CLAUDE.md 4.5c). "
            "Trend = prezzo di riferimento Cardmarket, condizione e lingua non filtrate.\n",
            md(tabella_controllo(df, settimana)), ""]

    errori = RADICE / "data" / "log" / f"errori_{settimana}.csv"
    n_err = len(pd.read_csv(errori)) if errori.exists() else 0
    out += ["## 11. Errori di download\n", f"{n_err} richieste fallite (registrate in `data/log/`), nessun dato inventato.", ""]

    testo = "\n".join(out)
    dest = RADICE / "riepiloghi" / f"blocco1_{settimana}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")
    print(testo)


if __name__ == "__main__":
    main()
