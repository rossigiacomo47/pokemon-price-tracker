# Variabili del modello del prezzo equo · PROPOSTA (9/10/2026, da approvare)

Calcolate da `src/caratteristiche.py`, una riga per variante, in `data/caratteristiche/AAAA-Wnn.parquet`.
I **conteggi per valore** (sulle carte che entrano nel modello) sono in `riepiloghi/blocco3_AAAA-Wnn.md`.
Le tabelle di conversione sono in `tabelle/` (set, rarità, rilasci) e in `iconici.csv`.

**Carte nel modello** = perimetro "dentro" + prezzo di riferimento ≥ 3 € (`soglia_bulk_eur`) + fonte TCGdex.
Il **catalogo giapponese da TCGCSV** (set vuoti su TCGdex e promo SM-P, S-P, s8a-P) ha le variabili ma
non il prezzo Cardmarket: serve per la ricerca e come comparabile con i prezzi NM inseriti a mano.

| # | Variabile (colonna) | Definizione | Fonte | Note e casi incerti |
|---|---|---|---|---|
| 1 | Pokémon (`pokemon_cat`) | Primo Pokémon raffigurato; i 30 più frequenti nel modello come categorie proprie, gli altri "altro" | TCGdex `dexId`; se manca, nome della carta confrontato con i nomi PokéAPI (en/ja) | Carte con più Pokémon (TAG TEAM): conta il primo (`n_pokemon` > 1) |
| 2 | Iconicità (`iconicita`) | alto / medio / basso | `iconici.csv` (non in lista = basso); proposta dai dati in `riepiloghi/iconicita_proposta.csv` (`src/iconicita_dati.py`) | **Fuori dal modello dal 10/10/2026** (doppio conteggio con il Pokémon raffigurato): usata solo come filtro dei comparabili |
| 3 | Generazione (`generazione`) | 1–9 | PokéAPI `generation_id` | |
| 4 | Leggendario/misterioso (`leggendario`) | sì / no | PokéAPI `is_legendary` o `is_mythical` | |
| 5 | Rarità armonizzata (`rarita_armonizzata`) | illustration rare · special illustration rare · character rare · gold-hyper-rainbow · shiny · galleria · promo | `tabelle/rarita.csv`; rarità mancanti su TCGdex completate da TCGplayer (set + numero) | **Riferimento del modello: illustration rare** (decisione 9/10). Gold, hyper e rainbow uniti: le fonti non le distinguono in modo affidabile. "Secret Rare" giapponesi e rarità nuove (Black White, Mega Attack, RGB, Futuristic) = da verificare |
| 5b | Alternate art (`alternate_art`) | sì / no | Nome TCGplayer con "Alternate" (Spada e Scudo, Ultra/Secret Rare) | Trattate come special illustration rare; la colonna permette di verificare se valgono davvero come le SIR. Le "special art" giapponesi di Spada e Scudo non sono ancora riconosciute |
| 6 | Meccanica (`meccanica`) | ex · EX · GX · V · VMAX · VSTAR · Mega · nessuna | TCGdex `suffix` + nome | TAG TEAM = GX; "EX" dopo il 2023 = ex |
| 7 | Variante (`variante`) | normale · holo · reverse | `variants_detailed` TCGdex + campo del prezzo Cardmarket | Se il prezzo sta in `trend-holo`, la carta è holo anche se TCGdex dice "normal" (es. Pikachu Hiroshima). `finitura_holo` serve alla somiglianza dei comparabili (decisione 9/10: non è un filtro) |
| 8 | Era (`era`) | Sole e Luna · Spada e Scudo · Scarlatto e Violetto · Mega | Serie TCGdex (`tabelle/set.csv`) | Si sovrappone all'età del set: controllo VIF nel blocco 4 |
| 9 | Età del set (`fascia_eta`) | 0–3 · 3–6 · 6–12 · 12–24 · 24–48 · 48+ mesi | Data di uscita del set | **Proposta**: aggiunte 24–48 e 48+ perché "24+" metteva insieme 2017–2024 |
| 10 | Tipo di set (`tipo_set`) | principale · speciale · sottoset · promo | `tabelle/set.csv` (regole + elenco) | Speciale = set ".5", high class pack giapponesi, mazzi, McDonald's |
| 11 | Modalità di rilascio (`rilascio`) | busta · prodotto speciale · evento o torneo · Pokémon Center · altro · da classificare | `tabelle/rilasci.csv`: timbri TCGdex, set | **Molte promo senza timbro restano "da classificare"**: elenco sopra 20 € in `riepiloghi/blocco3_rilasci_da_classificare.csv` |
| 12 | Diluizione (`diluizione_log`) | log del numero di carte della stessa rarità armonizzata nel set | Calcolata | **Tolta dal modello il 10/10/2026** (peso contrario alle attese, nessun beneficio in validazione) |
| 13 | Stamped (`stamped`) | sì / no | Timbro della variante TCGdex | |
| 14 | Esclusiva linguistica (`esclusiva`) | entrambe · solo giapponese · solo internazionale · incerta | Stessa specie + stesso illustratore nell'altra lingua, tra carte rare, full art o promo | **Proposta grezza**: "incerta" se manca l'illustratore o se la gemella potrebbe stare nei set giapponesi vuoti su TCGdex. Da migliorare (CLAUDE.md 4.7.5) |
| 15 | Illustratore (`illustratore_cat`) | Illustratori con almeno 30 carte nel modello; altri "altro"; mancante "sconosciuto" | TCGdex `illustrator` | |
| 16 | Standard (`standard`) | sì / no | TCGdex `legal.standard` | |
| 17 | Famiglia (`famiglia`) | carta da busta · promo e rilascio speciale | Tipo di set promo, rarità Promo, Classic Collection, McDonald's, stamped | Le stamped di carte da busta sono "promo e rilascio speciale" (decisione D5) |
| 18 | Lingua (`lingua`) | en (internazionale) · ja (giapponese) | Fonte | Modello unico (decisione D6) |
