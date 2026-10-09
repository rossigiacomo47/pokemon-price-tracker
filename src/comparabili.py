"""Blocco 5 - Comparabili rettificati e dati della dashboard (BOZZA, CLAUDE.md sezione 7).

Per ogni carta del perimetro:
  1. filtri obbligatori (7.2): stessa famiglia; carte da busta = stessa rarita' armonizzata e
     stesso livello di iconicita'; promo = stessa modalita' di rilascio e stessa iconicita';
  2. somiglianza 0-100% (distanza di Gower) sulle altre variabili, pesate con l'importanza
     stimata dal modello (era ed eta' con peso basso);
  3. se meno di 3 comparabili sopra il 70%: si allenta SOLO l'iconicita' e lo si scrive;
  4. rettifica = exp(predittore lineare della carta - predittore del comparabile), cioe'
     i pesi del modello con le interazioni (7.3).
Scrive in docs/data/ i file letti dalla dashboard:
  indice.json   ricerca (tutte le carte Pokemon, anche fuori perimetro)
  schede.json   scheda di ogni carta del perimetro con i suoi comparabili
  modello.json  riepilogo per la pagina "Il modello"

Uso:
    Mac:     .venv/bin/python src/comparabili.py 2026-W41
    Windows: .venv\\Scripts\\python src\\comparabili.py 2026-W41
"""

import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus

import numpy as np
import pandas as pd

from riepilogo import CONTROLLO_ID

RADICE = Path(__file__).resolve().parent.parent
DOCS = RADICE / "docs" / "data"
N_COMP = 8
SOGLIA_SIM = 70

# variabile -> (nome dell'importanza nel modello, tipo)
SOMIGLIANZA = {
    "pokemon": ("pokemon_cat", "cat"),
    "rarita_armonizzata": ("rarita_armonizzata", "cat"),
    "meccanica": ("meccanica", "cat"),
    "generazione": ("gen1", "cat"),
    "leggendario": ("leggendario", "cat"),
    "illustratore": ("illustratore_cat", "cat"),
    "lingua": ("lingua", "cat"),
    "iconicita": ("iconicita", "cat"),
    "finitura_holo": (None, "cat"),
    "rilascio_scheda": ("rilascio", "cat"),
    "tipo_set": ("tipo_set", "cat"),
    "set_id": ("set_cat", "cat"),
    "stamped": ("stamped", "cat"),
    "esclusiva": ("esclusiva", "cat"),
    "standard": ("standard", "cat"),
    "alternate_art": ("alternate_art", "cat"),
    "era": ("era", "cat"),
    "eta_mesi": ("fascia_eta", "num"),
    "diluizione_log": ("diluizione_log", "num"),
}
PESO_MINIMO = 0.2
PESO_BASSO = {"era": 0.3, "eta_mesi": 0.3}   # CLAUDE.md 7.2: era ed eta' con peso basso
PESO_FINITURA = 1.5                           # decisione del 9/10: holo conta nella somiglianza

ETICHETTE = {
    "pokemon": lambda v: f"{v}", "rarita_armonizzata": lambda v: f"{v}", "meccanica": lambda v: f"meccanica {v}",
    "generazione": lambda v: f"{int(v)}ª generazione" if not pd.isna(v) else "generazione ?",
    "leggendario": lambda v: "leggendario" if v else "non leggendario",
    "illustratore": lambda v: f"illustratore {v}", "lingua": lambda v: "giapponese" if v == "ja" else "internazionale",
    "iconicita": lambda v: "iconicità " + {"alto": "alta", "medio": "media", "basso": "bassa"}.get(v, str(v)), "finitura_holo": lambda v: "holo" if v else "non holo",
    "rilascio_scheda": lambda v: f"rilascio {v}", "tipo_set": lambda v: f"set {v}", "stamped": lambda v: "stamped" if v else "non stamped",
    "esclusiva": lambda v: {"entrambe": "presente in inglese e giapponese", "solo giapponese": "solo in giapponese",
                            "solo internazionale": "solo in inglese", "incerta": "esclusiva da verificare"}.get(v, str(v)),
    "set_id": lambda v: f"set {v}", "standard": lambda v: "in Standard" if v else "fuori Standard",
    "alternate_art": lambda v: "alternate art" if v else "non alternate art", "era": lambda v: f"era {v}",
}
LINGUA_CM = {"en": 1, "ja": 7}


N_GRUPPI = 128


def gruppo(k):
    """Stesso calcolo in docs/index.html (funzione gruppo): sceglie il file della scheda."""
    h = 0
    for ch in k:
        h = (h * 31 + ord(ch)) % 4294967296
    return h % N_GRUPPI


def chiave(r):
    v = r.versione if isinstance(r.versione, str) else ""
    return f"{r.lingua}|{r.id}|{int(r.variante_n)}|{v}"


def nome_inglese(r):
    """Nome in inglese per i link (le carte giapponesi su Cardmarket hanno il nome inglese)."""
    if r.lingua == "en":
        return str(r.nome)
    n = str(r.nomi_tcgp).split(" | ")[0] if isinstance(r.nomi_tcgp, str) else ""
    n = re.sub(r"\s-\s\S+$", "", n)
    n = re.sub(r"\s*\(.*?\)", "", n)
    return n or (str(r.pokemon) if isinstance(r.pokemon, str) else str(r.nome))


def link(r, nome_en):
    num = str(r.numero) if not pd.isna(r.numero) else ""
    q_cm = quote_plus(nome_en)
    cm = (f"https://www.cardmarket.com/it/Pokemon/Products/Search?searchString={q_cm}"
          f"&language={LINGUA_CM.get(r.lingua, 1)}&minCondition=2")
    extra = " japanese" if r.lingua == "ja" else ""
    eb = f"https://www.ebay.it/sch/i.html?_nkw={quote_plus(f'{nome_en} {num}{extra}'.strip())}&LH_Sold=1&LH_Complete=1"
    psa = f"https://www.psacard.com/pop/search?q={quote_plus(nome_en)}"
    return cm, eb, psa


def immagine(r):
    img = r.immagine if isinstance(r.immagine, str) else ""
    if img.startswith("https://assets.tcgdex.net"):
        return img + "/low.webp", img + "/high.webp"
    return img, img


def pulisci(o):
    """NaN e valori mancanti -> null: il JSON non accetta NaN (la pagina non leggerebbe il file)."""
    if isinstance(o, dict):
        return {k: pulisci(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [pulisci(v) for v in o]
    if isinstance(o, float) and math.isnan(o):
        return None
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def scrivi_json(percorso, dati):
    percorso.write_text(json.dumps(pulisci(dati), ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")


def pesi_somiglianza(imp):
    w = {}
    for var, (nome_imp, _) in SOMIGLIANZA.items():
        if var in PESO_BASSO:
            w[var] = PESO_BASSO[var]
        elif var == "finitura_holo":
            w[var] = PESO_FINITURA
        else:
            w[var] = max(PESO_MINIMO, float(imp.get(nome_imp, 0.0)))
    return w


def main():
    settimana = sys.argv[1] if len(sys.argv) > 1 else sorted((RADICE / "data" / "caratteristiche").glob("????-W??.parquet"))[-1].stem
    df = pd.read_parquet(RADICE / "data" / "caratteristiche" / f"{settimana}.parquet")
    prev = pd.read_parquet(RADICE / "data" / "previsioni" / f"{settimana}.parquet")
    mod = json.loads((RADICE / "modelli" / f"{settimana}.json").read_text(encoding="utf-8"))
    df["versione"] = df.versione.where(df.versione.notna(), None)
    prev["versione"] = prev.versione.where(prev.versione.notna(), None)
    df["k"] = [chiave(r) for r in df.itertuples()]
    prev["k"] = [chiave(r) for r in prev.itertuples()]
    df = df.merge(prev.drop(columns=["lingua", "id", "variante_n", "versione"]), on="k", how="left")

    pokemon_cat = df[df.categoria == "Pokemon"].copy()
    per = pokemon_cat[pokemon_cat.perimetro == "dentro"].copy()
    # una sola riga per carta+versione come comparabile: niente varianti doppie della stessa carta
    per = per[(per.variante_n == 0) | per.stamped | per.versione.notna()].reset_index(drop=True)
    print("carte del perimetro (schede):", len(per))

    # --- spread tra lingue (decisione del 9/10/2026): coppie stessa specie + illustratore + rarita'
    ill = per.illustratore.astype(str).str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    per["chiave_gemella"] = per.specie_id.astype("Int64").astype(str) + "|" + ill + "|" + per.rarita_armonizzata.astype(str)
    validi = per[per.prezzo_rif_eur.notna() & ~per.stamped & per.illustratore.notna() & per.specie_id.notna() & per.versione.isna()]
    g = validi.groupby(["chiave_gemella", "lingua"]).prezzo_rif_eur.median().unstack().dropna()
    g["rap"] = g.ja / g.en
    g["rar"] = g.index.str.split("|").str[2]
    spread = {"tutte": float(g.rap.median()), "coppie": int(len(g))}
    for rar_, sotto in g.groupby("rar"):
        if len(sotto) >= 8:
            spread[rar_] = float(sotto.rap.median())
    print("spread giapponese/inglese:", {k: round(v, 2) for k, v in spread.items()})
    b_ja = next((p["peso_log"] for p in mod["pesi"] if p["caratteristica"] == "lingua=ja"), 0.0)
    gemelle = {}
    for r in validi.itertuples():
        gemelle.setdefault(r.chiave_gemella, {}).setdefault(r.lingua, []).append(r)

    w = pesi_somiglianza(mod["importanza_variabili_punti_%"])
    wtot = sum(w.values())
    vals = {v: per[v].astype(str).values for v, (_, t) in SOMIGLIANZA.items() if t == "cat"}
    nums = {v: per[v].astype(float).fillna(per[v].astype(float).median()).values for v, (_, t) in SOMIGLIANZA.items() if t == "num"}
    rng = {v: (np.nanmax(a) - np.nanmin(a)) or 1.0 for v, a in nums.items()}
    fam, rar, ico, ril, lng = (per[c].astype(str).values for c in ("famiglia", "rarita_armonizzata", "iconicita", "rilascio_scheda", "lingua"))
    lin = per.lineare_log.values
    ids = per.id.values

    schede = {}
    for i in range(len(per)):
        base_mask = fam == fam[i]
        filtro_tutte = base_mask & ((rar == rar[i]) if fam[i] == "carta da busta" else (ril == ril[i]))
        filtro = filtro_tutte & (lng == lng[i])          # stessa lingua: obbligatoria
        allentato = False
        altra_lingua = False
        cand = filtro & (ico == ico[i]) & (ids != ids[i])
        sim = np.zeros(len(per))
        for v in vals:
            sim += w[v] * (vals[v] == vals[v][i])
        for v in nums:
            sim += w[v] * (1 - np.abs(nums[v] - nums[v][i]) / rng[v])
        sim = sim / wtot * 100
        if (sim[cand] >= SOGLIA_SIM).sum() < 3:
            cand = filtro & (ids != ids[i])
            allentato = True
        if cand.sum() < 3:
            # pochi comparabili nella stessa lingua: anche l'altra lingua, convertita con lo spread misurato
            cand = filtro_tutte & (ids != ids[i])
            altra_lingua = True
        idx = np.where(cand)[0]
        idx = idx[np.argsort(-sim[idx])]
        scelti, visti = [], set()
        for j in idx:
            if ids[j] in visti:
                continue
            visti.add(ids[j])
            scelti.append(j)
            if len(scelti) == N_COMP:
                break
        comps = []
        for j in scelti:
            uguali, diverse = [], []
            for v in ("pokemon", "set_id", "rarita_armonizzata", "rilascio_scheda", "iconicita", "lingua", "esclusiva", "finitura_holo",
                      "stamped", "meccanica", "alternate_art", "era"):
                a, b = per.at[i, v], per.at[j, v]
                if pd.isna(a) and pd.isna(b):
                    continue
                (uguali if str(a) == str(b) else diverse).append(ETICHETTE[v](per.at[j, v]))
            fattore = float(np.exp(lin[i] - lin[j])) if not (np.isnan(lin[i]) or np.isnan(lin[j])) else None
            convertita = lng[j] != lng[i]
            if fattore and convertita:
                # il modello converte la lingua con un coefficiente medio: lo sostituisco con lo spread misurato
                s_rar = spread.get(rar[i], spread["tutte"])
                fattore = fattore * (np.exp(b_ja) / s_rar if lng[i] == "en" else s_rar / np.exp(b_ja))
            comps.append({"k": per.at[j, "k"], "sim": int(round(sim[j])),
                          "fattore": round(fattore, 3) if fattore else None, "convertita": bool(convertita),
                          "uguali": uguali[:5], "diverse": diverse[:4]})
        gem = None
        altra = "ja" if lng[i] == "en" else "en"
        cand_g = gemelle.get(per.at[i, "chiave_gemella"], {}).get(altra, [])
        if cand_g and not per.at[i, "stamped"]:
            gr = cand_g[0]
            gem = {"nome": str(gr.nome), "set": str(gr.set_nome), "numero": str(gr.numero), "lingua": altra,
                   "trend": round(float(gr.prezzo_rif_eur), 2), "k": gr.k,
                   "spread_tipico": round(spread.get(rar[i], spread["tutte"]), 3)}
        schede[per.at[i, "k"]] = {"comps": comps, "allentato": allentato, "altra_lingua": altra_lingua, "gemella": gem}

    # --- dati di ogni carta
    def info(r):
        nome_en = nome_inglese(r)
        cm, eb, psa = link(r, nome_en)
        lo, hi = immagine(r)
        anno = str(r.set_data_uscita)[:4] if isinstance(r.set_data_uscita, str) else ""
        return {
            "nome": str(r.nome), "nome_en": nome_en, "set": str(r.set_nome), "numero": str(r.numero), "lingua": r.lingua,
            "anno": anno, "img": lo, "fonte": r.fonte_riga, "k": r.k,
            "perimetro": r.perimetro, "famiglia": r.famiglia, "rarita": r.rarita_armonizzata,
            "pokemon": None if pd.isna(r.pokemon) else r.pokemon, "iconicita": r.iconicita,
            "rilascio": r.rilascio_scheda, "esclusiva": r.esclusiva, "meccanica": r.meccanica, "variante": r.variante,
            "stamped": bool(r.stamped), "timbro": None if pd.isna(r.variante_timbro) else str(r.variante_timbro),
            "alternate_art": bool(r.alternate_art) if not pd.isna(r.alternate_art) else False,
            "era": r.era, "generazione": None if pd.isna(r.generazione) else int(r.generazione),
            "versione": r.versione,
            "trend": None if pd.isna(r.prezzo_rif_eur) else round(float(r.prezzo_rif_eur), 2),
            "cm_id": None if pd.isna(r.cm_id_prodotto) else int(r.cm_id_prodotto),
            "avg7": None if pd.isna(r.avg7_rif_eur) else round(float(r.avg7_rif_eur), 2),
            "avg30": None if pd.isna(r.avg30_rif_eur) else round(float(r.avg30_rif_eur), 2),
            "low": None if pd.isna(r.low_rif_eur) else round(float(r.low_rif_eur), 2),
            "campo_prezzo": r.campo_prezzo,
            "nel_modello": bool(r.in_addestramento),
            "stima": None if pd.isna(r.stima_eur) else round(float(r.stima_eur), 2),
            "stima_basso": None if pd.isna(r.stima_basso_eur) else round(float(r.stima_basso_eur), 2),
            "stima_alto": None if pd.isna(r.stima_alto_eur) else round(float(r.stima_alto_eur), 2),
        }

    carte = {r.k: info(r) for r in per.itertuples()}

    # --- minimi NM delle carte di controllo -> rapporto NM/trend (CLAUDE.md, riquadro sezione 6)
    cfg = json.loads((RADICE / "config.json").read_text(encoding="utf-8"))
    da, a = cfg["fascia_nm_da_pct"] / 100, cfg["fascia_nm_a_pct"] / 100
    cc = pd.read_csv(RADICE / "carte_controllo.csv")
    rapporti = []
    for r in cc.itertuples():
        lid = CONTROLLO_ID.get((r.nome, r.set))
        if not lid:
            continue
        k = f"{lid[0]}|{lid[1]}|0|"
        if k in carte and carte[k]["trend"]:
            carte[k]["nm_salvato"] = {"min": float(r.nm_offerta_min_eur), "trend": carte[k]["trend"],
                                      "data": str(r.data), "fonte": "carte di controllo"}
            rapporti.append(float(r.nm_offerta_min_eur) * (1 + (da + a) / 2) / carte[k]["trend"])
    rapporto = {"tipico": float(np.median(rapporti)), "p10": float(np.percentile(rapporti, 10)),
                "p90": float(np.percentile(rapporti, 90)), "n": len(rapporti),
                "errore_tipico": float(np.median(np.abs(np.array(rapporti) / np.median(rapporti) - 1))),
                "fonte": "carte di controllo (centro della fascia NM / trend)"}
    print("rapporto NM/trend:", {k: round(v, 3) if isinstance(v, float) else v for k, v in rapporto.items()})
    for k, s in schede.items():
        carte[k].update(s)
    # --- scarto reale tra le carte e le loro simili (fascia "in linea", CLAUDE.md riquadro sezione 6)
    scarti = []
    for k, c in carte.items():
        if not c["nel_modello"] or not c["trend"]:
            continue
        vals = [carte[x["k"]]["trend"] * x["fattore"] for x in c["comps"] if carte[x["k"]]["trend"] and x["fattore"]]
        if len(vals) >= 3:
            scarti.append(math.log(c["trend"] / float(np.median(vals))))
    q = np.percentile(scarti, [10, 25, 50, 75, 90])
    gap_relativo = dict(zip(["q10", "q25", "q50", "q75", "q90"], [float(x) for x in q]))
    gap_relativo["n"] = len(scarti)
    print("scarto carta / simili (log):", {k: round(v, 3) for k, v in gap_relativo.items()})

    # ogni comparabile porta con se' i dati essenziali: una scheda si legge da un solo file
    for k, c in carte.items():
        for comp in c["comps"]:
            o = carte[comp["k"]]
            comp["c"] = {x: o[x] for x in ("nome", "nome_en", "set", "numero", "lingua", "anno", "img", "trend")}

    # --- indice di ricerca: tutte le carte Pokemon (fuori perimetro comprese), una riga per carta+versione
    idx = pokemon_cat[(pokemon_cat.variante_n == 0) | pokemon_cat.stamped | pokemon_cat.versione.notna()]
    indice = []
    for r in idx.itertuples():
        nome_en = nome_inglese(r)
        lo, _ = immagine(r)
        extra = []
        if r.stamped:
            extra.append(f"timbro {r.variante_timbro}")
        if isinstance(r.versione, str):
            extra.append(f"versione {r.versione}")
        indice.append([r.k, str(r.nome), nome_en if nome_en != str(r.nome) else "", str(r.set_nome), str(r.numero),
                       r.lingua, lo, r.perimetro if r.k in carte else ("fuori" if r.perimetro != "dentro" else "dentro"),
                       ", ".join(extra), None if pd.isna(r.prezzo_rif_eur) else round(float(r.prezzo_rif_eur), 2)])

    # --- pagina "Il modello"
    cc = pd.read_csv(RADICE / "carte_controllo.csv")
    modello = {
        "settimana": settimana, "stato": mod["stato"], "carte": mod["carte"], "scelto": mod["modello_scelto"],
        "confronto": mod["confronto"], "segmenti": mod["segmenti"],
        "pesi": [p for p in mod["pesi"] if "×" not in p["caratteristica"] and not p["caratteristica"].startswith(("pokemon_cat", "illustratore_cat"))],
        "pesi_interazioni": sorted([p for p in mod["pesi"] if "×" in p["caratteristica"]], key=lambda p: -abs(p["peso_log"]))[:12],
        "pesi_pokemon": sorted([p for p in mod["pesi"] if p["caratteristica"].startswith("pokemon_cat")], key=lambda p: -p["peso_log"]),
        "riferimenti": mod["riferimenti"], "intervallo_log": mod["intervallo_log"],
        "controllo": cc[["nome", "set", "lingua", "nm_offerta_min_eur"]].to_dict("records"),
        "fascia_nm": [0, 5],
        "rapporto_nm": rapporto,
        "spread_lingue": spread,
        "gap_relativo": gap_relativo,
    }
    test = RADICE / "docs" / "data" / "test30.json"
    if test.exists():
        modello["test30"] = json.loads(test.read_text(encoding="utf-8"))

    DOCS.mkdir(parents=True, exist_ok=True)
    cartella = DOCS / "schede"
    cartella.mkdir(exist_ok=True)
    for f in cartella.glob("*.json"):
        f.unlink()
    gruppi = {}
    for k, c in carte.items():
        gruppi.setdefault(gruppo(k), {})[k] = c
    for g, dati in gruppi.items():
        scrivi_json(cartella / f"{g:03d}.json", dati)
    dim = sum(f.stat().st_size for f in cartella.glob("*.json")) / 1e6
    print(f"schede/: {len(gruppi)} file, {dim:.1f} MB in tutto, {dim / len(gruppi) * 1000:.0f} KB in media")
    for nome, dati in (("indice.json", indice), ("modello.json", modello)):
        scrivi_json(DOCS / nome, dati)
        print(nome, f"{(DOCS / nome).stat().st_size / 1e6:.2f} MB")
    allentati = sum(1 for s in schede.values() if s["allentato"])
    pochi = sum(1 for s in schede.values() if len(s["comps"]) < 3)
    print(f"schede: {len(schede)} | iconicità allentata: {allentati} | meno di 3 comparabili: {pochi}")


if __name__ == "__main__":
    main()
