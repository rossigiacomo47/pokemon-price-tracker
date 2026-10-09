# Pokémon Price Tracker (valutatore di carte) — istruzioni del progetto per Claude Code

> Versione 2.6 (10 ottobre 2026: iconicità fuori dal modello e usata solo nei comparabili, ricalcolata dai dati; diluizione tolta dal modello; character super rare (CSR) separata dalla character rare; tabelle `set.csv`, `rarita.csv`, `rilasci.csv` approvate; avviso "poco affidabile" nella scheda). Versione 2.5 (9 ottobre 2026: la valutazione confronta il minimo NM della carta con il valore delle carte simili, per il potenziale di crescita; test a 30 giorni). Versione 2.3 (8 ottobre 2026, dopo il blocco 1: soglia bulk 3 €, prezzi ambigui divisi normale/foil, stamped nel perimetro, modello unico en+ja, verifica del trend). Versione 2.2: promo di ogni finitura, regola del prezzo di riferimento per variante, era Sole e Luna da dicembre 2016. Versione 2.1: fascia Near Mint, carte di controllo, perimetro ampliato. Sostituisce l'impostazione precedente basata sull'archivio storico TCGCSV, che non è più scaricabile (i file d'archivio rispondono "403").

## 1. Chi sono e come devi lavorare con me

- Sono Giacomo, studente magistrale di marketing, con **conoscenze informatiche di base**.
- Uso **Claude Code dall'app Claude per computer** (scheda Code), non dal terminale. Ho sia un **PC Windows** sia un **Mac**, e un **iPhone** quando sono fuori casa. Il progetto deve funzionare su entrambi i computer.
- Rispondi sempre in **italiano chiaro e didattico** e definisci subito ogni termine tecnico.
- Indica il livello di ogni passaggio: **Principiante / Intermedio / Avanzato**.
- Metti un avviso **"Attenzione"** prima di ogni operazione rischiosa.
- **Prima di scrivere codice per una fase**, mostrami il piano e aspetta il mio ok.
- I comandi li esegui tu e io approvo. Quando invece devo fare qualcosa io (installare un programma, creare un account, inserire una chiave), spiegamelo **un passo alla volta** con questo formato:
  sistema operativo / dove farlo / cosa fare / cosa succede / risultato atteso / possibili errori / come tornare indietro.
  Se cambia tra Windows e Mac, dammi entrambe le versioni.
- **Mai comandi distruttivi** (es. `git push --force`, cancellazione di file o dei dati salvati) senza chiedermelo esplicitamente.
- Alla fine di ogni fase **verifica che funzioni davvero** e mostrami il risultato.
- Quando introduci un concetto statistico (regressione, logaritmo, validazione incrociata…), spiegamelo con un **esempio concreto su una carta**.
- Se una risposta è lunga, dividila in moduli numerati invece di tagliare contenuti.
- Per le scelte rapide preferisco **domande a scelta multipla**.

## 1b. File di partenza nella cartella

All'inizio la cartella contiene:

| File | A cosa serve | Chi lo usa |
|---|---|---|
| `CLAUDE.md` | Queste istruzioni: **sono la fonte di verità** | tu (Claude Code) |
| `riferimenti/mockup-dashboard.html` | **Mockup della dashboard da seguire** (sezione 10) | tu, per aspetto e struttura del sito |
| `riferimenti/scheda-progetto.html` | Riassunto visivo del progetto | io, per orientarmi |
| `riferimenti/guida-bussola.html` | Guida passo passo ai blocchi di lavoro | io |
| `carte_controllo.csv` | Le mie carte di controllo (sezione 6.8): 15 inserite l'8/10/2026, con l'offerta minima NM; da completare con altre 3–5 carte | entrambi |
| `iconici.csv` | Mia lista iniziale dei Pokémon iconici (sezione 5.4), da confermare | entrambi |

- Se un file di riferimento e `CLAUDE.md` non coincidono, **vale `CLAUDE.md`**: segnalamelo.
- Non modificare i file in `riferimenti/` senza chiedermelo.
- Le righe marcate "ESEMPIO" nei file CSV vanno ignorate e poi cancellate quando inserisco i dati veri.

## 2. Obiettivo del progetto

Uno strumento che, quando inserisco una **carta singola non gradata**, mi dice:

1. **A quanto dovrebbe essere** (prezzo equo, con un intervallo) sul mercato **Cardmarket in euro**.
2. **Se il prezzo attuale è in linea, sottovalutato o sopravvalutato** rispetto a carte simili.
3. **Con quali carte l'ha confrontata**: le carte più simili, con prezzo, link e differenze, così posso verificarle a mano.
4. **Un giudizio d'investimento**: è fondamentale. Deve dire se conviene comprare per tenere la carta nel tempo, con le ragioni, i rischi e **quanto è affidabile**.
5. Poi la carta entra nel **monitoraggio**: da quel giorno salva il prezzo, mostra il grafico e mi avvisa sull'iPhone.

Lo uso sia per **collezionare** sia per **rivendere**.

**Regola guida: tutto basato sui dati e verificabile.**
- Ogni numero deve dire da dove viene.
- Ogni giudizio deve mostrare i comparabili.
- Ogni "consiglio" deve dichiarare se è già stato **validato** sui dati o no.

**Prima versione, perimetro deciso:**
- solo **carte singole non gradate**;
- solo **carte Pokémon** (niente carte Allenatore ed Energia);
- solo **ere moderne, dal 2017**: Sole e Luna, Spada e Scudo, Scarlatto e Violetto, Mega, e i periodi giapponesi corrispondenti;
- **solo queste carte** (deciso l'8 ottobre 2026):
  1. **tutte le promo** Pokémon da Sole e Luna in poi (Black Star Promos internazionali, promo giapponesi come SM-P, S-P, SV-P, promo Pokémon Center, premi di eventi e tornei, promo in box e collezioni), comprese le carte Pokémon della **Celebrations Classic Collection** (ristampe del 2021, famiglia "promo e rilascio speciale", modalità di rilascio "prodotto speciale");
  2. dai set da Sole e Luna in poi, solo le carte Pokémon con rarità **illustration rare, special illustration rare, character rare** (giapponesi AR, SAR, CHR, CSR; dal 10/10/2026 la CSR è una rarità a sé, "character super rare", separata dalla CHR) e, per Spada e Scudo, le **alternate art** (le "full art alternative" di V, VMAX e VSTAR), trattate come equivalente delle special illustration rare;
  3. **gold, hyper e rainbow rare** (giapponesi UR, HR);
  4. **shiny** (Shiny Vault, shiny rare) e carte Pokémon delle **gallerie** (Trainer Gallery, Galarian Gallery e simili).
- **Escluse:** full art V/GX/ex/EX "normali" (non alternate art), holo rare, comuni, non comuni e tutte le altre rarità.
- **Precisazione (8 ottobre 2026):** le promo del punto 1 sono incluse **qualunque sia la finitura** (holo, non holo, stamped, full art), es. Hiroshima's Pikachu 261/SV-P. L'esclusione delle holo rare (e di comuni e non comuni) vale **solo per le carte da busta**.
- **Inizio dell'era (decisione D2, 8 ottobre 2026):** si include tutta l'era Sole e Luna, compresi i set giapponesi SM1S/SM1M usciti a dicembre 2016.
- Se valuto una carta fuori da questo perimetro, la dashboard deve dirlo chiaramente: "carta fuori dal perimetro del modello".
- carte **internazionali** e **giapponesi** (le esclusive giapponesi mi interessano molto): fonte dei prezzi giapponesi da verificare nel blocco 1 (sezione 4.7).

Sigillati, gradate, carte Allenatore, vintage e le lingue italiana e cinese sono estensioni successive (Fase 9).

Costo di funzionamento previsto: **0 €**. Eventuali fonti a pagamento solo con il mio ok (sezione 4.5).

## 3. Idea di fondo (spiegala sempre così)

- **Prezzo equo = modello di prezzo edonico.** È una regressione multipla sul **logaritmo del prezzo**: il prezzo di una carta si scompone nel valore delle sue caratteristiche (Pokémon raffigurato, rarità, promo, esclusiva linguistica…).
  - Con il logaritmo, ogni coefficiente si legge come **sovrapprezzo in %** (es. "Pikachu: +60%").
  - I pesi **li stima il modello dai dati**, non li decidiamo a mano.
  - Le combinazioni (es. "Pikachu ed esclusiva giapponese insieme valgono più della somma") si gestiscono con le **interazioni**.
- **Comparabili rettificati**, come nelle stime immobiliari: si prendono le carte più simili e si correggono i loro prezzi per le differenze (es. "uguale alla tua ma non promo: 40 € → corretta per la promo 50 €").
- **Niente storico disponibile?** Il modello impara confrontando **migliaia di carte oggi** (una "fotografia del mercato"), non l'andamento nel tempo.
- **Da subito salviamo fotografie periodiche del mercato.** Così il giudizio d'investimento si può verificare e migliorare nel tempo.

## 4. Fonti dei dati

### 4.1 TCGdex — fonte principale (prezzi Cardmarket in euro + caratteristiche)
- Gratuito, **nessuna chiave**. Documentazione: https://tcgdex.dev/markets-prices e https://tcgdex.dev/reference/card
- Endpoint carta: `https://api.tcgdex.net/v2/{lingua}/cards/{id}`. **Verificato l'8/10/2026:** l'API GraphQL non espone i prezzi, quindi serve una richiesta per carta (circa 22.500 carte moderne, circa 45 minuti con 3 richieste in parallelo).
- Prezzi `pricing.cardmarket` (EUR, aggiornati **una volta al giorno**): `trend`, `avg`, `low`, `avg1`, `avg7`, `avg30` e le versioni `-holo`.
  - **Una riga per variante.** Il campo `variants_detailed` dà un prezzo separato per ogni variante (normale, reverse, holo, stamped, foil speciali), ognuna con il suo prodotto Cardmarket. Le versioni stamped sono prodotti separati con prezzi diversi.
  - **Prezzo di riferimento (regola decisa l'8/10/2026):** su Cardmarket il campo `-holo` è la versione reverse/foil dello **stesso prodotto**. Quindi:
    1. variante reverse → `trend-holo`;
    2. variante normale di un prodotto che ha anche la reverse → `trend`;
    3. altrimenti si usa il campo con un prezzo valido (`trend`, es. Charizard VSTAR SWSH262, oppure `trend-holo`, es. Hiroshima's Pikachu SV-P 261);
    4. se sono pieni tutti e due e non si capisce quale sia la carta → "ambiguo": **segnalalo invece di indovinare**;
    5. un valore **0 è un dato mancante**, mai un prezzo.
  - Per ogni carta salva **quale campo** è stato usato (`campo_prezzo`).
  - `avg30` e `avg7` servono anche come **mini-storico a 30 giorni** (sezione 8.3).
  - Il prezzo non distingue condizione e, probabilmente, lingua: dichiaralo nella dashboard.
- Caratteristiche: `rarity`, `category`, `dexId`, `illustrator`, `variants` (`normal`, `reverse`, `holo`, `firstEdition`, `wPromo`), `set` (con data di uscita), disponibilità nelle diverse lingue, immagine ufficiale.
- **Verifica obbligatoria nel blocco 1:** le carte giapponesi su TCGdex (lingua `ja`) hanno prezzi Cardmarket? Su quante carte? Vedi la sezione 4.7.

### 4.2 TCGCSV — prezzi TCGplayer di oggi (USA, in dollari)
- https://tcgcsv.com — copia giornaliera dei dati TCGplayer, carte e sigillati.
  - **Categoria 3** "Pokemon": inglese, 220 set.
  - **Categoria 85** "Pokemon Japan": giapponese, 460 set.
  - Verificate l'8 ottobre 2026.
- **L'archivio storico non è più scaricabile**: non usarlo. I dati **del giorno** funzionano.
- Usi:
  - **fonte di riserva per i prezzi delle carte giapponesi** (sezione 4.7);
  - riconoscere le **esclusive linguistiche** (carta presente solo in giapponese o solo in inglese);
  - stimare il **sovrapprezzo giapponese vs inglese** sulle carte presenti in entrambe;
  - verificare il modello su un secondo mercato.
- Regole di cortesia (progetto amatoriale di una sola persona): User-Agent identificabile, pausa tra le richieste, scaricare **solo ciò che serve**, al massimo una volta al giorno.

### 4.3 Dati inseriti a mano (per la carta che valuto)
- **Popolazione PSA 10** e **popolazione PSA totale**: PSA non ha un'API pubblica per le popolazioni. Li leggo io sul sito PSA e li inserisco.
- **Copie in vendita su Cardmarket**: Cardmarket vieta la lettura automatica. Li leggo io e li inserisco.
- **Modalità di rilascio** e note sulla tiratura, quando non si ricavano in automatico.
- Questi dati **non entrano nella regressione** (non li abbiamo per tutte le carte). Entrano nel **confronto con i comparabili**, se ho inserito il dato anche per loro, e nel **giudizio d'investimento**, come fattori di scarsità. Mostra sempre che sono dati manuali e la data di inserimento.

### 4.4 eBay — non nella prima versione
- Vendite reali non accessibili (API riservata).
- Il contratto per sviluppatori vieta l'uso dei dati per addestrare modelli.
- Eventualmente in Fase 9, **solo per mostrare** annunci e link, mai nei modelli.

### 4.5 Opzioni a pagamento (solo con il mio ok)
- **PokemonPriceTracker API**, piano "API" (circa 9,99 $/mese, 6 mesi di storico).
  - Possibile uso: **un solo mese** per scaricare uno storico e fare un **backtest** del giudizio d'investimento.
  - Prima verifica: se lo storico include Cardmarket o solo TCGplayer, i crediti per chiamata, le condizioni d'uso (il sito ha indicazioni contrastanti sull'uso commerciale; il mio è personale) e la disdetta.
- **Scrydex**: popolazioni PSA per carte inglesi (piano e prezzo da verificare).
- **GemRate**: popolazioni PSA/CGC/Beckett/SGC, chiave su richiesta (prezzo non indicato).

### 4.5b Condizione (Near Mint) e lingua: regola fondamentale
**Il problema:** il prezzo `trend` di Cardmarket che riceviamo da TCGdex è un **prezzo di riferimento unico per prodotto**. Non possiamo chiederlo filtrato per condizione o per lingua: l'API ufficiale di Cardmarket è chiusa ai nuovi utenti e la lettura automatica delle pagine è vietata. Non sappiamo con certezza come Cardmarket calcola il `trend` rispetto a condizione e lingua.
- **Verifica del blocco 1 (8/10/2026):** l'aiuto ufficiale di Cardmarket non spiega il calcolo del trend. Fonti secondarie (CardNexus, MTG PowerTools) dicono che trend e medie non distinguono condizione e lingua. **Ipotesi di Giacomo:** il trend mescola tutte le lingue e risente anche di copie gradate vendute (da verificare, non confermato da fonti). Sulle 13 carte di controllo con prezzo, il centro della fascia NM va da −43% a +13% rispetto al trend: troppo variabile per una correzione unica, quindi per ora **nessuna correzione** (punto 3 sotto).
- **Nel blocco 1 verifica** sulle pagine di aiuto ufficiali di Cardmarket come viene calcolato il "trend" (quali condizioni, quali lingue). Riportami la fonte. Se non è chiaro, dichiaralo.

**Come lo gestiamo:**
1. **Addestramento e comparabili** usano il prezzo di riferimento per **tutte** le carte. Lo stesso "metro" per tutte rende il confronto **relativo** coerente. Il **livello assoluto** può però non corrispondere a una copia Near Mint nella lingua che voglio: dichiaralo sempre.
2. **Prezzi Near Mint manuali**: per la carta valutata **e per i suoi comparabili** inserisco io i prezzi Near Mint nella lingua giusta, come **fascia** (sezione 4.5c). È il flusso principale di valutazione (sezione 7.0).
3. **Calibrazione con le carte di controllo**: per ogni carta di controllo registro anche la **fascia Near Mint nella lingua giusta** (4.5c). Calcola lo scarto tipico tra il **punto centrale della fascia** e il `trend` (es. "le copie NM in italiano costano in media il 12% più del trend") e mostralo, con il numero di carte su cui si basa. Se lo scarto è stabile, usalo per correggere il prezzo equo e dichiara la correzione. Se è troppo variabile, non correggere e scrivilo.
4. **Copie in vendita (manuale)**: si contano sempre con i filtri **Near Mint + lingua**.
5. I **link di ricerca Cardmarket** devono aprire, se possibile, la ricerca già filtrata per lingua e condizione minima Near Mint. Verifica i parametri del link; se non è possibile, usa un link normale e scrivimelo.
6. Nella dashboard, accanto a ogni prezzo automatico: "prezzo di riferimento Cardmarket, condizione e lingua non filtrate".

### 4.5c Fascia Near Mint calcolata dal minimo (decisione dell'8 ottobre 2026)
**Il problema:** l'offerta "Near Mint" più bassa su Cardmarket spesso non è davvero Near Mint (venditore generoso nella valutazione). Usarla così com'è sottostima il valore di una copia NM vera.

**La regola (semplice, un solo numero da leggere):**
1. Su Cardmarket, con i filtri **Near Mint + lingua giusta**, leggo solo l'**offerta minima**.
2. Il sistema calcola la **fascia NM**: dal **minimo** al **minimo +5%** (larghezza sempre 5%). Il **punto centrale** è minimo +2,5%.
   - Esempio: minimo 300 € → fascia **300–315 €**, punto centrale **307,50 €**. Minimo 500 € → fascia **500–525 €**.
3. Le due percentuali stanno in `config.json` (`fascia_nm_da_pct: 0`, `fascia_nm_a_pct: 5`), facili da cambiare.
4. Il **punto centrale** è il prezzo NM usato in rettifica, mediana dei comparabili, rapporto NM/trend e calibrazione.
5. La **larghezza** della fascia entra nell'intervallo del prezzo equo: l'intervallo va dalla fascia rettificata più bassa alla più alta. Il controllo di dispersione ±15% (sezione 6) si fa invece sui **punti centrali**.
6. **Attenzione: +5% è un'ipotesi dichiarata, non un dato misurato.** Nella scheda scrivi accanto alla fascia: "stimata dal minimo NM +5% (ipotesi)". Se in futuro registro per qualche carta anche altre offerte, misura lo scarto vero e proponimi se correggere le percentuali.
7. Tipo di prezzo predefinito nella scheda: **"Minimo NM Cardmarket (+5%)"**. Alternativa: "Mediana ultime 3 vendite NM (eBay)", che non riceve la fascia perché sono vendite concluse. Non mescolare i due tipi nella stessa valutazione (7.0 punto 5).

### 4.6 Regole sulle fonti
- **Vietato** lo scraping di siti che lo vietano (Cardmarket, eBay, PSA compresi).
- **Mai inventare prezzi o dati.** Se una fonte non risponde: registra l'errore, salta, continua.
- Tieni traccia della **provenienza** di ogni dato (fonte, data, manuale o automatico).

### 4.7 Carte giapponesi: quale fonte di prezzo (decisione dell'8 ottobre 2026)
1. **Prima scelta: Cardmarket in euro tramite TCGdex.** Nel blocco 1 verifica quante carte giapponesi moderne hanno un prezzo Cardmarket. Mostrami il risultato e decidiamo insieme.
   - Se la copertura è buona: un **unico modello** internazionali + giapponesi, con la variabile **lingua**.
2. **Riserva: TCGplayer tramite TCGCSV (categoria 85).**
   - È in **dollari** e riguarda il **mercato USA**.
   - Serve un **modello separato** per le giapponesi, con conversione in euro (tasso BCE, es. servizio Frankfurter, da verificare); mostra sempre anche il prezzo originale in dollari.
   - Ogni giudizio su una carta giapponese deve dire chiaramente: **"rispetto al mercato USA (TCGplayer)"**.
3. Comparabili e confronti **sempre sulla stessa fonte di prezzo**: niente prezzi Cardmarket mescolati con prezzi TCGplayer nello stesso confronto.
4. **Indizio positivo (8 ottobre 2026):** Cardmarket elenca le carte giapponesi come **prodotti separati**, in espansioni proprie (es. "VMAX Climax", "Pokémon Card 151", "Terastal Festival ex"). Il loro prezzo di riferimento quindi riguarda solo il giapponese. Nel blocco 1 verifica se TCGdex riporta questi prezzi.
5. **Corrispondenza tra versioni:** la stessa illustrazione può esistere in giapponese e in inglese con set e numeri diversi. Crea una tabella di corrispondenza e **segnalami i casi incerti** invece di indovinare.
6. **Decisione D6 (8/10/2026, dopo il blocco 1):** le giapponesi da busta hanno prezzo Cardmarket su TCGdex nel 65–80% dei casi → **modello unico** internazionali + giapponesi, con la variabile lingua. Le promo giapponesi sono poche anche su TCGplayer (SM-P e S-P mancano su TCGdex): quelle con prezzo Cardmarket entrano nel modello unico; per quelle senza (es. SM-P, S-P, Pikachu Munch) la valutazione usa **solo i comparabili con i prezzi NM inseriti da Giacomo**, e la scheda lo dichiara. Niente modello separato su TCGplayer.
7. **Prezzi ambigui (D4) e stamped (D5), 8/10/2026:** se `trend` e `trend-holo` sono entrambi pieni, la variante si divide in due righe, "normale" (`trend`) e "foil" (`trend-holo`), quando si leggono i dati (`src/prezzi.py`), senza modificare la fotografia. Le varianti stamped di carte da busta entrano nel perimetro come "promo e rilascio speciale".
8. **Catalogo giapponese da TCGCSV (decisione del 9/10/2026):** 23 set giapponesi esistono su TCGdex ma senza carte (es. Shiny Star V, Eevee Heroes, VMAX Rising, 25th Anniversary Collection, Pokémon GO, Time Gazer). Le loro carte, e le promo SM-P, S-P e s8a-P, si prendono da TCGCSV (nome, numero, rarità, foto): **senza prezzo Cardmarket**, quindi fuori dall'addestramento, ma cercabili nella dashboard e usabili come comparabili con i prezzi NM inseriti a mano.

## 5. Variabili del modello del prezzo equo (lista decisa)

Perimetro: **carte Pokémon moderne (dal 2017), singole, non gradate, internazionali e giapponesi**. Ogni variabile va documentata in `variabili.md`, con definizione, fonte, valori e numero di carte per valore.

### 5.1 Il soggetto della carta
| # | Variabile | Valori | Fonte |
|---|---|---|---|
| 1 | Pokémon raffigurato | i ~30 più frequenti come categorie proprie, gli altri in "altro" | TCGdex `dexId` / nome |
| 2 | Livello di iconicità | alto / medio / basso | **Dati + mia lista** (5.4) |
| 3 | Generazione del Pokémon | 1–9 (da verificare l'effetto nostalgia della 1ª generazione) | numero Pokédex |
| 4 | Leggendario / misterioso | sì / no | PokéAPI (gratuita, senza chiave), campi `is_legendary` e `is_mythical` |

### 5.2 Rarità e stampa
| # | Variabile | Valori | Fonte |
|---|---|---|---|
| 5 | Rarità armonizzata | illustration rare / special illustration rare / character rare / gold / hyper-rainbow / shiny / galleria / **promo (nessuna rarità)** — solo le rarità del perimetro (sezione 2); le alternate art di Spada e Scudo → special illustration rare (tienile riconoscibili con una colonna `alternate_art`, così possiamo verificare se valgono davvero come le SIR) | TCGdex `rarity` + **tabella di conversione** `rarita.csv`: i nomi cambiano tra le ere **e tra le lingue** (es. AR, SAR, SR, UR, CHR, CSR giapponesi). Mostrami la tabella prima di usarla |
| 6 | Meccanica | ex / EX / GX / V / VMAX / VSTAR / Mega / nessuna | TCGdex (`suffix`, nome) |
| 7 | Variante | normale / holo / reverse | TCGdex `variants` |

### 5.3 Set, età e rilascio (gli indizi della tiratura)
| # | Variabile | Valori | Fonte |
|---|---|---|---|
| 8 | Era | Sole e Luna / Spada e Scudo / Scarlatto e Violetto / Mega | TCGdex |
| 9 | Età del set | mesi dall'uscita, a fasce (es. 0–3, 3–6, 6–12, 12–24, 24+): l'effetto non è lineare | data di uscita del set |
| 10 | Tipo di set | principale / speciale / sottoset (es. Trainer Gallery) / promo | TCGdex + tabella `set.csv` |
| 11 | Modalità di rilascio | busta / prodotto speciale (box, collezione) / evento o torneo / Pokémon Center / altro | tabella `rilasci.csv`, compilata in parte a mano |
| 12 | Diluizione | numero di carte della stessa rarità nel set (in logaritmo). **Tolta dal modello il 10/10/2026**: il peso usciva contrario alle attese e non riduceva l'errore in validazione. Resta calcolata nei dati | calcolata |
| 13 | Stamped | sì / no | nome e variante, `variants.wPromo` |

### 5.4 Altre variabili
| # | Variabile | Valori | Fonte |
|---|---|---|---|
| 14 | Esclusiva linguistica | in entrambe le lingue / **solo giapponese** / **solo internazionale** | TCGCSV categorie 3 e 85, disponibilità per lingua su TCGdex, tabella di corrispondenza (4.7) + mia correzione |
| 15 | Illustratore | i più frequenti come categorie proprie, gli altri in "altro" | TCGdex `illustrator` |
| 16 | Giocabile nel formato Standard | sì / no | TCGdex `legal.standard` |
| 17 | **Famiglia** | **carta da busta** / **promo e rilascio speciale** | Derivata da tipo di set (10), modalità di rilascio (11) e stamped (13). Promo, premi, carte in box o collezioni, Pokémon Center e stamped → "promo e rilascio speciale" |
| 18 | Lingua | internazionale / giapponese | Solo se le giapponesi hanno la stessa fonte di prezzo (4.7); altrimenti modello separato |

**Iconicità (variabile 2), come la calcoliamo:**
1. Il modello stima il **sovrapprezzo di ogni Pokémon** a parità delle altre caratteristiche (regolarizzato, così i Pokémon con poche carte non ottengono pesi estremi).
2. Dividiamo i Pokémon in tre livelli (alto / medio / basso) in base a quel sovrapprezzo.
3. Confrontiamo il risultato con la **mia lista** (`iconici.csv`). Mostrami le differenze e decido io i casi dubbi. **Fino alla conferma (9/10/2026)** si usa `iconici.csv` così com'è, in via provvisoria (gli 8 "da confermare" = alto).
4. Attenzione a non contare due volte lo stesso effetto: "Pokémon raffigurato" e "iconicità" sono collegate. Prova le due versioni (solo Pokémon, solo iconicità) e tieni quella che sbaglia meno.
5. **Decisione del 10 ottobre 2026:** nella regressione resta solo il **Pokémon raffigurato** (l'iconicità contava due volte lo stesso effetto). L'iconicità si usa **solo come filtro dei comparabili** (7.2) e nel giudizio d'investimento. I livelli si ricalcolano dai dati con `src/iconicita_dati.py` (sovrapprezzo del Pokémon rispetto al Pokémon medio: **alto ≥ +200%**, **medio da +75% a +200%**, almeno 8 carte) e li confermo io in `iconici.csv`.

### 5.5 Interazioni (combinazioni): sono fondamentali
Per me le **combinazioni** contano quanto le singole variabili: un **Pikachu promo esclusiva giapponese** vale più della somma di "Pikachu" + "promo" + "esclusiva". Un'interazione è un peso in più che si attiva solo quando due o tre caratteristiche sono presenti **insieme**.

**Combinazioni chiave** (da provare tutte, documentate in `variabili.md`):
- **iconicità × famiglia × esclusiva linguistica** (il caso "Pikachu promo esclusiva giapponese");
- **famiglia × rarità**: la rarità deve pesare molto per le carte da busta e poco per le promo;
- famiglia × iconicità;
- iconicità × rarità;
- iconicità × stamped;
- iconicità × modalità di rilascio;
- era × rarità.

**Come gestirle:**
1. **Conta le carte per combinazione** e mostramelo (es. "Pikachu + promo + solo giapponese: 23 carte"). Un peso stimato su poche carte è incerto.
2. **Interazioni esplicite** nella regressione per le combinazioni con abbastanza carte (indicativamente almeno 15–20).
3. **Regolarizzazione** per le combinazioni con poche carte: il peso viene "frenato" verso zero e cresce solo se i dati lo giustificano.
4. **Modello flessibile** (gradient boosting): trova le combinazioni da solo. Confronta il suo errore con quello della regressione **in particolare sulle carte con combinazioni chiave**.
5. **Comparabili**: i filtri per famiglia, iconicità e rilascio (7.2) fanno sì che una combinazione rara venga confrontata con carte della stessa combinazione. È la rete di sicurezza quando il modello ha pochi dati.
6. Nella scheda di valutazione, se la carta ha una combinazione con poche carte nel pool, **abbassa l'affidabilità** e scrivilo.

Le interazioni si tengono se riducono l'errore nella validazione incrociata. **Eccezione:** quelle della prima riga (iconicità × famiglia × esclusiva) si tengono comunque, regolarizzate, se ci sono almeno 15 carte, perché per me sono centrali. Mostrami sempre il loro effetto.

### 5.6 Effetti attesi (ipotesi per il controllo di buon senso)
Non sono pesi: sono le **direzioni che mi aspetto**. Se il modello trova il contrario, fermati e indaga.
- Iconicità alta, Pokémon come Charizard, Pikachu, Umbreon: **↑ forte**.
- Rarità illustration rare, special illustration rare, gold/hyper rispetto a holo rara: **↑ molto forte**.
- 1ª generazione, leggendario/misterioso, stamped: **↑**.
- **Promo di Pokémon iconici, soprattutto esclusive giapponesi** (es. Pikachu promo): **↑ forte anche senza rarità alta**. Se il modello non lo trova, è un segnale che manca qualcosa.
- Rilascio evento/torneo o Pokémon Center: **↑**. Prodotto speciale: **da scoprire**. Per me la modalità di rilascio ha importanza **medio-alta**: verifica se i dati lo confermano e dimmelo.
- Diluizione (più carte della stessa rarità nel set): **↓**.
- Ere e set più vecchi: **↑**, ma l'età potrebbe avere un effetto a "U" (prezzo alto all'uscita, calo, risalita quando il set esce di stampa).
- Giocabile in Standard: **↑ lieve**.
- Meccanica, variante, illustratore, esclusiva internazionale: **da scoprire**.
- Era ed età del set si sovrappongono: se il VIF lo conferma, tienine una sola.

### 5.7 Variabili escluse dalla regressione (e perché)
- **Popolazione PSA 10, popolazione PSA totale, copie in vendita su Cardmarket**: non le abbiamo per tutte le carte, quindi non si può stimarne il peso. Si usano nei comparabili e nel giudizio d'investimento (dati manuali, 4.3).
- **Tiratura ufficiale**: non è pubblica. La sostituiscono gli indizi della sezione 5.3.
- **Qualsiasi dato derivato dal prezzo** (es. "carta più cara del set"): il modello "barerebbe".
- **"Promo" separato da "tipo di set = promo"**: dicono la stessa cosa, se ne tiene una sola.
- **Famiglia (17)** riassume tipo di set, rilascio e stamped: nella regressione usala soprattutto **nelle interazioni** e controlla il VIF per non contare due volte lo stesso effetto.

## 6. Modello del prezzo equo

> **Obiettivo della valutazione (chiarito da Giacomo il 9 ottobre 2026).** Giacomo inserisce il **minimo NM di oggi** della carta (Cardmarket, filtri NM + lingua) e vuole sapere se la carta, **a quel prezzo di mercato, è sottovalutata, in linea o sopravvalutata rispetto a carte simili**: è un supporto alla valutazione per investimento (potenziale di crescita), non la valutazione di una singola offerta.
> 1. **Valore secondo le carte simili** = mediana dei comparabili rettificati (7.3). Il prezzo NM di ogni comparabile è quello inserito da Giacomo, se c'è (riusato con il rapporto NM/trend, 7.0.6); altrimenti è **stimato in automatico** dal suo trend × rapporto NM/trend tipico, e la scheda lo dichiara. Giacomo può sempre correggerlo.
> 2. **Giudizio relativo**: il minimo NM della carta (centro della fascia +5%) confrontato con quel valore. L'intervallo "in linea" non è ±15%: è la **fascia centrale reale** (25°–75° percentile) dello scarto tra le carte e le loro simili, misurata su tutto il pool (circa ±30–40%), perché tra carte con le stesse caratteristiche il prezzo varia molto. Sotto la fascia = **sottovalutata**, sopra = **sopravvalutata**.
> 3. **Modello** = seconda opinione dello stesso confronto (valore delle caratteristiche).
> 4. **Validazione**: accanto al giudizio la scheda mostra il risultato del mini-storico a 30 giorni (8.3). Al 9/10/2026: le carte più sottovalutate (primo quinto) sono salite in media del +6,0% contro +1,6% del mercato, con crescita mediana 0% e correlazione debole (−0,06). È un **segnale debole e non validato**: indizio di potenziale di crescita, non previsione.
> 5. La soglia ±15% della sezione 6 resta l'obiettivo per l'errore del modello, ma **non blocca il giudizio relativo**, che dichiara sempre la propria incertezza.
> 6. Le carte **senza prezzo Cardmarket** (promo SM-P e S-P, catalogo giapponese) funzionano allo stesso modo, ma servono i prezzi NM inseriti a mano per le carte simili che non hanno trend.


1. **Dati di addestramento**:
   - carte singole con prezzo Cardmarket valido;
   - escludi le carte "bulk": **soglia decisa l'8/10/2026: 3 €** (decisione D3; con 15 € restavano solo ~900 varianti, sotto il minimo di 1.500–2.500) sul prezzo di riferimento (`soglia_bulk_eur` in `config.json`). Le carte sotto soglia restano nella fotografia ma non entrano nell'addestramento; la scheda di una carta sotto soglia deve dirlo ("sotto la soglia del modello");
   - escludi i prezzi palesemente anomali, segnalandoli.
2. **Modello base**: regressione multipla su `log(prezzo)`, con le variabili della sezione 5 e le interazioni della 5.5.
   - Le variabili a categorie si codificano con una **categoria di riferimento**; dimmi sempre quale è. **Rarità: riferimento "illustration rare"** (decisione del 9/10/2026: la holo rara da busta è fuori perimetro; i sovrapprezzi di rarità si leggono rispetto a una IR).
   - Peso → sovrapprezzo: `(e^b − 1) × 100`. Mostra ogni sovrapprezzo con il suo **intervallo di confidenza**.
   - Circa **10–20 carte per ogni peso** stimato: accorpa in "altro" le categorie con meno di ~30 carte.
   - Usa la **regolarizzazione** (es. ridge) per stabilizzare i pesi delle categorie con poche carte, e una **versione robusta** meno sensibile ai prezzi anomali. Confronta i risultati.
   - Controlla le **variabili che si sovrappongono** (VIF) e segnalamele.
   - **Selezione delle variabili** solo con la validazione incrociata: una variabile resta se riduce l'errore, non perché "sembra significativa".
   - **Controllo di buon senso**: mostrami la tabella dei sovrapprezzi. Se un peso va contro la logica del mercato (es. "special illustration rare" che vale meno di "holo rara"), fermati e indaga prima di andare avanti.
3. **Confronto** (con la validazione incrociata), tenendo l'impostazione che **sbaglia meno**, sempre con la spiegazione dei fattori:
   - un modello unico con le interazioni della 5.5;
   - **due modelli separati**, uno per famiglia (carte da busta / promo e rilasci speciali);
   - un modello più flessibile (es. gradient boosting), che trova da solo le combinazioni.
   - Riporta l'errore tipico **per famiglia** e **per lingua**: le promo potrebbero essere più difficili da stimare.
4. **Validazione incrociata** (il modello stima carte che non ha visto):
   - riporta l'errore tipico in % (es. "±25%");
   - riportalo anche per fascia di prezzo e per tipo di carta.
5. **Intervallo**: per ogni carta un **prezzo equo con intervallo** (es. 10°–90° percentile dell'errore).
6. **Spiegazione**: il contributo di ogni caratteristica in % (es. "Pikachu: +60%", "promo: +25%").
7. **Quando si addestra:**
   - **la prima volta nel blocco 4, insieme a me**: guardiamo pesi, errori e carte di controllo prima di usare il modello;
   - **poi in automatico ogni settimana** (GitHub Actions), sulla fotografia più recente, senza che io debba fare nulla;
   - **controlli automatici prima di pubblicare i nuovi pesi**: se l'errore peggiora di oltre il 20%, se un peso importante cambia segno o varia di oltre il 50%, o se le carte di controllo peggiorano molto, **non pubblicare**, tieni i pesi della settimana prima e mandami una notifica con il motivo;
   - salva lo storico dei pesi (`modelli/AAAA-Wnn.json`), così vediamo come cambia il valore delle caratteristiche nel tempo.
8. **Carte di controllo** (`carte_controllo.csv`):
   - 15–20 carte che conosco bene, scelte insieme, con il link e i **prezzi di mercato Near Mint nella lingua giusta**: **offerta minima** (il sistema ne ricava la fascia +5%, 4.5c) e, se disponibile, la **mediana delle ultime 3 vendite NM su eBay**. Nessun "prezzo personale": contano solo prezzi di mercato verificabili;
   - colonne: `nome, set, numero, lingua, rarita_o_tipo, link_cardmarket, nm_offerta_min_eur, ebay_venduti_mediana3_eur, data, note`;
   - devono includere combinazioni chiave, es. promo giapponesi di Pokémon iconici. Al 8/10/2026 ne mancano ancora di **gold/hyper**, **shiny** e **stamped**: aggiungerle prima del blocco 4;
   - **non servono per l'addestramento**: servono per verificarlo. A ogni training mostra, uno accanto all'altro: stima del modello (calibrata), fascia NM, prezzo di riferimento Cardmarket (`trend`) e scarto in %.
   - L'eBay venduto si usa **solo come confronto a mano** nelle carte di controllo, mai nell'addestramento (4.4).

**Soglia di affidabilità (decisa l'8 ottobre 2026): errore massimo ±15%** per tutte le carte e tutte le fasce di prezzo (es. su una carta da 20 € l'errore tipico non deve superare ±3 €).
- Misurala con la validazione incrociata **per famiglia, lingua e fascia di prezzo** (<10 €, 10–50 €, 50–200 €, >200 €).
- Dove il modello **supera il 15%**, la scheda **non usa il prezzo equo del modello** per il giudizio: scrive "modello poco affidabile per questo tipo di carta" e si basa **solo sui comparabili con prezzi NM**.
- La stessa soglia vale per i comparabili: se l'intervallo tra i comparabili rettificati è più largo di ±15% intorno alla mediana, il giudizio di prezzo è "❔ Dati insufficienti" e la scheda mi suggerisce di aggiungere o controllare comparabili.
- **Attenzione:** è una soglia severa. È possibile che il modello sul prezzo di riferimento non la raggiunga in tutti i segmenti. Dopo il blocco 4 mostrami in quali segmenti la rispetta e in quali no, e cosa si potrebbe migliorare.
- Riporta soglia e risultati nella pagina "Il modello".

**Giudizio di prezzo:**
- 🟢 **Sottovalutata**: prezzo sotto l'intervallo;
- ⚪ **In linea**: dentro l'intervallo;
- 🔴 **Sopravvalutata**: sopra l'intervallo;
- ❔ **Dati insufficienti**: pochi comparabili o caratteristiche incerte.

## 7. Comparabili rettificati

### 7.0 Flusso principale di valutazione (deciso l'8 ottobre 2026)
Il prezzo di riferimento automatico non distingue condizione e lingua (4.5b). Per questo la valutazione di una carta usa **prezzi Near Mint inseriti da me**:
1. Inserisco la carta da valutare.
2. Il sistema trova da solo le **5–8 carte più simili** (regole in 7.2) e per ognuna mostra:
   - foto, nome, set, numero, lingua;
   - variabili in comune ✓ e differenze ✗;
   - **link di ricerca su Cardmarket** (filtrato Near Mint + lingua, se possibile) e **link alle vendite concluse su eBay**;
   - una **casella per l'offerta minima Near Mint** (la fascia +5% compare sotto, calcolata, 4.5c), oppure per la mediana eBay se scelgo quel tipo di prezzo, con fonte, data ed eventuale nota.
3. Inserisco anche il **prezzo Near Mint della carta da valutare** (l'offerta che sto guardando).
4. **Calcolo:**
   - ogni comparabile viene **rettificato** verso la carta valutata con i pesi del modello, **interazioni comprese**. Esempio: "Pikachu promo" a 40 € → + esclusiva giapponese → + full art → + peso della combinazione = stima per la mia carta;
   - la **mediana** dei comparabili rettificati è il **valore secondo le carte simili** (vedi il riquadro all'inizio della sezione 6); l'intervallo è la fascia centrale reale degli scarti nel pool;
   - il prezzo equo del modello (sul prezzo di riferimento, calibrato con 4.5b) si mostra come **seconda opinione**. Se le due stime differiscono di oltre il 30%: avviso;
   - **giudizio di prezzo** (sottovalutata / in linea / sopravvalutata) confrontando il mio prezzo NM con il prezzo equo NM;
   - **giudizio d'investimento** (sezione 8).
5. **Regole sui prezzi manuali:**
   - **stesso tipo di prezzo per tutte le carte** di una valutazione (tutte "minimo NM Cardmarket +5%" oppure tutte "mediana delle ultime 3 vendite NM su eBay"). Se mescolo tipi diversi, avvisami;
   - nota da mostrare accanto alle caselle: "la fascia corregge il fatto che il minimo spesso non è davvero NM"; per eBay, meglio la **mediana delle ultime 3 vendite** NM nella stessa lingua che una vendita singola;
   - servono **almeno 3 comparabili con prezzo**, altrimenti "❔ Dati insufficienti";
   - prezzi più vecchi di **30 giorni**: avvisami e chiedimi se aggiornarli.
6. **I prezzi che inserisco si salvano** in `dati_manuali.csv` (carta, offerta minima, fascia calcolata con le percentuali di quel giorno, lingua, condizione, fonte, data) **insieme al `trend` automatico di quel giorno**, e si **riusano senza invecchiare**:
   - per ogni prezzo manuale calcola il **rapporto NM / trend** di quel giorno, sul punto centrale e sui due estremi della fascia (es. "la copia NM in italiano costava il 15% più del trend");
   - il rapporto cambia molto più lentamente del prezzo. Quando la carta torna come comparabile, la casella si precompila con **rapporto × trend di oggi**, cioè un prezzo NM aggiornato in automatico;
   - mostra sempre che è un valore **aggiornato con il trend**, la data del prezzo originale e il prezzo originale;
   - rapporto più vecchio di **90 giorni**: chiedimi di reinserire il prezzo;
   - con tanti rapporti salvati, stima lo **scarto NM tipico** per famiglia, lingua e fascia di prezzo, e usalo per le carte che non ho mai prezzato (sostituisce e migliora la calibrazione della 4.5b).
7. **Da dove vengono i pesi:** dal modello addestrato sul pool di migliaia di carte (sezione 6). Pochi prezzi manuali non bastano per stimare tanti pesi. Quando avrò accumulato **almeno 200–300 prezzi NM manuali**, verifica se i sovrapprezzi stimati sul pool valgono anche sui prezzi NM e mostrami le differenze.

### 7.1 Da dove vengono
- Dalla **fotografia del mercato** più recente (sezione 9): le stesse carte, lo stesso giorno e lo stesso prezzo (`trend` Cardmarket) usati per il modello.
- Per ogni comparabile: foto ufficiale, nome, set, numero e **link di ricerca su Cardmarket** (link normale, senza leggere la pagina in automatico).
- La carta valutata **non** è mai tra i propri comparabili.
- Comparabili **sempre sulla stessa fonte di prezzo** della carta valutata (4.7).

### 7.2 Come si sceglie (decisioni dell'8 ottobre 2026)
1. **Filtri obbligatori, diversi per famiglia** (variabile 17). La candidata deve essere della **stessa famiglia** e avere uguali:
   - **carte da busta**: stessa **fascia di rarità** + stesso **livello di iconicità**;
   - **promo e rilasci speciali**: stessa **modalità di rilascio** + stesso **livello di iconicità**. Qui la rarità conta poco: entra solo nel punteggio di somiglianza.
2. **Punteggio di somiglianza 0–100%** su tutte le altre variabili della sezione 5, con la distanza di Gower: categorie uguali = 1, diverse = 0; numeri più vicini = più simili.
   - Pesi della somiglianza = **importanza delle variabili stimata dal modello**. Per ora nessun peso imposto a mano: rivediamo più avanti, guardando i risultati, se la modalità di rilascio deve contare di più.
   - **Era ed età del set: peso basso.** Una carta recente può essere molto simile a una di qualche era fa. La differenza di prezzo dovuta all'età la corregge la **rettifica** (7.3); il suo effetto nel tempo lo valuta il giudizio d'investimento.
   - **Stessa lingua (decisione del 9/10/2026):** la lingua è un **filtro obbligatorio**. Solo se nella stessa lingua restano meno di 3 comparabili si usano carte dell'altra lingua, **convertite con lo spread misurato** tra inglese e giapponese (coppie con stessa specie, illustratore e rarità; al 9/10: la giapponese costa circa il 47% dell'inglese, IR 41%, SIR 64%, gold 73%, promo ×2,25), e la scheda lo dichiara.
   - **Espansione (decisione del 9/10/2026):** l'espansione è una variabile del modello (set con almeno 15 carte) e conta nella somiglianza ("stessa espansione"), con il peso stimato dal modello come le altre variabili.
   - **Modo di rilascio da Bulbapedia (decisione del 9/10/2026, sostituisce la classificazione a mano):** per **tutte** le promo (SM, SWSH, SVP, MEP e giapponesi SM-P, S-P, SV-P, M-P; 2.128 carte) il modo di rilascio viene dalla colonna "Promotion" delle liste di Bulbapedia (`fonti/*.html`, `src/rilasci_bulbapedia.py` → `tabelle/rilasci_bulbapedia.csv`), qualunque sia il prezzo, quindi **si usa anche nel modello** (nessun indizio di prezzo). Categorie: Pokémon Center · evento o torneo · prodotto speciale · **campagna d'acquisto** (carte in regalo comprando buste/box o videogiochi, Friendly Shop, Lawson…) · altro (riviste, film, McDonald's, mostre e collaborazioni come Munch e Van Gogh) · da classificare. `tabelle/rilasci_manuali.csv` vale solo dove Bulbapedia non ha la carta.
   - **Modo di rilascio delle promo (decisione del 9/10/2026):** `tabelle/rilasci_manuali.csv` contiene le promo sopra 20 € classificate con ricerche web (fonte e affidabilità per ogni riga; 84 su 121, le altre vuote perché senza fonte). Queste classificazioni si usano **solo per la scheda e per scegliere i comparabili**. Il **modello** usa solo le regole automatiche (timbri, nomi TCGplayer), perché classificare solo le promo care renderebbe "da classificare" un indizio di prezzo (vietato, sezione 14).
   - **Gemella nell'altra lingua:** se la stessa illustrazione esiste nell'altra lingua, la scheda mostra il suo prezzo e lo confronta con lo spread tipico (indizio di potenziale).
   - **Finitura holo (decisione del 9/10/2026):** holo / non holo conta nel punteggio di somiglianza con un peso alto, ma **non è un filtro obbligatorio**.
3. Si confronta con **tutte** le carte che passano i filtri e si mostrano le **5–8 più simili** (sono io a inserirne i prezzi, quindi non troppe).
4. **Se i filtri lasciano meno di 3 comparabili** sopra il 70% di somiglianza:
   - allenta **solo il livello di iconicità**. La famiglia non cambia mai, e restano fissi la rarità per le carte da busta e la modalità di rilascio per le promo;
   - **scrivi chiaramente** nella scheda quale filtro è stato allentato;
   - se non basta, il giudizio è "❔ Dati insufficienti".

### 7.3 Rettifica del prezzo
- Ogni comparabile si corregge per le differenze con la carta valutata, usando i sovrapprezzi del modello.
  - Esempio: comparabile a 90 €, unica differenza iconicità media invece di alta (+40%) → 90 × 1,40 ≈ 126 €.
- Mostra il prezzo **originale** e **rettificato** e la **mediana dei rettificati**: è un secondo prezzo equo.
- Se modello e mediana dei comparabili differiscono di oltre il 30%: avviso "qualcosa non è catturato dalle variabili".

### 7.4 Cosa mostra la scheda per ogni comparabile
- percentuale di somiglianza;
- caratteristiche in comune (✓) e differenze (✗);
- prezzo originale e rettificato;
- foto e link.

**Avviso "Poco affidabile" (deciso il 10 ottobre 2026).** Accanto al giudizio compare l'etichetta gialla "Poco affidabile", con il motivo, quando:
- le carte simili vanno corrette in media più di **×2** (o ÷2): sono troppo diverse dalla carta valutata;
- ci sono meno di 3 carte simili con una correzione calcolabile;
- servono carte dell'altra lingua, convertite con lo spread medio.
- lo scarto tra il minimo NM e il valore delle simili è più grande di quello di 9 carte su 10 del mercato (oltre il 10° o il 90° percentile): spesso la carta ha qualcosa di speciale che le variabili non vedono (es. Pikachu Van Gogh, Umbreon Gold Star).
Un tetto alle correzioni è stato provato (×5, ×3, ×2, ×1,5) e non migliorava i risultati: per questo si avvisa invece di correggere.

### 7.5 Dati di scarsità dei comparabili
- Quando valuto una carta, la pagina **mi chiede** popolazione PSA 10, popolazione PSA totale e copie in vendita su Cardmarket **anche per i comparabili**:
  - mostra per ognuno i **link di ricerca PSA e Cardmarket**;
  - io leggo i numeri e li scrivo.
- I numeri restano **salvati** e si riusano nelle valutazioni successive:
  - file `dati_manuali.csv` nel repository, con la data di inserimento;
  - salvataggio con lo stesso meccanismo sicuro della sezione 11; nel frattempo restano nel browser.
- Mostra la data di ogni dato e avvisami se ha più di 90 giorni.
- Il confronto di scarsità (es. "PSA 10: 120 copie contro una mediana di 480 dei comparabili") si fa solo con **almeno 3 comparabili** che hanno il dato. Altrimenti scrivi "dati di scarsità insufficienti".

## 8. Giudizio d'investimento (fondamentale)

### 8.1 Componenti
1. **Valutazione relativa**: scostamento dal prezzo equo (sezione 6).
2. **Andamento recente**: `trend` rispetto ad `avg30`, `avg7` rispetto ad `avg30`, cioè il movimento dell'ultimo mese.
3. **Fattori strutturali**: età e probabile fuori stampa, iconicità, esclusività, rarità e diluizione, modalità di rilascio.
4. **Scarsità** (dati manuali): popolazione PSA 10 e copie in vendita rispetto ai comparabili.
5. **Rischio e liquidità**: distanza tra `low` e `trend`, numero di comparabili, volatilità quando disponibile.

### 8.1b Pesi iniziali (decisi l'8 ottobre 2026, da rivedere più avanti)
| Componente | Peso | Sotto-componenti (proposta) |
|---|---|---|
| Valutazione relativa | 35% | sconto rispetto al prezzo equo e alla mediana dei comparabili rettificati |
| Fattori strutturali | 30% | età / probabile fuori stampa 7,5% · iconicità 7,5% · rilascio limitato 7,5% · diluizione bassa 7,5% |
| Scarsità (dati manuali) | 20% | popolazione PSA 10 rispetto ai comparabili 10% · copie in vendita su Cardmarket rispetto ai comparabili 10% |
| Andamento dell'ultimo mese | 15% | `trend` e `avg7` rispetto ad `avg30`. Regola iniziale: salita moderata = positivo; picco improvviso = prudenza |
| Rischio | penalità fino a −15 punti (proposta) | prezzi molto dispersi (`low` molto sotto `trend`), pochi comparabili, set uscito da meno di 3 mesi |

**Soglie del giudizio (proposta):** 🟢 Interessante ≥ 65 · ⚪ Neutro 40–64 · 🔴 Sconsigliato < 40 · ❔ Dati insufficienti se mancano prezzo equo o comparabili.

- Se mancano i dati manuali di scarsità, ridistribuisci il loro 20% sugli altri componenti in proporzione e **dichiaralo** nella scheda.
- Ogni componente va trasformato in un punteggio 0–100 confrontabile, ad esempio con il **percentile** tra le carte simili. Spiegami come prima di implementarlo.
- Questi pesi sono **dichiarati, non validati**: in dashboard lo stato è "non ancora validato" finché la sezione 8.4 non li sostituisce con pesi stimati dai dati.
- Li rivedremo insieme più avanti: tienili in `config.json`, facili da cambiare.

### 8.2 Risultato
- **Punteggio d'investimento 0–100** e giudizio: 🟢 Interessante / ⚪ Neutro / 🔴 Sconsigliato / ❔ Dati insufficienti.
- **Pro e contro**, in 3–5 punti con numeri.
- **Orizzonte** a cui si riferisce: da concordare con me (es. 6–12 mesi).
- **Stato di validazione, sempre visibile**:
  - "Non ancora validato": i pesi sono regole dichiarate;
  - "Verificato sul mini-storico a 30 giorni" (8.3);
  - "Verificato su N giudizi passati" (8.4).

### 8.3 Validazione subito: mini-storico a 30 giorni
- Stima il modello del prezzo equo usando `avg30` come prezzo ("com'era circa un mese fa").
- Controlla se le carte che risultavano sottovalutate sono poi salite più delle altre verso il `trend` attuale.
- È un test grezzo: `avg30` è una media, non un prezzo puntuale, e copre un solo mese. **Dichiaralo.** Ma è il primo controllo basato sui dati, disponibile dal primo giorno.

### 8.4 Validazione nel tempo: registro dei giudizi
- Ogni giudizio emesso si salva in `docs/data/registro_giudizi.csv`: data, carta, prezzo, prezzo equo, punteggio, componenti.
- Dopo 3, 6 e 12 mesi confronta i giudizi con i prezzi reali, sulle fotografie di mercato salvate (sezione 9):
  - le carte "Interessanti" hanno fatto meglio di quelle "Neutre" e del mercato?
  - riporta tasso di successo, rendimento mediano e numero di casi.
- Quando ci sono abbastanza casi, **i pesi del punteggio si stimano dai dati** al posto delle regole iniziali. Mostrami sempre il prima e il dopo.
- Opzione: backtest immediato con uno storico a pagamento (4.5), solo con il mio ok.

### 8.5 Testo fisso nella dashboard
*"Valutazioni e giudizi sono stime statistiche con margine di errore, basate su dati di mercato e su carte simili: non sono certezze né consulenza finanziaria."*

## 9. Dati salvati e monitoraggio

- **Fotografia del mercato**:
  - **settimanale**: tutte le carte sopra la soglia, con prezzi Cardmarket e campi TCGplayer utili;
  - salvala compressa (Parquet), con **un file per settimana** (es. `data/mercato/2026-W41.parquet`);
  - controlla la dimensione: deve restare piccola (pochi MB a settimana al massimo);
  - serve per il riaddestramento e per verificare i giudizi.
- **Monitoraggio giornaliero** delle carte che aggiungo (`watchlist.csv`):
  - prezzo da quando la inserisco;
  - grafico;
  - segnali (ribasso, rialzo, stabile da N giorni, obiettivo di prezzo raggiunto).
- **Attenzione:** GitHub rifiuta file oltre 100 MB e non è fatto per molti GB. Se lo spazio cresce troppo, proponimi un'alternativa prima che diventi un problema.

`watchlist.csv`: una riga per carta salvata. Colonne:
- `id`, `tcgdex_id`, `nome`, `set`, `numero`, `variante`, `lingua`;
- `link_cardmarket`, `data_inserimento`;
- `prezzo_obiettivo_eur`, `prezzo_vendita_obiettivo_eur`;
- dati manuali: `psa10_pop`, `psa_pop_totale`, `copie_cardmarket`, `data_dati_manuali`;
- correzioni manuali: `promo`, `stamped`, `esclusiva_lingua`, `iconico`, `rilascio`;
- `attivo`, `note`.

## 10. Dashboard (`docs/index.html`, su GitHub Pages)

**Riferimento obbligatorio: `riferimenti/mockup-dashboard.html`, versione approvata il 9 ottobre 2026** (stile minimal, fascia NM calcolata dal minimo). Sostituisce la versione dell'8 ottobre. La dashboard vera deve seguirlo:
- **stessa struttura**: barra in alto con le tre sezioni "Valuta una carta", "Monitorate", "Il modello";
- **stesse sezioni e stesso ordine** dentro ogni schermata. In "Valuta una carta": ricerca con candidati → scheda carta con caratteristiche → **riquadro del prezzo equo NM** con il giudizio di prezzo e la **barra dell'intervallo** (fascia, tacca della mediana, pallino della mia offerta) → sotto, **riquadro investimento** con componenti e "Perché" → prezzi Near Mint con la mia carta e i comparabili → avvertenza e "Aggiungi al monitoraggio";
- **stesso stile**:
  - token di stile (colori, raggi, caratteri) in `:root`, in cima al file;
  - sfondo bianco, testo nero;
  - **Outfit** per titoli e numeri grandi, **Atkinson Hyperlegible** per il testo;
  - angoli medi: riquadri 16–18 px, pulsanti e caselle 10–12 px; solo le etichette delle caratteristiche sono a pillola;
- **regola dei colori**: nero per tutto ciò che è neutro (barre, grafici, pulsanti principali); verde e rosso solo per gli esiti; giallo solo per gli avvisi da notare. Barre e grafici sempre in un solo colore. **Eccezione (9/10/2026):** il pallino rosso del logo resta (è il marchio); i link al passaggio del mouse non diventano rossi;
- **accessibilità**: testo con contrasto almeno 4,5:1; bordi di caselle e pulsanti almeno 3:1; contorno nero visibile quando si usa la tastiera; pulsanti alti almeno 44 px;
- **stesso comportamento** del calcolo nella scheda: si aggiorna appena inserisco o cambio un prezzo NM, con le regole delle sezioni 6 e 7 (almeno 3 comparabili, dispersione massima ±15%).

Nel mockup:
- **tutti i numeri sono dati di esempio inventati**: vanno sostituiti con i dati reali, e l'etichetta "Dati di esempio" va tolta;
- i **riquadri grigi** sono segnaposto per le **foto ufficiali** delle carte (TCGdex);
- i link a Cardmarket ed eBay sono generici: nel sito vero devono aprire la ricerca della carta specifica (4.5b punto 5).

Puoi migliorare dettagli tecnici (accessibilità, prestazioni, versione mobile), ma **ogni cambiamento visibile di struttura o stile va proposto e approvato da me prima**.

- **Stile**: vedi sopra (sfondo bianco, testo nero, regola dei colori). Foto reali delle carte.
- **Mobile first**: deve funzionare bene su iPhone.
- **Non indicizzata** dai motori di ricerca.
- **Valutazione istantanea**: ogni settimana precalcola per tutte le carte del modello prezzo equo, intervallo, comparabili e componenti del giudizio, in un file JSON compresso. La dashboard li legge senza server: cerco una carta e vedo subito la scheda, anche da iPhone. I dati manuali che inserisco si applicano nel browser.

**"Valuta una carta":**
- ricerca per nome con **foto**, oppure incolla un **link Cardmarket**: ricava set e nome **dal testo del link, senza aprire la pagina**;
- se ci sono più candidati, mostrali con foto.

**Scheda di valutazione:**
- foto, nome, set, caratteristiche;
- prezzo attuale e **prezzo equo con intervallo**;
- giudizio di prezzo;
- **giudizio d'investimento** con punteggio, pro e contro, orizzonte, stato di validazione;
- **comparabili rettificati** con link;
- caselle per i **prezzi Near Mint** della carta e dei comparabili (7.0), e per PSA 10 e copie in vendita;
- pulsante **"Aggiungi al monitoraggio"**.

**Sezione "Monitorate":** grafico dal giorno di inserimento, segnali, obiettivi.

**Pagina "Il modello":**
- errore tipico;
- sovrapprezzi per caratteristica (es. quanto vale "iconico", "promo", "esclusiva giapponese");
- risultati delle validazioni.

È utile anche per il portfolio.

## 11. Aggiunta al monitoraggio e notifiche

- **Aggiunta al monitoraggio** dalla dashboard e da iPhone (Comando Rapido "Condividi → Valuta carta"), in modo **sicuro**:
  - la dashboard è pubblica, quindi **nessuna chiave dentro la pagina**;
  - usa una issue GitHub precompilata, accettata solo se aperta da me;
  - oppure un token "fine-grained" limitato a questo repository e con scadenza, salvato solo nel Comando Rapido;
  - proponimi la soluzione più semplice e spiegami come revocare il token.
- **Notifiche ntfy** sull'iPhone:
  - nome del canale lungo e casuale, nel Secret `NTFY_TOPIC`;
  - un riepilogo al giorno solo se c'è qualcosa di rilevante;
  - avviso separato per obiettivi raggiunti e per aggiornamenti falliti.

## 12. Automazione (GitHub Actions)

- **Settimanale**: fotografia del mercato, riaddestramento, precalcolo delle valutazioni.
- **Giornaliero**: prezzi delle carte monitorate, segnali, notifiche.
- Avvio manuale disponibile (`workflow_dispatch`).
- **Attenzione:** l'orario dei workflow è in **UTC** (06:30 UTC = 8:30 italiane con l'ora legale, 7:30 con l'ora solare).
- Chiavi solo nei **GitHub Secrets**, mai nel codice, nei log o nella dashboard.
- Se un workflow fallisce: notifica ntfy e avviso in dashboard.
- **Attenzione:** nei repository pubblici i workflow programmati si disattivano dopo 60 giorni senza attività. Verifica che i commit automatici bastino.

## 13. Fasi di lavoro

0. **Prima di iniziare** (Principiante): cartella, app Claude, account GitHub.
1. **Fotografia del mercato** (Intermedio):
   - scarica da TCGdex le carte con prezzo Cardmarket e le caratteristiche di base;
   - per il modello tieni solo le carte del **perimetro della sezione 2** (promo + rarità speciali, dal 2017), ma salva nella fotografia anche le altre: potranno servire per le estensioni;
   - **mostrami quante carte ci sono per ogni rarità del perimetro e per le promo**: se il totale è troppo basso per stimare i pesi (indicativamente meno di 1.500–2.500 carte), dimmelo e proponimi come ampliarlo;
   - filtra il bulk;
   - **verifica la fonte dei prezzi giapponesi** (4.7) e mostrami quante carte giapponesi hanno un prezzo Cardmarket;
   - mostrami un riepilogo: quante carte, quali set, distribuzione dei prezzi, quante carte per famiglia e per lingua.
2. **Online e raccolta automatica** (Intermedio): GitHub, GitHub Pages, workflow settimanale della fotografia. **Va fatto presto**: ogni settimana di ritardo è una fotografia in meno per la validazione.
3. **Caratteristiche delle carte** (Intermedio/Avanzato):
   - tutte le variabili della sezione 5, documentate in `variabili.md`;
   - tabelle `rarita.csv`, `set.csv`, `rilasci.csv`, `iconici.csv`: mostrami ognuna prima di usarla (le prime tre **approvate il 10/10/2026**);
   - mostrami i casi incerti e quante carte ci sono per ogni valore di ogni variabile.
4. **Modello del prezzo equo** (Avanzato): regressione, interazioni, validazione incrociata, confronto con un modello flessibile, sovrapprezzi per caratteristica. Mostrami i risultati prima di andare avanti.
5. **Comparabili e scheda di valutazione** (Avanzato): comparabili rettificati, "Valuta una carta" (ricerca con foto, link Cardmarket), dati manuali, precalcolo settimanale.
6. **Giudizio d'investimento** (Avanzato): componenti (8.1), punteggio, pro e contro, mini-storico a 30 giorni (8.3), registro dei giudizi (8.4).
7. **Monitoraggio e notifiche** (Intermedio): watchlist, aggiunta sicura da dashboard e iPhone, grafico dal giorno di inserimento, notifiche ntfy.
8. **Verifica nel tempo** (Avanzato, dopo 3–6 mesi di fotografie): confronto dei giudizi con i prezzi reali, stima dei pesi dai dati, aggiornamento del punteggio.
9. **Estensioni** (più avanti): sigillati, gradate, carte Allenatore, vintage (prima del 2017), lingue italiana e cinese, storico a pagamento (solo con il mio ok), README e pagina "Il modello" per il portfolio.

Non passare alla fase successiva finché la precedente non funziona e non me l'hai fatta verificare.

## 14. Cose da non fare

- Non inventare prezzi, popolazioni o dati mancanti.
- Non fare scraping di siti che lo vietano.
- Non usare variabili derivate dal prezzo per stimare il prezzo.
- Non presentare il giudizio d'investimento come validato se non lo è.
- Non presentare stime come certezze.
- Non scrivere chiavi, token o nomi dei canali nel codice, nei log o nella dashboard.
- Non cancellare né riscrivere le fotografie del mercato e il registro dei giudizi.
- Non usare comandi git distruttivi.
