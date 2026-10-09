# Test sul mini-storico a 30 giorni (2026-W41) · CLAUDE.md 8.3

**Domanda:** le carte che un mese fa costavano meno delle loro simili sono poi salite più delle altre?

Prezzo di un mese fa = media a 30 giorni Cardmarket; oggi = trend. Carte: 3457. Crescita media di tutto il pool: +1.6%.

**Limiti:** `avg30` è una media, non un prezzo puntuale; un solo mese; il rumore della media può creare un falso "ritorno verso la media". È un test grezzo, il primo basato sui dati.

## A. Rispetto alle carte simili (comparabili rettificati)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 640 | 6.3 | 0.4 | 50.6 |
| 2 | 640 | 0.9 | -0.6 | 45.2 |
| 3 | 640 | 0.6 | -0.7 | 45.0 |
| 4 | 640 | -0.7 | -1.7 | 43.3 |
| 5 · più sopravvalutate | 640 | 0.6 | -1.2 | 45.5 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.066 (p = 0.000173). Negativa = le carte più sottovalutate sono salite di più.

## B. Rispetto al modello (valore delle caratteristiche)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 692 | 6.8 | 0.6 | 51.0 |
| 2 | 691 | 0.4 | -0.9 | 45.6 |
| 3 | 691 | -0.1 | -0.9 | 44.0 |
| 4 | 691 | -0.1 | -1.2 | 44.9 |
| 5 · più sopravvalutate | 692 | 1.3 | -0.2 | 47.3 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.052 (p = 0.00211). Negativa = le carte più sottovalutate sono salite di più.
