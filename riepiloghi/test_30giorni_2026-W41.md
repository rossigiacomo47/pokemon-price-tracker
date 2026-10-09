# Test sul mini-storico a 30 giorni (2026-W41) · CLAUDE.md 8.3

**Domanda:** le carte che un mese fa costavano meno delle loro simili sono poi salite più delle altre?

Prezzo di un mese fa = media a 30 giorni Cardmarket; oggi = trend. Carte: 3457. Crescita media di tutto il pool: +1.6%.

**Limiti:** `avg30` è una media, non un prezzo puntuale; un solo mese; il rumore della media può creare un falso "ritorno verso la media". È un test grezzo, il primo basato sui dati.

## A. Rispetto alle carte simili (comparabili rettificati)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 641 | 5.7 | 0.0 | 47.9 |
| 2 | 641 | 2.5 | 0.0 | 49.1 |
| 3 | 640 | -0.3 | -1.4 | 43.1 |
| 4 | 641 | 1.0 | -0.1 | 46.3 |
| 5 · più sopravvalutate | 641 | -0.3 | -1.4 | 45.2 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.070 (p = 7.56e-05). Negativa = le carte più sottovalutate sono salite di più.

## B. Rispetto al modello (valore delle caratteristiche)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 692 | 6.3 | 0.5 | 50.9 |
| 2 | 691 | 0.9 | -0.7 | 46.2 |
| 3 | 691 | 0.0 | -0.9 | 43.7 |
| 4 | 691 | -1.2 | -1.6 | 43.4 |
| 5 · più sopravvalutate | 692 | 2.3 | 0.0 | 48.6 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.048 (p = 0.0045). Negativa = le carte più sottovalutate sono salite di più.
