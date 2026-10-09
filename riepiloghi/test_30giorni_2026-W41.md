# Test sul mini-storico a 30 giorni (2026-W41) · CLAUDE.md 8.3

**Domanda:** le carte che un mese fa costavano meno delle loro simili sono poi salite più delle altre?

Prezzo di un mese fa = media a 30 giorni Cardmarket; oggi = trend. Carte: 3457. Crescita media di tutto il pool: +1.6%.

**Limiti:** `avg30` è una media, non un prezzo puntuale; un solo mese; il rumore della media può creare un falso "ritorno verso la media". È un test grezzo, il primo basato sui dati.

## A. Rispetto alle carte simili (comparabili rettificati)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 640 | 6.2 | 0.0 | 48.6 |
| 2 | 639 | 2.4 | 0.0 | 49.5 |
| 3 | 639 | -0.7 | -1.5 | 42.1 |
| 4 | 639 | -0.2 | -1.8 | 43.8 |
| 5 · più sopravvalutate | 640 | 0.0 | -0.9 | 46.1 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.070 (p = 6.88e-05). Negativa = le carte più sottovalutate sono salite di più.

## B. Rispetto al modello (valore delle caratteristiche)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 692 | 6.8 | 0.7 | 51.3 |
| 2 | 691 | 0.5 | -1.1 | 45.3 |
| 3 | 691 | -0.1 | -0.9 | 44.1 |
| 4 | 691 | -0.5 | -1.4 | 44.3 |
| 5 · più sopravvalutate | 692 | 1.6 | -0.1 | 47.7 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.053 (p = 0.0017). Negativa = le carte più sottovalutate sono salite di più.
