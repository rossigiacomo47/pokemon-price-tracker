"""Regole sui prezzi di riferimento, applicate quando si legge una fotografia.

La fotografia salvata resta com'e' (CLAUDE.md sezione 14): queste funzioni
producono una tabella derivata, uguale per tutte le settimane.
"""

import pandas as pd

CAMPI = ("trend", "avg7", "avg30", "low")


def espandi_ambigui(df):
    """Decisione D4 (8/10/2026): una variante con `trend` e `trend-holo` entrambi pieni
    esiste in due versioni su Cardmarket. Diventa due righe:
    "normale" (campi senza -holo) e "foil" (campi -holo).
    Le altre righe restano uguali, con versione = None."""
    df = df.copy()
    df["versione"] = None
    ambigui = df[df.campo_prezzo == "ambiguo"]
    if ambigui.empty:
        return df

    normale = ambigui.copy()
    normale["versione"] = "normale"
    normale["campo_prezzo"] = "trend"
    foil = ambigui.copy()
    foil["versione"] = "foil"
    foil["campo_prezzo"] = "trend-holo"
    for campo in CAMPI:
        normale[f"{campo}_rif_eur" if campo != "trend" else "prezzo_rif_eur"] = normale[f"cm_{campo}"]
        foil[f"{campo}_rif_eur" if campo != "trend" else "prezzo_rif_eur"] = foil[f"cm_{campo}_holo"]

    return pd.concat([df[df.campo_prezzo != "ambiguo"], normale, foil], ignore_index=True)
