# Test sul mini-storico a 30 giorni (2026-W41) · CLAUDE.md 8.3

**Domanda:** le carte che un mese fa costavano meno delle loro simili sono poi salite più delle altre?

Prezzo di un mese fa = media a 30 giorni Cardmarket; oggi = trend. Carte: 3457. Crescita media di tutto il pool: +1.6%.

**Limiti:** `avg30` è una media, non un prezzo puntuale; un solo mese; il rumore della media può creare un falso "ritorno verso la media". È un test grezzo, il primo basato sui dati.

## A. Rispetto alle carte simili (comparabili rettificati)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 638 | 6.4 | 0.5 | 50.8 |
| 2 | 638 | 1.1 | -0.8 | 45.0 |
| 3 | 638 | 0.8 | -0.6 | 45.6 |
| 4 | 638 | 0.3 | -0.8 | 45.0 |
| 5 · più sopravvalutate | 638 | -0.2 | -1.7 | 45.1 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.076 (p = 1.96e-05). Negativa = le carte più sottovalutate sono salite di più.

## B. Rispetto al modello (valore delle caratteristiche)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 692 | 6.2 | 0.5 | 50.9 |
| 2 | 691 | 0.7 | -0.8 | 45.7 |
| 3 | 691 | 0.1 | -1.4 | 43.3 |
| 4 | 691 | -1.0 | -1.4 | 44.4 |
| 5 · più sopravvalutate | 692 | 2.3 | 0.0 | 48.4 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.048 (p = 0.00469). Negativa = le carte più sottovalutate sono salite di più.
