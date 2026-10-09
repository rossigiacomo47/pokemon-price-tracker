"""Blocco 4 - Modello del prezzo equo (BOZZA da rivedere insieme, CLAUDE.md sezione 6).

Regressione sul logaritmo del prezzo di riferimento Cardmarket, con le variabili della
sezione 5 e le interazioni della 5.5. Confronta con la validazione incrociata (5 gruppi):
  - ridge senza interazioni (due versioni: solo Pokemon / solo iconicita', CLAUDE.md 5.4)
  - ridge con interazioni
  - versione robusta (Huber) con interazioni
  - due modelli separati per famiglia
  - modello flessibile (gradient boosting)
Scrive:
  modelli/AAAA-Wnn.json                pesi, sovrapprezzi con intervallo, errori, scelte
  data/previsioni/AAAA-Wnn.parquet     prezzo stimato (fuori campione) per ogni carta
  riepiloghi/blocco4_AAAA-Wnn.md       riepilogo leggibile

Uso:
    Mac:     .venv/bin/python src/modello.py 2026-W41
    Windows: .venv\\Scripts\\python src\\modello.py 2026-W41
"""

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import HuberRegressor, Ridge
from sklearn.model_selection import KFold

warnings.filterwarnings("ignore")
RADICE = Path(__file__).resolve().parent.parent
SEED = 41
K = 5

# variabile -> categoria di riferimento (CLAUDE.md 6.2: dichiararla sempre)
CATEGORICHE = {
    "pokemon_cat": "altro",
    "iconicita": "basso",
    "rarita_armonizzata": "illustration rare",
    "meccanica": "nessuna",
    "variante": "normale",
    "era": "Scarlatto e Violetto",
    "fascia_eta": "12-24",
    "tipo_set": "principale",
    "set_cat": "altro",
    "rilascio": "busta",
    "esclusiva": "entrambe",
    "illustratore_cat": "altro",
    "lingua": "en",
}
BINARIE = ["gen1", "leggendario", "stamped", "standard", "alternate_art", "promo_fam"]
NUMERICHE = ["diluizione_log"]
INTERAZIONI = [
    ("iconicita", "famiglia", "esclusiva"),  # la combinazione chiave: si tiene comunque se >= 15 carte
    ("famiglia", "rarita_armonizzata"),
    ("famiglia", "iconicita"),
    ("iconicita", "rarita_armonizzata"),
    ("iconicita", "stamped"),
    ("iconicita", "rilascio"),
    ("era", "rarita_armonizzata"),
]
MIN_CARTE_INTERAZIONE = 15


def prepara(df):
    d = df.copy()
    d["gen1"] = (d.generazione == 1).astype(float)
    d["leggendario"] = d.leggendario.fillna(False).astype(float)
    d["stamped"] = d.stamped.astype(float)
    d["standard"] = d.standard.astype(float)
    d["alternate_art"] = d.alternate_art.fillna(False).astype(float)
    d["promo_fam"] = (d.famiglia != "carta da busta").astype(float)
    for c in CATEGORICHE:
        d[c] = d[c].astype(str)
    d["famiglia"] = d.famiglia.astype(str)
    d["diluizione_log"] = d.diluizione_log.fillna(0.0)
    return d


def colonne_design(tr, usa_pokemon=True, usa_iconicita=True, interazioni=True):
    """Elenco delle colonne (nome, funzione) da costruire, deciso sui dati di addestramento."""
    spec = []
    for var, ref in CATEGORICHE.items():
        if var == "pokemon_cat" and not usa_pokemon:
            continue
        if var == "iconicita" and not usa_iconicita:
            continue
        for v in sorted(tr[var].unique()):
            if v != ref:
                spec.append((f"{var}={v}", ("cat", var, v)))
    for b in BINARIE:
        spec.append((b, ("num", b)))
    for n in NUMERICHE:
        spec.append((n, ("num", n)))
    if interazioni:
        for vars_ in INTERAZIONI:
            if "iconicita" in vars_ and not usa_iconicita:
                continue
            gruppi = tr.groupby([tr[v].astype(str) for v in vars_]).size()
            for chiave, n in gruppi.items():
                chiave = chiave if isinstance(chiave, tuple) else (chiave,)
                if n < MIN_CARTE_INTERAZIONE:
                    continue
                # niente interazione se uno dei livelli e' il riferimento della sua variabile
                if any(CATEGORICHE.get(v) == k for v, k in zip(vars_, chiave)):
                    continue
                if any(k in ("False", "0.0", "carta da busta") for k in chiave):
                    continue
                nome = " × ".join(f"{v}={k}" for v, k in zip(vars_, chiave))
                spec.append((nome, ("int", vars_, chiave)))
    return spec


def costruisci_X(d, spec):
    X = np.zeros((len(d), len(spec)))
    for j, (_, s) in enumerate(spec):
        if s[0] == "cat":
            X[:, j] = (d[s[1]].values == s[2])
        elif s[0] == "num":
            X[:, j] = d[s[1]].values.astype(float)
        else:
            m = np.ones(len(d), dtype=bool)
            for v, k in zip(s[1], s[2]):
                m &= d[v].astype(str).values == k
            X[:, j] = m
    return X


def errore_tipico(y, pred):
    """Mediana dell'errore percentuale assoluto: |prezzo stimato / prezzo vero - 1|."""
    return float(np.median(np.abs(np.exp(pred - y) - 1)))


class Lineare:
    def __init__(self, tipo="ridge", alpha=3.0, **opz):
        self.tipo, self.alpha, self.opz = tipo, alpha, opz

    def fit(self, d, y):
        self.spec = colonne_design(d, **self.opz)
        X = costruisci_X(d, self.spec)
        self.media, self.scala = X.mean(0), X.std(0) + 1e-9
        Xs = (X - self.media) / self.scala
        if self.tipo == "huber":
            self.m = HuberRegressor(alpha=self.alpha * 1e-3, epsilon=1.5, max_iter=2000).fit(Xs, y)
        else:
            self.m = Ridge(alpha=self.alpha).fit(Xs, y)
        return self

    def predict(self, d):
        return self.m.predict((costruisci_X(d, self.spec) - self.media) / self.scala)

    def coefficienti(self):
        return dict(zip([n for n, _ in self.spec], self.m.coef_ / self.scala))


class PerFamiglia:
    def __init__(self, **opz):
        self.opz = opz

    def fit(self, d, y):
        self.m = {f: Lineare(**self.opz).fit(d[d.famiglia == f], y[d.famiglia.values == f]) for f in d.famiglia.unique()}
        return self

    def predict(self, d):
        out = np.zeros(len(d))
        for f, m in self.m.items():
            sel = d.famiglia.values == f
            if sel.any():
                out[sel] = m.predict(d[sel])
        return out


class Flessibile:
    def fit(self, d, y):
        self.cols = list(CATEGORICHE) + BINARIE + NUMERICHE + ["famiglia"]
        self.cat = list(CATEGORICHE) + ["famiglia"]
        self.livelli = {c: sorted(d[c].unique()) for c in self.cat}
        self.m = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, max_leaf_nodes=31,
                                               min_samples_leaf=15, l2_regularization=1.0,
                                               categorical_features=[c in self.cat for c in self.cols],
                                               random_state=SEED).fit(self._X(d), y)
        return self

    def _X(self, d):
        X = d[self.cols].copy()
        for c in self.cat:
            X[c] = pd.Categorical(X[c], categories=self.livelli[c]).codes.astype(float)
            X.loc[X[c] < 0, c] = np.nan
        return X.astype(float)

    def predict(self, d):
        return self.m.predict(self._X(d))


def cv(fabbrica, d, y):
    pred = np.zeros(len(d))
    for tr, te in KFold(K, shuffle=True, random_state=SEED).split(d):
        pred[te] = fabbrica().fit(d.iloc[tr], y[tr]).predict(d.iloc[te])
    return pred


def segmenti(d, y, pred):
    err = np.abs(np.exp(pred - y) - 1)
    prezzo = np.exp(y)
    fascia = pd.cut(prezzo, [0, 10, 50, 200, 1e9], labels=["< 10 €", "10–50 €", "50–200 €", "> 200 €"], right=False)
    righe = []
    for nome, chiave in [("famiglia", d.famiglia.values), ("lingua", d.lingua.values), ("fascia di prezzo", fascia),
                         ("famiglia × lingua", d.famiglia.values + " · " + d.lingua.values)]:
        for k in pd.unique(chiave):
            sel = np.asarray(chiave == k)
            righe.append({"gruppo": nome, "segmento": str(k), "carte": int(sel.sum()),
                          "errore_tipico": round(float(np.median(err[sel])) * 100, 1),
                          "entro_15": bool(np.median(err[sel]) <= 0.15)})
    return pd.DataFrame(righe)


def main():
    settimana = sys.argv[1] if len(sys.argv) > 1 else sorted((RADICE / "data" / "caratteristiche").glob("????-W??.parquet"))[-1].stem
    tutte = prepara(pd.read_parquet(RADICE / "data" / "caratteristiche" / f"{settimana}.parquet"))
    d = tutte[tutte.in_addestramento].reset_index(drop=True)
    y = np.log(d.prezzo_rif_eur.values)
    print(f"Carte nel modello: {len(d)}")

    # --- scelta di alpha (forza della regolarizzazione) per il ridge con interazioni
    alpha_err = {}
    for a in (1, 3, 10, 30):
        alpha_err[a] = errore_tipico(y, cv(lambda: Lineare("ridge", a), d, y))
    alpha = min(alpha_err, key=alpha_err.get)
    print("alpha:", alpha_err, "->", alpha)

    candidati = {
        "ridge senza interazioni, Pokémon + iconicità": lambda: Lineare("ridge", alpha, interazioni=False),
        "ridge senza interazioni, solo Pokémon": lambda: Lineare("ridge", alpha, interazioni=False, usa_iconicita=False),
        "ridge senza interazioni, solo iconicità": lambda: Lineare("ridge", alpha, interazioni=False, usa_pokemon=False),
        "ridge con interazioni": lambda: Lineare("ridge", alpha),
        "robusto (Huber) con interazioni": lambda: Lineare("huber", alpha),
        "due modelli per famiglia (ridge con interazioni)": lambda: PerFamiglia(tipo="ridge", alpha=alpha),
        "flessibile (gradient boosting)": Flessibile,
    }
    risultati, previsioni = [], {}
    for nome, fab in candidati.items():
        p = cv(fab, d, y)
        previsioni[nome] = p
        chiave = (d.iconicita == "alto") & (d.famiglia != "carta da busta")
        risultati.append({"modello": nome, "errore_tipico_%": round(errore_tipico(y, p) * 100, 1),
                          "entro_±15%_quota": round(float(np.mean(np.abs(np.exp(p - y) - 1) <= 0.15)) * 100, 1),
                          "errore_combinazioni_chiave_%": round(errore_tipico(y[chiave], p[chiave]) * 100, 1)})
        print(risultati[-1], flush=True)
    risultati = pd.DataFrame(risultati)
    lineari = risultati[~risultati.modello.str.startswith("flessibile")]
    scelto = lineari.sort_values("errore_tipico_%").iloc[0].modello
    pred_cv = previsioni[scelto]

    # --- selezione delle variabili: quanto peggiora l'errore togliendo ciascuna (validazione incrociata)
    importanza = {}
    base_err = errore_tipico(y, previsioni["ridge con interazioni"])
    for var in list(CATEGORICHE) + BINARIE + NUMERICHE:
        d2 = d.copy()
        if var in CATEGORICHE:
            d2[var] = CATEGORICHE[var]
        else:
            d2[var] = 0.0
        importanza[var] = round((errore_tipico(y, cv(lambda: Lineare("ridge", alpha), d2, y)) - base_err) * 100, 2)
    print("importanza:", importanza, flush=True)

    # --- modello finale (lineare scelto, interpretabile) sull'intero pool + intervalli bootstrap
    finale = candidati[scelto]().fit(d, y)
    coef = finale.coefficienti() if hasattr(finale, "coefficienti") else Lineare("ridge", alpha).fit(d, y).coefficienti()
    rng = np.random.default_rng(SEED)
    boot = []
    interpretabile = Lineare("ridge", alpha).fit(d, y)
    nomi = [n for n, _ in interpretabile.spec]
    for _ in range(150):
        idx = rng.integers(0, len(d), len(d))
        m = Lineare("ridge", alpha).fit(d.iloc[idx], y[idx])
        c = m.coefficienti()
        boot.append([c.get(n, 0.0) for n in nomi])
    boot = np.array(boot)
    c0 = interpretabile.coefficienti()
    pesi = pd.DataFrame({
        "caratteristica": nomi,
        "peso_log": [c0[n] for n in nomi],
        "sovrapprezzo_%": [(np.exp(c0[n]) - 1) * 100 for n in nomi],
        "ic_basso_%": (np.exp(np.percentile(boot, 5, axis=0)) - 1) * 100,
        "ic_alto_%": (np.exp(np.percentile(boot, 95, axis=0)) - 1) * 100,
    }).round(1)
    pesi["carte_con_la_caratteristica"] = [int(costruisci_X(d, [s]).sum()) for s in interpretabile.spec]

    # --- intervallo di previsione dai residui fuori campione
    res = y - pred_cv
    q10, q90 = np.percentile(res, [10, 90])
    seg = segmenti(d, y, pred_cv)

    # --- previsioni per tutte le carte del perimetro (anche sotto soglia e catalogo)
    per = tutte[(tutte.perimetro == "dentro") & (tutte.categoria == "Pokemon")].copy()
    per["stima_log"] = finale.predict(per)
    # predittore lineare unico (ridge con interazioni): serve per le rettifiche dei comparabili (CLAUDE.md 7.3)
    per["lineare_log"] = interpretabile.predict(per)
    per["stima_eur"] = np.exp(per.stima_log)
    per["stima_basso_eur"] = np.exp(per.stima_log + q10)
    per["stima_alto_eur"] = np.exp(per.stima_log + q90)
    oof = pd.Series(np.exp(pred_cv), index=d.index)
    mappa_oof = dict(zip(zip(d.id, d.variante_n, d.versione.fillna("")), oof))
    per["stima_fuori_campione_eur"] = [mappa_oof.get((a, b, c if isinstance(c, str) else ""))
                                       for a, b, c in zip(per.id, per.variante_n, per.versione)]
    dest_prev = RADICE / "data" / "previsioni" / f"{settimana}.parquet"
    dest_prev.parent.mkdir(parents=True, exist_ok=True)
    per[["lingua", "id", "variante_n", "versione", "lineare_log", "stima_eur", "stima_basso_eur", "stima_alto_eur",
         "stima_fuori_campione_eur"]].to_parquet(dest_prev, index=False)

    # --- salvataggio pesi
    modello = {
        "settimana": settimana, "stato": "BOZZA - da rivedere insieme (CLAUDE.md 6.7)",
        "carte": len(d), "soglia_bulk_eur": float(d.prezzo_rif_eur.min().round(2)),
        "modello_scelto": scelto, "alpha": alpha, "riferimenti": CATEGORICHE,
        "confronto": risultati.to_dict("records"),
        "intervallo_log": [float(q10), float(q90)],
        "segmenti": seg.to_dict("records"),
        "importanza_variabili_punti_%": importanza,
        "pesi": pesi.to_dict("records"),
        "design": [(n, list(map(str, s))) for n, s in interpretabile.spec],
        "media": interpretabile.media.tolist(), "scala": interpretabile.scala.tolist(),
        "intercetta": float(interpretabile.m.intercept_),
    }
    (RADICE / "modelli").mkdir(exist_ok=True)
    (RADICE / "modelli" / f"{settimana}.json").write_text(json.dumps(modello, ensure_ascii=False, indent=1), encoding="utf-8")

    scrivi_riepilogo(settimana, d, y, pred_cv, risultati, scelto, alpha, pesi, seg, importanza, q10, q90, tutte, finale)


def tab_md(t):
    col = [str(c) for c in t.columns]
    righe = ["| " + " | ".join(col) + " |", "|" + "---|" * len(col)]
    for v in t.itertuples(index=False):
        righe.append("| " + " | ".join("" if pd.isna(x) else str(x) for x in v) + " |")
    return "\n".join(righe)


ATTESE = [  # (caratteristica, direzione attesa, CLAUDE.md 5.6)
    ("iconicita=alto", "+"), ("rarita_armonizzata=special illustration rare", "+"),
    ("rarita_armonizzata=gold-hyper-rainbow", "+"), ("gen1", "+"), ("leggendario", "+"), ("stamped", "+"),
    ("rilascio=Pokemon Center", "+"), ("rilascio=evento o torneo", "+"), ("diluizione_log", "-"), ("standard", "+"),
]


def scrivi_riepilogo(settimana, d, y, pred, risultati, scelto, alpha, pesi, seg, importanza, q10, q90, tutte, finale):
    out = [f"# Blocco 4 — Modello del prezzo equo ({settimana}) · BOZZA DA RIVEDERE INSIEME\n",
           f"Carte nel modello: **{len(d)}** (perimetro, prezzo di riferimento Cardmarket ≥ 3 €). "
           f"Prezzo: `log(trend)`; errore tipico = mediana di |stima / prezzo − 1| su carte **non viste** "
           f"(validazione incrociata a {K} gruppi). Regolarizzazione ridge alpha = {alpha}.\n",
           "## 1. Confronto dei modelli\n", tab_md(risultati), "",
           f"**Modello scelto (lineare con l'errore più basso, spiegabile): {scelto}.** "
           "Il modello flessibile serve da confronto: se sbaglia molto meno, vuol dire che mancano combinazioni.\n",
           f"Intervallo del prezzo equo (10°–90° percentile dell'errore): da {np.exp(q10) * 100 - 100:+.0f}% a {np.exp(q90) * 100 - 100:+.0f}%.\n",
           "## 2. Soglia ±15% per segmento (CLAUDE.md 6)\n", tab_md(seg), "",
           "Nei segmenti oltre il 15% la scheda **non usa il prezzo del modello**: usa solo i comparabili con i prezzi NM.\n",
           "## 3. Cosa vale ogni caratteristica (sovrapprezzo % con intervallo al 90%, bootstrap)\n",
           "Riferimenti: " + ", ".join(f"{k} = {v}" for k, v in CATEGORICHE.items()) + ".\n"]
    p = pesi.copy()
    p["peso_abs"] = p.peso_log.abs()
    principali = p[~p.caratteristica.str.contains("×") & ~p.caratteristica.str.startswith(("pokemon_cat", "illustratore_cat"))]
    out += [tab_md(principali.drop(columns=["peso_abs", "peso_log"])), ""]
    out += ["### Pokémon (rispetto ad \"altro\")\n",
            tab_md(p[p.caratteristica.str.startswith("pokemon_cat")].sort_values("peso_log", ascending=False).drop(columns=["peso_abs", "peso_log"])), ""]
    out += ["### Interazioni (combinazioni) con almeno 15 carte\n",
            tab_md(p[p.caratteristica.str.contains("×")].sort_values("peso_abs", ascending=False).drop(columns=["peso_abs", "peso_log"]).head(40)), ""]
    controlli = []
    for car, atteso in ATTESE:
        r = pesi[pesi.caratteristica == car]
        if len(r):
            v = r.iloc[0]["sovrapprezzo_%"]
            ok = (v > 0) if atteso == "+" else (v < 0)
            controlli.append({"caratteristica": car, "atteso": atteso, "trovato_%": v, "esito": "ok" if ok else "⚠️ CONTRO L'ATTESA: indagare"})
    out += ["## 4. Controllo di buon senso (CLAUDE.md 5.6)\n", tab_md(pd.DataFrame(controlli)), ""]
    out += ["## 5. Importanza delle variabili (punti % di errore in più togliendola)\n",
            tab_md(pd.DataFrame(sorted(importanza.items(), key=lambda x: -x[1]), columns=["variabile", "peggioramento_punti_%"])),
            "", "Valori ≤ 0: la variabile non riduce l'errore (candidata a essere tolta, CLAUDE.md 6.2).\n"]

    ctrl_id = ["swshp-SWSH262", "S8b-223", "cel25cc-CC015", "sv08-238", "svp-085", "sv03.5-168", "SV2a-168",
               "sv03.5-170", "sv03.5-199", "SV8a-217", "swsh10.5-072", "swsh12.5gg-GG44", "SV8-132"]
    cc = pd.read_csv(RADICE / "carte_controllo.csv")
    nm = dict(zip(["swshp-SWSH262", "S8b-223", "cel25cc-CC015", "sv08-238", "svp-085", "sv03.5-168", "SV-P-062", "SV2a-168",
                   "sv03.5-170", "sv03.5-199", "SV8a-217", "swsh10.5-072", "swsh12.5gg-GG44", "SV8-132"],
                  cc.nm_offerta_min_eur.astype(float)))
    righe = []
    for cid in ctrl_id:
        r = d[(d.id == cid) & (d.stamped == 0)]
        if not len(r):
            continue
        i = r.index[0]
        stima = float(np.exp(pred[i]))
        centro = nm[cid] * 1.025
        righe.append({"carta": f"{r.nome.iloc[0]} ({cid})", "trend": round(float(r.prezzo_rif_eur.iloc[0]), 2),
                      "stima_modello_fuori_campione": round(stima, 2),
                      "scarto_vs_trend_%": round((stima / r.prezzo_rif_eur.iloc[0] - 1) * 100),
                      "centro_fascia_NM": round(centro, 2), "scarto_vs_NM_%": round((stima / centro - 1) * 100)})
    out += ["## 6. Carte di controllo (stima senza aver visto la carta, nessuna calibrazione)\n", tab_md(pd.DataFrame(righe)), ""]
    (RADICE / "riepiloghi" / f"blocco4_{settimana}.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
