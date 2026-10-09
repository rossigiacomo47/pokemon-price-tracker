# Test sul mini-storico a 30 giorni (2026-W41) · CLAUDE.md 8.3

**Domanda:** le carte che un mese fa costavano meno delle loro simili sono poi salite più delle altre?

Prezzo di un mese fa = media a 30 giorni Cardmarket; oggi = trend. Carte: 3457. Crescita media di tutto il pool: +1.6%.

**Limiti:** `avg30` è una media, non un prezzo puntuale; un solo mese; il rumore della media può creare un falso "ritorno verso la media". È un test grezzo, il primo basato sui dati.

## A. Rispetto alle carte simili (comparabili rettificati)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 631 | 6.0 | 0.0 | 49.9 |
| 2 | 630 | 2.0 | -0.0 | 47.3 |
| 3 | 631 | -1.2 | -1.3 | 42.0 |
| 4 | 630 | -1.1 | -2.6 | 42.1 |
| 5 · più sopravvalutate | 631 | 1.4 | -0.2 | 47.5 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.060 (p = 0.000761). Negativa = le carte più sottovalutate sono salite di più.

## B. Rispetto al modello (valore delle caratteristiche)

| gruppo | carte | crescita_media_pct | crescita_mediana_pct | quota_salite_pct |
|---|---|---|---|---|
| 1 · più sottovalutate | 692 | 6.3 | 0.7 | 51.4 |
| 2 | 691 | 1.4 | -0.6 | 46.0 |
| 3 | 691 | -1.1 | -1.8 | 43.0 |
| 4 | 691 | 1.0 | -1.1 | 44.6 |
| 5 · più sopravvalutate | 692 | 0.7 | -0.1 | 47.7 |

Correlazione di Spearman tra sottovalutazione e crescita: -0.052 (p = 0.00244). Negativa = le carte più sottovalutate sono salite di più.
