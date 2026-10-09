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
| 3 · Caratteristiche | Tabelle `set.csv`, `rarita.csv`, `rilasci.csv` **approvate il 10/10/2026**; rilasci delle promo da Bulbapedia. Da confermare: livelli di iconicità proposti dai dati (`riepiloghi/iconicita_proposta.csv`) |
| 4 · Modello del prezzo equo | Iconicità e diluizione tolte dal modello (10/10/2026). Ruolo: seconda opinione del valore relativo. Test a 30 giorni: segnale debole ma nella direzione giusta (`riepiloghi/test_30giorni_2026-W41.md`) |
| 5 · Comparabili e scheda | **Bozza online**: inserisci il minimo NM di oggi, la scheda dice se la carta è sottovalutata, in linea o sopravvalutata rispetto alle simili (CLAUDE.md 2.5). Avviso "Poco affidabile" quando le carte simili sono troppo diverse |
| 6–9 | Da iniziare |

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

Leggere **[riepiloghi/revisione_notte_2026-10-09.md](riepiloghi/revisione_notte_2026-10-09.md)** e rispondere alle decisioni.
Controllare lunedì 12/10 che la fotografia 2026-W42 sia stata salvata da sola.

Ordine degli script (dopo una nuova fotografia):
`src/tabelle.py` (solo la prima volta) → `src/caratteristiche.py` → `src/modello.py` → `src/comparabili.py` → `src/test_30giorni.py` → di nuovo `src/comparabili.py` (per inserire il test nella pagina "Il modello").
Per la proposta di iconicità dai dati: `src/iconicita_dati.py` (non modifica `iconici.csv`).

*Valutazioni e giudizi sono stime statistiche con margine di errore, basate su dati di mercato
e su carte simili: non sono certezze né consulenza finanziaria.*
