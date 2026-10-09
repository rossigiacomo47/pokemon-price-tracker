# Test sul mini-storico a 30 giorni (2026-W41) · CLAUDE.md 8.3

**Domanda:** le carte che un mese fa costavano meno delle loro simili sono poi salite più delle altre?

Prezzo di un mese fa = media a 30 giorni Cardmarket; oggi = trend. Carte: 3457. Crescita media di tutto il pool: +1.6%.

**Limiti:** `avg30` è una media, non un prezzo puntuale; un solo mese; il rumore della media può creare un falso "ritorno verso la media". È un test grezzo, il primo basato sui dati.

## A. Rispetto alle carte simili (comparabili rettificati)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 642 | 6.2 | 0.1 | 50.0 |
| 2 | 642 | 1.2 | 0.0 | 47.5 |
| 3 | 642 | 0.5 | -1.3 | 43.5 |
| 4 | 642 | 0.4 | -1.3 | 43.8 |
| 5 · più sopravvalutate | 642 | -0.3 | -1.4 | 45.2 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.073 (p = 3.38e-05). Negativa = le carte più sottovalutate sono salite di più.

## B. Rispetto al modello (valore delle caratteristiche)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 692 | 6.2 | 0.3 | 50.6 |
| 2 | 691 | 0.9 | -0.8 | 45.9 |
| 3 | 691 | -0.2 | -1.5 | 43.6 |
| 4 | 691 | -0.8 | -1.4 | 43.8 |
| 5 · più sopravvalutate | 692 | 2.2 | 0.0 | 48.8 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.047 (p = 0.00587). Negativa = le carte più sottovalutate sono salite di più.
