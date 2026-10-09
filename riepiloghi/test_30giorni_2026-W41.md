# Test sul mini-storico a 30 giorni (2026-W41) · CLAUDE.md 8.3

**Domanda:** le carte che un mese fa costavano meno delle loro simili sono poi salite più delle altre?

Prezzo di un mese fa = media a 30 giorni Cardmarket; oggi = trend. Carte: 3457. Crescita media di tutto il pool: +1.6%.

**Limiti:** `avg30` è una media, non un prezzo puntuale; un solo mese; il rumore della media può creare un falso "ritorno verso la media". È un test grezzo, il primo basato sui dati.

## A. Rispetto alle carte simili (comparabili rettificati)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 642 | 5.1 | 0.0 | 49.7 |
| 2 | 641 | 2.0 | -0.4 | 46.0 |
| 3 | 642 | 0.4 | -0.8 | 44.5 |
| 4 | 641 | 0.7 | -1.3 | 44.5 |
| 5 · più sopravvalutate | 642 | -0.2 | -1.6 | 45.3 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.063 (p = 0.000373). Negativa = le carte più sottovalutate sono salite di più.

## B. Rispetto al modello (valore delle caratteristiche)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 692 | 6.8 | 0.6 | 51.0 |
| 2 | 691 | 0.4 | -0.9 | 45.6 |
| 3 | 691 | -0.1 | -0.9 | 44.0 |
| 4 | 691 | -0.1 | -1.2 | 44.9 |
| 5 · più sopravvalutate | 692 | 1.3 | -0.2 | 47.3 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.052 (p = 0.00211). Negativa = le carte più sottovalutate sono salite di più.
