# Pokémon Price Tracker — valutatore di carte

Strumento personale che stima il prezzo equo Near Mint di carte Pokémon singole non gradate
(Cardmarket, EUR), con comparabili rettificati e giudizio d'investimento.
Le istruzioni complete e le decisioni sono in [CLAUDE.md](CLAUDE.md) (fonte di verità).

Pagina: https://rossigiacomo47.github.io/pokemon-price-tracker/ (provvisoria, non indicizzata)

## A che punto siamo

| Blocco | Stato |
|---|---|
| 0 · Prima di iniziare | Mac pronto (Python 3.13, Git, GitHub CLI in ~/.local/bin), account GitHub collegato. Da fare: Python e Git sul PC Windows |
| 1 · Fotografia del mercato | Prima fotografia salvata l'8/10/2026 (`data/mercato/2026-W41.parquet`). Decisioni D3–D6 prese: soglia 3 €, prezzi ambigui divisi normale/foil, stamped dentro, modello unico en+ja. Perimetro provvisorio: 3.173 varianti con prezzo ≥ 3 € |
| 2 · Online e raccolta automatica | Repository pubblico, pagina su GitHub Pages, workflow settimanale (lunedì 11:00 UTC) provato a mano l'8/10/2026. Da verificare: prima esecuzione automatica lunedì 12/10 (2026-W42) |
| 3 · Caratteristiche | In corso. Fatto: punto 3.1 (fonti TCGCSV e PokéAPI in `data/riferimento/`). Da fare: set.csv, rarita.csv, rilasci.csv, variabili, corrispondenze en↔ja |
| 4–9 | Da iniziare |

Riepilogo del blocco 1: [riepiloghi/blocco1_2026-W41.md](riepiloghi/blocco1_2026-W41.md)

## Come si usa

Prima volta (crea l'ambiente virtuale con le librerie):

- Mac: `python3 -m venv .venv` e poi `.venv/bin/python -m pip install -r requirements.txt`
- Windows: `py -3.13 -m venv .venv` e poi `.venv\Scripts\python -m pip install -r requirements.txt`

Fotografia del mercato (circa 25 minuti; non sovrascrive una fotografia già salvata):

- Mac: `.venv/bin/python src/scarica_tcgdex.py` e `.venv/bin/python src/scarica_tcgcsv_promo_ja.py`
- Windows: `.venv\Scripts\python src\scarica_tcgdex.py` e `.venv\Scripts\python src\scarica_tcgcsv_promo_ja.py`

Riepilogo: `.venv/bin/python src/riepilogo.py 2026-W41` (Windows: `.venv\Scripts\python src\riepilogo.py 2026-W41`)

## File

| File | Contenuto |
|---|---|
| `config.json` | Parametri: pause tra le richieste, serie scaricate, soglia bulk (3 €), fascia NM (0–5%) |
| `src/scarica_tcgdex.py` | Scarica da TCGdex le carte moderne en/ja, una riga per variante |
| `src/scarica_tcgcsv_promo_ja.py` | Scarica da TCGCSV (TCGplayer, USD) le promo giapponesi SM-P, S-P, SV-P, M-P |
| `src/riepilogo.py` | Conteggi, perimetro provvisorio, copertura giapponesi, carte di controllo |
| `data/mercato/` | Fotografie settimanali (Parquet). **Non si cancellano né si riscrivono** |
| `data/log/` | Richieste fallite durante i download |
| `cache/` | Copie locali delle risposte API (solo sul computer, non su GitHub) |

## Prezzo di riferimento

Cardmarket tramite TCGdex: `trend` oppure `trend-holo` secondo la regola di CLAUDE.md 4.1
(campo `campo_prezzo`). Condizione e lingua **non filtrate**. Uno 0 è un dato mancante.

## Prossimo passo

Blocco 3, punto 3.2. Note per riprendere:
- collegamento set TCGdex ↔ TCGCSV: per sigla (ja 83/90, en 55/82); eccezioni da scrivere a mano, già individuate: en sm1→1863, sm2→1919, sm3→1957, sm4→2071, sm5→2178, sm6→2209, sm8→2328, sm9→2377, sm10→2420, sm11→2464, sm12→2534, sma→2594, swshp→2545, swsh1→2585, swsh4.5sv→2781, cel25cc→2931, 30th-c→24837, 2017sm→2148, 2018sm→2364, 2019sm→2555, 2021swsh→2782, 2022swsh→3150, 2023sv→23306, 2024sv→24163, tk-sm-*→2069; ja SM1p→23692, SM2p→23693, SM3p→23694, SM4p→23707, SM5p→23695, MC→24567, SVLS→23793;
- 23 set giapponesi sono vuoti su TCGdex (tra cui S4a Shiny Star V, S6a Eevee Heroes, S8a 25th, S10b Pokémon GO): da discutere con Giacomo;
- alternate art SWSH riconoscibili dal nome TCGplayer ("Alternate Full Art", "Alternate Art Secret");
- decisioni blocco 3: Q1-A (niente variabile full art), Q2-A (revisione manuale solo casi incerti > 20 € non automatizzabili).


Controllare lunedì 12/10 che la fotografia 2026-W42 sia stata salvata da sola. Poi blocco 3: caratteristiche delle carte (rarita.csv con la rarità giapponese da TCGCSV, set.csv, rilasci.csv, iconici.csv).
Da recuperare nella prossima fotografia: le 9 carte fallite con errore 503 (`data/log/`).

*Valutazioni e giudizi sono stime statistiche con margine di errore, basate su dati di mercato
e su carte simili: non sono certezze né consulenza finanziaria.*
