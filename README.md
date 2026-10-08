# Pokémon Price Tracker — valutatore di carte

Strumento personale che stima il prezzo equo Near Mint di carte Pokémon singole non gradate
(Cardmarket, EUR), con comparabili rettificati e giudizio d'investimento.
Le istruzioni complete e le decisioni sono in [CLAUDE.md](CLAUDE.md) (fonte di verità).

## A che punto siamo

| Blocco | Stato |
|---|---|
| 0 · Prima di iniziare | Mac pronto (Python 3.13, Git). Da fare: Python e Git sul PC Windows, account GitHub da verificare |
| 1 · Fotografia del mercato | Prima fotografia salvata l'8/10/2026 (`data/mercato/2026-W41.parquet`). Decisioni D3–D6 prese: soglia 3 €, prezzi ambigui divisi normale/foil, stamped dentro, modello unico en+ja. Perimetro provvisorio: 3.173 varianti con prezzo ≥ 3 € |
| 2–9 | Da iniziare |

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

Blocco 2: GitHub, Pages e raccolta settimanale automatica (serve l'account GitHub).
Da recuperare nella prossima fotografia: le 9 carte fallite con errore 503 (`data/log/`).

*Valutazioni e giudizi sono stime statistiche con margine di errore, basate su dati di mercato
e su carte simili: non sono certezze né consulenza finanziaria.*
