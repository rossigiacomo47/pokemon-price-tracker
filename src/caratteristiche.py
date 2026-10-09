"""Blocco 3 - Caratteristiche delle carte (le 18 variabili di CLAUDE.md sezione 5).

Legge la fotografia (con la regola dei prezzi ambigui di src/prezzi.py), le tabelle in
tabelle/ (set, rarita', rilasci), iconici.csv e le tabelle di riferimento in
data/riferimento/ (TCGCSV, PokeAPI). Scrive:

    data/caratteristiche/AAAA-Wnn.parquet   una riga per variante, con le variabili
    riepiloghi/blocco3_AAAA-Wnn.md          conteggi, casi incerti, combinazioni chiave

Aggiunge anche il CATALOGO delle carte giapponesi che TCGdex non ha (set vuoti e promo
SM-P / S-P, decisione del 9/10/2026): nome, numero, rarita' e foto da TCGCSV, senza
prezzo Cardmarket. Non entrano nell'addestramento, servono per la ricerca e come
comparabili con i prezzi NM inseriti a mano.

Uso:
    Mac:     .venv/bin/python src/caratteristiche.py 2026-W41
    Windows: .venv\\Scripts\\python src\\caratteristiche.py 2026-W41
"""

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from prezzi import espandi_ambigui

RADICE = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RADICE / "config.json").read_text(encoding="utf-8"))
TAB = RADICE / "tabelle"
RIF = RADICE / "data" / "riferimento"
SOGLIA = CONFIG["soglia_bulk_eur"]

RARITA_ALTE = {"illustration rare", "special illustration rare", "character rare", "character super rare",
               "gold-hyper-rainbow", "shiny", "galleria"}
GRUPPI_PROMO_JA = {23881: "SM-P", 23876: "S-P", 23847: "s8a-P"}  # assenti su TCGdex


def norm_numero(x):
    """'062/SV-P' -> '62', 'SWSH262' -> 'SWSH262', 'TG01/TG30' -> 'TG1'."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    s = str(x).split("/")[0].strip().upper().replace(" ", "")
    m = re.match(r"^([A-Z\-]*?)0*(\d+)([A-Z]*)$", s)
    return f"{m.group(1)}{int(m.group(2))}{m.group(3)}" if m else s


def mancante(r):
    return r is None or (isinstance(r, float) and math.isnan(r)) or r in ("None", "")


# ------------------------------------------------------------------ TCGCSV

def indice_tcgcsv():
    """(lingua, gruppo, numero normalizzato) -> rarita', nomi, alternate art."""
    pezzi = []
    for lingua in ("en", "ja"):
        t = pd.read_parquet(RIF / f"tcgcsv_prodotti_{lingua}.parquet")
        t = t[t.numero.notna()].copy()
        t["lingua"] = lingua
        pezzi.append(t)
    t = pd.concat(pezzi, ignore_index=True)
    t["num"] = t.numero.map(norm_numero)
    t["base"] = ~t.nome.str.contains(r"\(", regex=True)
    t = t.sort_values("base", ascending=False)

    def riassumi(g):
        rar = g.rarita.dropna()
        rar = rar[rar != "None"]
        return pd.Series({
            "rarita_tcgp": rar.iloc[0] if len(rar) else None,
            "nomi_tcgp": " | ".join(g.nome.astype(str).head(6)),
            "alt_art": g.nome.str.contains("Alternate", regex=False).any(),
            "prodotto_tcgp": int(g.prodotto_id.iloc[0]),
        })

    return t.groupby(["lingua", "gruppo_id", "num"]).apply(riassumi, include_groups=False).reset_index()


# ------------------------------------------------------------------ Pokemon

def tabella_specie():
    sp = pd.read_csv(RIF / "pokeapi_specie.csv")
    sp["leggendario"] = sp.is_legendary.astype(bool) | sp.is_mythical.astype(bool)
    return sp.set_index("id")


def pokemon_da_nome(nome, lingua, sp):
    """Cerca il nome di una specie dentro il nome della carta (il piu' lungo vince)."""
    col = "nome_ja" if lingua == "ja" else "nome_en"
    migliore, lung = None, 0
    for sid, n in sp[col].dropna().items():
        if len(n) > lung and n in str(nome):
            migliore, lung = sid, len(n)
    return migliore


MECCANICA = [
    (r"VMAX", "VMAX"), (r"VSTAR", "VSTAR"), (r"TAG TEAM|GX", "GX"),
    (r"(^|\s)(Mega|M)\s|メガ", "Mega"), (r"(^|\s)EX$|-EX$", "EX"), (r"\bex\b|ex$", "ex"), (r"(\s|^)V$|V$", "V"),
]


def meccanica(nome, suffisso):
    s = str(suffisso) if not mancante(suffisso) else ""
    if s == "TAG TEAM-GX":
        return "GX"
    if s in ("EX", "GX", "V", "ex"):
        base = s
    else:
        base = None
    n = str(nome)
    for regex, valore in MECCANICA:
        if re.search(regex, n):
            if valore in ("Mega", "VMAX", "VSTAR"):
                return valore
            return base or valore
    return base or "nessuna"


# ------------------------------------------------------------------ rilascio

ORDINE_TIMBRI = [
    ("pokemon-center", "Pokemon Center"),
    ("staff", "evento o torneo"), ("regional-championships", "evento o torneo"),
    ("worlds", "evento o torneo"), ("player-rewards", "evento o torneo"),
    ("professor-program", "evento o torneo"), ("gym-challenge", "evento o torneo"),
    ("pre-release", "evento o torneo"), ("prerelease", "evento o torneo"),
    ("ultra-ball-league", "evento o torneo"), ("league", "evento o torneo"),
    ("illustration-contest", "evento o torneo"),
    ("set-logo", "prodotto speciale"), ("25th-celebration", "prodotto speciale"),
    ("30th-anniversary", "prodotto speciale"), ("snowflake", "prodotto speciale"),
    ("trick-or-trade", "prodotto speciale"), ("eb-games", "prodotto speciale"),
    ("gamestop", "prodotto speciale"), ("bulbasaur", "prodotto speciale"),
    ("charmander", "prodotto speciale"), ("squirtle", "prodotto speciale"),
    ("pikachu", "prodotto speciale"),
]


INDIZI_TCGPLAYER = [
    ("Pokemon Center", "Pokemon Center"), ("Pokémon Center", "Pokemon Center"),
    ("In-Store Event", "evento o torneo"), ("Championship", "evento o torneo"), ("Winner", "evento o torneo"),
    ("Staff", "evento o torneo"), ("Prerelease", "evento o torneo"),
    ("Cosmos Holo", "prodotto speciale"), ("Let's Play", "prodotto speciale"),
]


BULBAPEDIA = None


def rilascio_bulbapedia(riga):
    """Categoria dalla lista di Bulbapedia (tutte le promo, qualunque prezzo): None se assente."""
    global BULBAPEDIA
    if BULBAPEDIA is None:
        f = TAB / "rilasci_bulbapedia.csv"
        t = pd.read_csv(f, dtype=str) if f.exists() else pd.DataFrame(columns=["set_id", "num", "rilascio"])
        BULBAPEDIA = dict(zip(zip(t.set_id, t.num), t.rilascio))
    return BULBAPEDIA.get((str(riga.set_id), norm_numero(riga.numero)))


def rilascio(riga):
    if riga.famiglia == "carta da busta":
        return "busta"
    if riga.set_id in ("cel25cc", "30th-c"):
        return "prodotto speciale"
    if "McDonald" in str(riga.set_nome):
        return "altro"
    timbro = riga.variante_timbro
    if mancante(timbro):
        da_bulba = rilascio_bulbapedia(riga)
        if da_bulba and da_bulba != "da classificare":
            return da_bulba
    if not mancante(timbro):
        for chiave, valore in ORDINE_TIMBRI:
            if chiave in str(timbro):
                return valore
        return "altro"
    # indizio dai nomi TCGplayer: vale solo se TUTTI i prodotti con quel numero lo riportano
    # (se lo riporta uno solo, e' una versione diversa della carta, es. timbrata "Prerelease")
    nomi = [n for n in str(riga.nomi_tcgp).split(" | ") if n and n != "nan"] if not mancante(riga.nomi_tcgp) else []
    if nomi:
        for indizio, valore in INDIZI_TCGPLAYER:
            if all(indizio.lower() in n.lower() for n in nomi):
                return valore
    return "da classificare"


# ------------------------------------------------------------------ principale

def costruisci(settimana):
    df = espandi_ambigui(pd.read_parquet(RADICE / "data" / "mercato" / f"{settimana}.parquet"))
    df["fonte_riga"] = "TCGdex"
    data_foto = pd.Timestamp(df.data_fotografia.iloc[0])

    sets = pd.read_csv(TAB / "set.csv")
    df = df.merge(sets[["lingua", "set_id", "era", "tipo_set", "tcgcsv_gruppo_id"]], on=["lingua", "set_id"], how="left")

    # --- collegamento a TCGCSV (set + numero)
    idx = indice_tcgcsv()
    df["num"] = df.numero.map(norm_numero)
    df = df.merge(idx, left_on=["lingua", "tcgcsv_gruppo_id", "num"], right_on=["lingua", "gruppo_id", "num"], how="left")
    df = df.drop(columns=["gruppo_id"])

    # --- catalogo da TCGCSV per le giapponesi assenti su TCGdex
    df = pd.concat([df, catalogo_ja(sets, data_foto)], ignore_index=True)

    # --- rarita'
    rar = pd.read_csv(TAB / "rarita.csv")
    mappa = {(r.fonte, r.lingua, r.rarita_originale): (r.rarita_armonizzata, r.perimetro) for r in rar.itertuples()}
    df["rarita_fonte"] = np.where(df.rarita_tcgdex.map(mancante), "TCGplayer", "TCGdex")
    df["rarita_originale"] = np.where(df.rarita_fonte == "TCGdex", df.rarita_tcgdex, df.rarita_tcgp)
    df.loc[df.rarita_originale.map(mancante), "rarita_fonte"] = "mancante"
    arm = [mappa.get((f, l, r), ("mancante", "da verificare")) if f != "mancante" else ("mancante", "da verificare")
           for f, l, r in zip(df.rarita_fonte, df.lingua, df.rarita_originale)]
    df["rarita_armonizzata"] = [a for a, _ in arm]
    df["perimetro_rarita"] = [p for _, p in arm]

    df["alternate_art"] = (df.lingua == "en") & (df.era == "Spada e Scudo") & df.alt_art.fillna(False).astype(bool) \
        & df.rarita_originale.isin(["Ultra Rare", "Secret Rare"])
    df.loc[df.alternate_art, ["rarita_armonizzata", "perimetro_rarita"]] = ["special illustration rare", "dentro"]
    galleria = df.set_id.astype(str).str.endswith(("tg", "gg"))
    df.loc[galleria, ["rarita_armonizzata", "perimetro_rarita"]] = ["galleria", "dentro"]

    # --- famiglia
    df["stamped"] = ~df.variante_timbro.map(mancante)
    promo = (df.tipo_set == "promo") | df.set_id.isin(["cel25cc", "30th-c"]) \
        | df.set_nome.astype(str).str.contains("McDonald") | (df.rarita_originale == "Promo") \
        | df.stamped | df.set_id.isin(list(GRUPPI_PROMO_JA.values()))
    df["famiglia"] = np.where(promo, "promo e rilascio speciale", "carta da busta")
    df.loc[promo & ~df.rarita_armonizzata.isin(RARITA_ALTE), "rarita_armonizzata"] = "promo"

    # --- perimetro
    oltre = pd.to_numeric(df.num.str.extract(r"(\d+)$")[0], errors="coerce") > df.set_carte_ufficiali
    per = np.where(df.famiglia == "promo e rilascio speciale", "dentro", df.perimetro_rarita)
    per = np.where((per == "da verificare") & (df.rarita_armonizzata == "mancante") & ~oltre, "fuori", per)
    per = np.where(df.categoria != "Pokemon", "fuori", per)
    per = np.where(df.variante_formato == "jumbo", "fuori", per)
    df["perimetro"] = per

    # --- rilascio. Due colonne (decisione del 9/10/2026):
    #   rilascio         solo regole automatiche -> usata dal MODELLO (le classificazioni a mano riguardano
    #                    solo le promo sopra 20 euro: nel modello diventerebbero un indizio di prezzo, vietato)
    #   rilascio_scheda  regole + correzioni a mano -> usata da scheda e scelta dei comparabili
    df["rilascio"] = df.apply(rilascio, axis=1)
    df["rilascio_scheda"] = df.rilascio
    manuali = TAB / "rilasci_manuali.csv"
    if manuali.exists():
        m = pd.read_csv(manuali, dtype=str).fillna("")
        m = m[m.rilascio.str.strip() != ""]
        corr = dict(zip(m.lingua + "|" + m.id, m.rilascio.str.strip()))
        chiavi = df.lingua.astype(str) + "|" + df.id.astype(str)
        # le classificazioni a mano valgono solo dove Bulbapedia non ha la carta
        trovate = chiavi.isin(corr) & (df.famiglia != "carta da busta") & ~df.stamped & (df.rilascio == "da classificare")
        df.loc[trovate, "rilascio_scheda"] = chiavi[trovate].map(corr)
        print(f"Rilasci corretti a mano: {int(trovate.sum())} varianti")

    # --- soggetto
    sp = tabella_specie()
    primo = pd.to_numeric(df.dex_id.astype(str).str.split(",").str[0], errors="coerce")
    senza = primo.isna() & (df.categoria == "Pokemon")
    for i in df.index[senza]:
        lingua_nome = "en" if df.at[i, "fonte_riga"] == "catalogo TCGCSV" else df.at[i, "lingua"]
        primo.at[i] = pokemon_da_nome(df.at[i, "nome"], lingua_nome, sp)
    df["specie_id"] = primo
    df["n_pokemon"] = df.dex_id.astype(str).str.count(",") + 1
    df["pokemon"] = df.specie_id.map(sp.nome_en)
    df["generazione"] = df.specie_id.map(sp.generation_id)
    df["leggendario"] = df.specie_id.map(sp.leggendario)
    icon = pd.read_csv(RADICE / "iconici.csv")
    icon = icon[~icon.pokemon.astype(str).str.upper().str.contains("ESEMPIO")]
    df["iconicita"] = df.pokemon.map(dict(zip(icon.pokemon, icon.livello))).fillna("basso")

    # --- stampa
    df["meccanica"] = [meccanica(n, s) for n, s in zip(df.nome, df.suffisso)]
    # "EX" maiuscolo esiste solo prima del 2017 (e nelle ristampe Classic Collection): da SV in poi e' "ex"
    df.loc[(df.meccanica == "EX") & df.era.isin(["Scarlatto e Violetto", "Mega"]), "meccanica"] = "ex"
    df["variante"] = np.select(
        [df.versione == "foil", df.variante_tipo == "reverse", df.variante_tipo == "holo",
         (df.variante_tipo == "normal") & (df.campo_prezzo == "trend-holo")],
        ["holo", "reverse", "holo", "holo"], default="normale")
    df["finitura_holo"] = df.variante.isin(["holo", "reverse"])

    # --- set, eta', diluizione
    uscita = pd.to_datetime(df.set_data_uscita, errors="coerce")
    df["eta_mesi"] = ((data_foto - uscita).dt.days / 30.44).round(1)
    df["fascia_eta"] = pd.cut(df.eta_mesi, [-1, 3, 6, 12, 24, 48, 1e4],
                              labels=["0-3", "3-6", "6-12", "12-24", "24-48", "48+"]).astype(str)
    base = df[(df.fonte_riga == "TCGdex") & ~df.stamped & (df.variante_n == 0)]
    conta = base.groupby(["lingua", "set_id", "rarita_armonizzata"]).id.nunique()
    df["n_stessa_rarita_set"] = [conta.get((l, s, r), 1) for l, s, r in zip(df.lingua, df.set_id, df.rarita_armonizzata)]
    df["diluizione_log"] = np.log(df.n_stessa_rarita_set.clip(lower=1))
    df["standard"] = df.legale_standard.fillna(False).astype(bool)

    # --- addestramento
    df["in_addestramento"] = (df.perimetro == "dentro") & (df.prezzo_rif_eur >= SOGLIA) & (df.fonte_riga == "TCGdex")

    # --- categorie con poche carte -> "altro" (contate sull'addestramento)
    df.loc[df.illustratore.map(mancante), "illustratore"] = None
    tr = df[df.in_addestramento]
    top = tr.pokemon.value_counts().head(30).index
    df["pokemon_cat"] = np.where(df.pokemon.isin(top), df.pokemon, "altro")
    ill = tr.illustratore.value_counts()
    df["illustratore_cat"] = np.where(df.illustratore.isin(ill[ill >= 30].index), df.illustratore,
                                      np.where(df.illustratore.map(mancante), "sconosciuto", "altro"))

    # espansione (decisione del 9/10/2026): i set con almeno 15 carte nel modello come categorie proprie
    n_set = tr.groupby("set_id").size()
    df["set_cat"] = np.where(df.set_id.isin(n_set[n_set >= 15].index), df.set_id, "altro")

    df["esclusiva"] = esclusiva_linguistica(df, sets)
    return df


def catalogo_ja(sets, data_foto):
    """Carte giapponesi assenti su TCGdex: dai set vuoti e dai set promo SM-P, S-P, s8a-P."""
    pieni = set(sets[sets.carte_su_tcgdex > 0].tcgcsv_gruppo_id.dropna().astype(int))
    vuoti = sets[(sets.lingua == "ja") & (sets.carte_su_tcgdex == 0) & sets.tcgcsv_gruppo_id.notna()]
    vuoti = vuoti[~vuoti.tcgcsv_gruppo_id.astype(int).isin(pieni)]
    t = pd.read_parquet(RIF / "tcgcsv_prodotti_ja.parquet")
    t = t[t.numero.notna() & ~t.nome.str.contains(r"\(", regex=True)]
    righe = []
    for gid, sid in list(zip(vuoti.tcgcsv_gruppo_id.astype(int), vuoti.set_id)) + list(GRUPPI_PROMO_JA.items()):
        info = sets[sets.set_id == sid].iloc[0] if (sets.set_id == sid).any() else None
        for p in t[t.gruppo_id == gid].itertuples():
            tipo = str(p.tipo_carta or "")
            righe.append({
                "data_fotografia": data_foto.date().isoformat(), "fonte_riga": "catalogo TCGCSV",
                "fonte": "TCGCSV", "lingua": "ja", "id": f"tcgcsv-{p.prodotto_id}",
                "numero": p.numero, "num": norm_numero(p.numero), "nome": re.sub(r"\s-\s\S+$", "", str(p.nome)),
                "categoria": "Trainer" if tipo.startswith("Trainer") else ("Energy" if "Energy" in tipo else "Pokemon"),
                "rarita_tcgdex": None, "rarita_tcgp": p.rarita, "nomi_tcgp": p.nome, "alt_art": False,
                "prodotto_tcgp": p.prodotto_id,
                "immagine": f"https://tcgplayer-cdn.tcgplayer.com/product/{p.prodotto_id}_400w.jpg",
                "set_id": sid, "set_nome": p.gruppo_nome,
                "set_data_uscita": info.data_uscita if info is not None else p.gruppo_data,
                "era": info.era if info is not None else "Spada e Scudo" if sid == "S-P" else "Sole e Luna",
                "tipo_set": info.tipo_set if info is not None else "promo",
                "tcgcsv_gruppo_id": gid, "set_carte_ufficiali": info.carte_ufficiali if info is not None else None,
                "variante_n": 0, "variante_tipo": None, "variante_formato": "standard",
                "variante_timbro": None, "campo_prezzo": "nessuno", "prezzo_rif_eur": None,
            })
    return pd.DataFrame(righe)


def esclusiva_linguistica(df, sets):
    """Esiste la stessa illustrazione nell'altra lingua? Chiave: specie + illustratore,
    tra carte di rarita' alta, full art o promo. Proposta da verificare (CLAUDE.md 4.7.5)."""
    alte = df.rarita_armonizzata.isin(RARITA_ALTE | {"promo"}) | df.rarita_originale.isin(
        ["Ultra Rare", "Super Rare", "Secret Rare", "Double rare", "Triple Rare", "Holo Rare V", "Holo Rare VMAX"])
    ill = df.illustratore.astype(str).str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    chiave = df.specie_id.astype("Int64").astype(str) + "|" + ill
    ok = alte & df.specie_id.notna() & ~df.illustratore.map(mancante)
    presenti = {l: set(chiave[ok & (df.lingua == l)]) for l in ("en", "ja")}
    # nomi inglesi nel catalogo TCGCSV giapponese (set vuoti su TCGdex): per i casi incerti
    cat = df[df.fonte_riga == "catalogo TCGCSV"].nome.astype(str).str.lower()
    nomi_catalogo = set(cat.str.replace(r"\s*\(.*\)", "", regex=True))

    out = []
    for i, l, k, valido, era, nome in zip(df.index, df.lingua, chiave, ok, df.era, df.pokemon.astype(str)):
        altra = "ja" if l == "en" else "en"
        if not valido:
            out.append("incerta")
        elif k in presenti[altra]:
            out.append("entrambe")
        elif l == "en" and era == "Spada e Scudo" and any(n.startswith(nome.lower()) for n in nomi_catalogo):
            out.append("incerta")
        else:
            out.append("solo giapponese" if l == "ja" else "solo internazionale")
    return out


# ------------------------------------------------------------------ riepilogo

def tab_md(t):
    col = [str(c) for c in t.columns]
    righe = ["| " + " | ".join(col) + " |", "|" + "---|" * len(col)]
    for v in t.itertuples(index=False):
        righe.append("| " + " | ".join("" if pd.isna(x) else str(x) for x in v) + " |")
    return "\n".join(righe)


VARIABILI = [
    ("pokemon_cat", "1. Pokémon raffigurato (30 più frequenti, altri = altro)"),
    ("iconicita", "2. Livello di iconicità (provvisorio: iconici.csv)"),
    ("generazione", "3. Generazione"),
    ("leggendario", "4. Leggendario o misterioso"),
    ("rarita_armonizzata", "5. Rarità armonizzata"),
    ("alternate_art", "5b. Alternate art (SWSH, equivalente SIR)"),
    ("meccanica", "6. Meccanica"),
    ("variante", "7. Variante"),
    ("era", "8. Era"),
    ("fascia_eta", "9. Età del set (mesi)"),
    ("tipo_set", "10. Tipo di set"),
    ("set_cat", "10b. Espansione (set con almeno 15 carte nel modello, altri = altro)"),
    ("rilascio", "11. Modalità di rilascio"),
    ("n_stessa_rarita_set", "12. Diluizione (carte della stessa rarità nel set; nel modello in logaritmo)"),
    ("stamped", "13. Stamped"),
    ("esclusiva", "14. Esclusiva linguistica"),
    ("illustratore_cat", "15. Illustratore (con almeno 30 carte, altri = altro)"),
    ("standard", "16. Giocabile in Standard"),
    ("famiglia", "17. Famiglia"),
    ("lingua", "18. Lingua"),
]


def riepilogo(df, settimana):
    tr = df[df.in_addestramento]
    out = [f"# Blocco 3 — Caratteristiche delle carte ({settimana}) · PROPOSTA DA APPROVARE\n",
           f"Carte nel modello (perimetro + prezzo ≥ {SOGLIA} €): **{len(tr)}** varianti. "
           f"Catalogo giapponese da TCGCSV (senza prezzo Cardmarket): {int((df.fonte_riga == 'catalogo TCGCSV').sum())} carte.\n"]
    for col, titolo in VARIABILI:
        v = tr[col]
        if col == "n_stessa_rarita_set":
            v = pd.cut(v, [0, 5, 10, 20, 40, 1000], labels=["1–5", "6–10", "11–20", "21–40", "41+"])
        conta = v.astype(str).value_counts().rename_axis("valore").reset_index(name="carte")
        out += [f"## {titolo}\n", tab_md(conta.head(40)), ""]

    inc = df[(df.perimetro == "da verificare") & (df.categoria == "Pokemon")]
    out += ["## Da verificare (fuori dal modello finché non decidi)\n",
            tab_md(inc.groupby(["lingua", "rarita_originale"]).agg(
                varianti=("id", "size"), sopra_20=("prezzo_rif_eur", lambda s: int((s >= 20).sum()))).reset_index()), ""]

    dc = tr[tr.rilascio == "da classificare"]
    out += [f"## Promo con modalità di rilascio da classificare\n",
            f"{len(dc)} varianti nel modello, di cui {int((dc.prezzo_rif_eur >= 20).sum())} sopra 20 € "
            f"(elenco in `riepiloghi/blocco3_rilasci_da_classificare.csv`).\n"]
    dc[dc.prezzo_rif_eur >= 20].sort_values("prezzo_rif_eur", ascending=False)[
        ["lingua", "id", "nome", "set_nome", "prezzo_rif_eur", "nomi_tcgp"]].to_csv(
        RADICE / "riepiloghi" / "blocco3_rilasci_da_classificare.csv", index=False)

    combo = [
        ("Iconicità alta × promo × solo giapponese", (tr.iconicita == "alto") & (tr.famiglia != "carta da busta") & (tr.esclusiva == "solo giapponese")),
        ("Iconicità alta × promo", (tr.iconicita == "alto") & (tr.famiglia != "carta da busta")),
        ("Iconicità alta × carta da busta", (tr.iconicita == "alto") & (tr.famiglia == "carta da busta")),
        ("Pikachu × promo × solo giapponese", (tr.pokemon == "Pikachu") & (tr.famiglia != "carta da busta") & (tr.esclusiva == "solo giapponese")),
        ("Pikachu × promo", (tr.pokemon == "Pikachu") & (tr.famiglia != "carta da busta")),
        ("Iconicità alta × SIR", (tr.iconicita == "alto") & (tr.rarita_armonizzata == "special illustration rare")),
        ("Iconicità alta × stamped", (tr.iconicita == "alto") & tr.stamped),
        ("Iconicità alta × Pokémon Center", (tr.iconicita == "alto") & (tr.rilascio == "Pokemon Center")),
    ]
    out += ["## Combinazioni chiave (CLAUDE.md 5.5): carte nel modello\n",
            tab_md(pd.DataFrame([(n, int(m.sum()), "sì" if m.sum() >= 15 else "no (regolarizzata o solo comparabili)")
                                 for n, m in combo], columns=["combinazione", "carte", "≥ 15 carte"])), ""]

    ctrl = controllo(df)
    out += ["## Carte di controllo: caratteristiche riconosciute\n", tab_md(ctrl), ""]
    testo = "\n".join(out)
    (RADICE / "riepiloghi" / f"blocco3_{settimana}.md").write_text(testo, encoding="utf-8")
    return testo


CONTROLLO_ID = {
    "swshp-SWSH262": "Charizard VSTAR", "S8b-223": "Pikachu VMAX JA", "cel25cc-CC015": "Umbreon ☆",
    "sv08-238": "Pikachu ex SIR", "svp-085": "Pikachu Grey Felt Hat", "sv03.5-168": "Charmander IR",
    "SV-P-062": "Eevee Nagaba JA", "SV2a-168": "Charmander AR JA", "sv03.5-170": "Squirtle IR",
    "sv03.5-199": "Charizard ex SIR", "SV8a-217": "Umbreon ex SAR JA", "swsh10.5-072": "Mewtwo V alt",
    "swsh12.5gg-GG44": "Mewtwo VSTAR GG", "SV8-132": "Pikachu ex SAR JA",
}


def controllo(df):
    c = df[df.id.isin(CONTROLLO_ID) & ~df.stamped & (df.versione.isna() | (df.versione == "normale"))]
    c = c.drop_duplicates("id")
    t = c[["id", "pokemon", "iconicita", "rarita_armonizzata", "alternate_art", "meccanica", "variante",
           "famiglia", "rilascio", "esclusiva", "era", "perimetro", "in_addestramento"]].copy()
    t.insert(0, "carta", t.id.map(CONTROLLO_ID))
    munch = df[(df.set_id == "SM-P") & (df.num == "288")]
    if len(munch):
        m = munch.iloc[0]
        t.loc[len(t)] = ["Pikachu Munch JA (catalogo)", m.id, m.pokemon, m.iconicita, m.rarita_armonizzata, False,
                         m.meccanica, "—", m.famiglia, m.rilascio, m.esclusiva, m.era, m.perimetro, False]
    return t.drop(columns=["id"])


def main():
    settimana = sys.argv[1] if len(sys.argv) > 1 else sorted((RADICE / "data" / "mercato").glob("????-W??.parquet"))[-1].stem
    df = costruisci(settimana)
    dest = RADICE / "data" / "caratteristiche" / f"{settimana}.parquet"
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dest, index=False, compression="zstd")
    print(riepilogo(df, settimana))
    print(f"\nSalvata: {dest.relative_to(RADICE)} ({len(df)} righe, {dest.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
