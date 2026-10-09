"""Iconicita' stimata dai dati (CLAUDE.md 5.4, punti 1-3).

Stima il sovrapprezzo di ogni Pokemon a parita' delle altre caratteristiche (ridge: i Pokemon con
poche carte vengono "frenati" verso zero), poi propone tre livelli e li confronta con iconici.csv.
Scrive riepiloghi/iconicita_proposta.csv (non modifica iconici.csv: decide Giacomo).

Livelli proposti (sovrapprezzo rispetto al Pokemon medio):
    alto  >= +200%   (vale almeno il triplo: comprende tutti i Pokemon "alto" della lista di Giacomo)
    medio da +75% a +200%
    basso  < +75%
Servono almeno 8 carte per proporre "alto" o "medio".

Uso:
    Mac:     .venv/bin/python src/iconicita_dati.py 2026-W41
    Windows: .venv\\Scripts\\python src\\iconicita_dati.py 2026-W41
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from modello import Lineare, prepara

RADICE = Path(__file__).resolve().parent.parent
MIN_CARTE = 3
MIN_CARTE_LIVELLO = 8


def main():
    settimana = sys.argv[1] if len(sys.argv) > 1 else "2026-W41"
    d = prepara(pd.read_parquet(RADICE / "data" / "caratteristiche" / f"{settimana}.parquet"))
    d = d[d.in_addestramento].reset_index(drop=True)
    conta = d.pokemon.value_counts()
    # per questa stima ogni Pokemon con almeno 3 carte ha la sua categoria (non solo i 30 piu' frequenti)
    d["pokemon_cat"] = np.where(d.pokemon.isin(conta[conta >= MIN_CARTE].index), d.pokemon, "altro").astype(str)
    y = np.log(d.prezzo_rif_eur.values)
    m = Lineare("ridge", 10, interazioni=False).fit(d, y)
    coef = {n.split("=", 1)[1]: v for n, v in m.coefficienti().items() if n.startswith("pokemon_cat=")}
    tab = pd.DataFrame({"pokemon": list(coef), "peso_log": list(coef.values())})
    tab["peso_log"] -= tab.peso_log.median()           # rispetto al Pokemon "medio", non ad "altro"
    tab["sovrapprezzo_%"] = ((np.exp(tab.peso_log) - 1) * 100).round(0)
    tab["carte"] = tab.pokemon.map(conta)
    tab["livello_dati"] = np.select(
        [(tab["sovrapprezzo_%"] >= 200) & (tab.carte >= MIN_CARTE_LIVELLO),
         (tab["sovrapprezzo_%"] >= 75) & (tab.carte >= MIN_CARTE_LIVELLO)],
        ["alto", "medio"], default="basso")
    lista = pd.read_csv(RADICE / "iconici.csv")
    tab["livello_tua_lista"] = tab.pokemon.map(dict(zip(lista.pokemon, lista.livello))).fillna("basso (non in lista)")
    tab["diverso"] = tab.livello_dati != tab.livello_tua_lista.str.split(" ").str[0]
    tab = tab.sort_values("sovrapprezzo_%", ascending=False)
    tab.drop(columns=["peso_log"]).to_csv(RADICE / "riepiloghi" / "iconicita_proposta.csv", index=False)
    print(tab.drop(columns=["peso_log"]).head(40).to_string(index=False))
    print("\nNella tua lista ma non 'alto' nei dati:")
    print(tab[tab.livello_tua_lista.isin(["alto", "medio"]) & tab.diverso].drop(columns=["peso_log"]).to_string(index=False))


if __name__ == "__main__":
    main()
