"""Test sul mini-storico a 30 giorni (CLAUDE.md 8.3) - le carte "sottovalutate rispetto alle
simili" un mese fa sono poi salite piu' delle altre?

Prezzo "un mese fa" = media a 30 giorni (avg30) di Cardmarket; prezzo "oggi" = trend.
Due misure di sottovalutazione, calcolate solo con i prezzi di un mese fa:
  A. carte simili: prezzo della carta / mediana delle carte simili rettificate (comparabili)
  B. modello: prezzo della carta / stima del modello per le sue caratteristiche (fuori campione)
LIMITI DICHIARATI: avg30 e' una media, non un prezzo puntuale; copre un solo mese; il rumore
della media a 30 giorni puo' creare un "ritorno verso la media" che gonfia il risultato.

Uso:
    Mac:     .venv/bin/python src/test_30giorni.py 2026-W41
    Windows: .venv\\Scripts\\python src\\test_30giorni.py 2026-W41
"""

import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from modello import PerFamiglia, cv, prepara

RADICE = Path(__file__).resolve().parent.parent


def chiave(r):
    v = r.versione if isinstance(r.versione, str) else ""
    return f"{r.lingua}|{r.id}|{int(r.variante_n)}|{v}"


def gruppi(gap, crescita, nome):
    q = pd.qcut(gap, 5, labels=["1 · più sottovalutate", "2", "3", "4", "5 · più sopravvalutate"])
    t = pd.DataFrame({"gruppo": q, "crescita": crescita}).groupby("gruppo", observed=True).agg(
        carte=("crescita", "size"),
        crescita_media_pct=("crescita", lambda x: round((np.exp(x.mean()) - 1) * 100, 1)),
        crescita_mediana_pct=("crescita", lambda x: round((np.exp(x.median()) - 1) * 100, 1)),
        quota_salite_pct=("crescita", lambda x: round((x > 0).mean() * 100, 1)),
    ).reset_index()
    rho, p = spearmanr(gap, crescita)
    return t, rho, p


def tab_md(t):
    col = [str(c) for c in t.columns]
    righe = ["| " + " | ".join(col) + " |", "|" + "---|" * len(col)]
    for v in t.itertuples(index=False):
        righe.append("| " + " | ".join(str(x) for x in v) + " |")
    return "\n".join(righe)


def main():
    settimana = sys.argv[1] if len(sys.argv) > 1 else "2026-W41"
    df = prepara(pd.read_parquet(RADICE / "data" / "caratteristiche" / f"{settimana}.parquet"))
    df["k"] = [chiave(r) for r in df.itertuples()]
    d = df[df.in_addestramento & df.avg30_rif_eur.notna() & (df.avg30_rif_eur > 0)].reset_index(drop=True)
    avg30 = dict(zip(d.k, d.avg30_rif_eur))

    # A. carte simili (comparabili gia' scelti dalla dashboard, rettifiche del modello)
    carte = {}
    for f in glob.glob(str(RADICE / "docs" / "data" / "schede" / "*.json")):
        carte.update(json.loads(Path(f).read_text(encoding="utf-8")))
    gapA = []
    for r in d.itertuples():
        c = carte.get(r.k)
        vals = [avg30[x["k"]] * x["fattore"] for x in (c or {}).get("comps", []) if x["k"] in avg30 and x.get("fattore")]
        gapA.append(np.log(r.avg30_rif_eur / np.median(vals)) if len(vals) >= 3 else np.nan)
    d["gap_simili"] = gapA

    # B. modello addestrato sui prezzi di un mese fa, stima fuori campione
    y30 = np.log(d.avg30_rif_eur.values)
    d["gap_modello"] = y30 - cv(lambda: PerFamiglia(tipo="ridge", alpha=10), d, y30)

    d["crescita"] = np.log(d.prezzo_rif_eur / d.avg30_rif_eur)
    out = [f"# Test sul mini-storico a 30 giorni ({settimana}) · CLAUDE.md 8.3\n",
           "**Domanda:** le carte che un mese fa costavano meno delle loro simili sono poi salite più delle altre?\n",
           "Prezzo di un mese fa = media a 30 giorni Cardmarket; oggi = trend. "
           f"Carte: {len(d)}. Crescita media di tutto il pool: {(np.exp(d.crescita.mean()) - 1) * 100:+.1f}%.\n",
           "**Limiti:** `avg30` è una media, non un prezzo puntuale; un solo mese; il rumore della media può creare "
           "un falso \"ritorno verso la media\". È un test grezzo, il primo basato sui dati.\n"]
    for col, titolo in (("gap_simili", "A. Rispetto alle carte simili (comparabili rettificati)"),
                        ("gap_modello", "B. Rispetto al modello (valore delle caratteristiche)")):
        s = d[d[col].notna()]
        t, rho, p = gruppi(s[col], s.crescita, titolo)
        out += [f"## {titolo}\n", tab_md(t), "",
                f"Correlazione di Spearman tra sottovalutazione e crescita: {rho:+.3f} (p = {p:.3g}). "
                "Negativa = le carte più sottovalutate sono salite di più.\n"]
    testo = "\n".join(out)
    (RADICE / "riepiloghi" / f"test_30giorni_{settimana}.md").write_text(testo, encoding="utf-8")
    print(testo)


if __name__ == "__main__":
    main()
