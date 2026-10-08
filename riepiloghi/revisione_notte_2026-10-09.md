# Revisione del lavoro notturno · 9 ottobre 2026

Lavoro autorizzato da Giacomo la notte del 9/10: **bozza dei blocchi 3, 4 e 5**, da rifinire insieme.
**Niente è "approvato"** finché non lo confermi. Tutto è salvato su GitHub (`main`).

## 1. Cosa trovi stamattina

| Blocco | Stato | Dove guardare |
|---|---|---|
| 3 · Caratteristiche | ✅ bozza completa: 18 variabili su tutte le carte, tabelle di conversione, catalogo giapponese | `riepiloghi/blocco3_2026-W41.md`, `variabili.md`, `tabelle/` |
| 4 · Modello del prezzo equo | ✅ bozza: 7 modelli confrontati, sovrapprezzi con intervalli, controllo di buon senso | `riepiloghi/blocco4_2026-W41.md`, `modelli/2026-W41.json` |
| 5 · Comparabili e scheda | ✅ bozza **online**: ricerca con foto, scheda, comparabili rettificati, prezzi NM, calcolo dal vivo | **https://rossigiacomo47.github.io/pokemon-price-tracker/** (etichetta gialla "Bozza da rifinire") |
| 6 · Investimento, 7 · Monitoraggio | non iniziati (segnaposto nella pagina) | — |

**Prova dall'iPhone (5 minuti):**
1. Cerca "charizard ex 199" e apri la scheda.
2. Inserisci 3 minimi NM nelle caselle delle carte simili e la tua offerta.
3. Guarda come si aggiornano il prezzo equo, il giudizio e la barra dell'intervallo.

I prezzi che inserisci restano **solo sul tuo telefono**: il salvataggio su GitHub arriva nel blocco 7.

## 2. Le cose importanti (in ordine di importanza)

### 2.0 ⚠️⚠️ La scoperta più importante: la soglia ±15% sembra irraggiungibile, anche con i comparabili

Prima di chiudere ho fatto due prove in più, sul prezzo di riferimento Cardmarket, l'unico disponibile per tutte le carte.

**Prova A: cambiare il prezzo o la soglia del modello**

| Prova | Errore tipico, lineare | Errore tipico, flessibile |
|---|---|---|
| Attuale: trend, carte ≥ 3 € | ±50% | ±44% |
| Media a 30 giorni, ≥ 3 € | ±49% | ±43% |
| Trend, ≥ 10 € | ±51% | ±42% |
| Media a 30 giorni, ≥ 10 € | ±48% | ±40% |
| Trend, ≥ 10 €, solo carte da busta | ±47% | ±42% |

**Prova B: il metodo dei comparabili**, simulato usando il trend al posto dei tuoi prezzi NM

| Regola | Carte in cui i comparabili "concordano" | Errore tipico, tutte le carte | Errore tipico quando concordano |
|---|---|---|---|
| 8 più simili, dispersione massima ±15% (regola attuale) | **0%** (2 carte su 3.428) | ±48% | ±20% |
| 3 più simili, dispersione massima ±15% | 4% | ±48% | ±32% |
| 3 più simili, dispersione "interquartile" ±15% | 21% | ±48% | ±35% |

**Cosa vuol dire:** due carte con le stesse caratteristiche (stessa rarità, stesso Pokémon, stesso tipo di rilascio…) possono costare l'una il doppio dell'altra, per l'illustrazione, la popolarità o la storia della carta. Né il modello né i comparabili riescono a scendere sotto il ±40%. Con la regola attuale (8 comparabili entro ±15%) la scheda direbbe **quasi sempre "Dati insufficienti"**.

**Attenzione:** con i tuoi prezzi NM le cose potrebbero andare un po' meglio, perché il trend è "sporco" (gradate, lingue). Lo vedremo solo provando su qualche carta vera. L'eterogeneità tra le carte però resta.

**Da decidere insieme (è il punto principale di stamattina):**
- **A.** Tenere ±15% come obiettivo, ma mostrare sempre un intervallo **onesto** (per esempio ±40%) e il giudizio solo quando la tua offerta è chiaramente fuori dall'intervallo;
- **B.** Cambiare la regola di dispersione dei comparabili: le 3–5 più simili, con una misura meno severa, accettando che l'errore sia di ±30–35%;
- **C.** Investire su variabili che catturino il fascino della carta (illustratore, tipo di scena, Pokémon "in coppia", popolarità su Google Trends…), poi rimisurare;
- **D.** Usare il valutatore soprattutto come **confronto relativo** ("questa carta costa più o meno delle sue simili") più che come prezzo esatto.

### 2.1 ⚠️ Il modello sbaglia molto più del ±15%

| Modello (stima su carte mai viste) | Errore tipico |
|---|---|
| Lineare migliore (due modelli per famiglia, con combinazioni) | **±50%** |
| Flessibile (gradient boosting) | ±44% |
| Segmenti entro ±15% | **0 su 8** |

**Un esempio concreto.** Per la Pikachu with Grey Felt Hat il trend vale 667 €, ma il modello stima 21 €. Il modello vede "promo Pikachu inglese del 2023" e non può sapere della febbre legata al museo Van Gogh. Lo stesso vale per la Munch (9.300 €). Ogni carta ha un fascino della sua illustrazione che le variabili non catturano.

**Cosa significa in pratica:** esattamente quello che prevede CLAUDE.md. Dove il modello supera il 15%, cioè ovunque, la scheda **non usa il suo prezzo**:
- il prezzo equo viene **solo dai comparabili con i tuoi prezzi NM**;
- il modello resta una "seconda opinione" dichiarata poco affidabile.

Il modello resta comunque utile per due cose: **scegliere i comparabili** (pesi della somiglianza) e **rettificarli** (×1,55, ×0,85…).

**I pesi invece hanno senso** (sovrapprezzi rispetto a una illustration rare inglese, iconicità bassa):

| Caratteristica | Sovrapprezzo |
|---|---|
| SIR | +209% |
| Pokémon Center | +277% |
| Iconicità alta | +133% |
| Solo giapponese | +83% |
| Alternate art (in più rispetto a SIR) | +81% |
| 1ª generazione | +72% |
| Umbreon, Espeon, Sylveon | da +270% a +420% rispetto ad "altro" |

**Cosa si potrebbe provare (da decidere insieme):**
- usare come prezzo la **media a 30 giorni** invece del trend, che è meno "nervosa";
- addestrare solo sulle carte **sopra i 10 €**: sotto i 10 € l'errore è del 56%;
- aggiungere variabili sull'**illustrazione**, per esempio l'illustratore famoso o lo stile della scena;
- accettare il ruolo di "seconda opinione" e puntare tutto sui comparabili. È già così.

### 2.2 Controllo di buon senso: 1 peso contro le attese, 3 forti da capire
- ⚠️ **Diluizione: +6%**, mentre ci si aspettava un calo. Le carte rare dei set con tante carte rare costano di più. Probabile motivo: i set speciali più ricercati (151, Prismatic Evolutions…) hanno molte IR e SIR.
- **Era Sole e Luna: +313%** rispetto a Scarlatto e Violetto. È coerente con "set vecchi = fuori stampa", ma è molto forte.
- **Shiny −50%** rispetto a una IR (le baby shiny costano poco). **Giapponese −36%** a parità di tutto il resto.

### 2.3 La tua combinazione chiave ha pochissime carte
"Iconicità alta × promo × solo giapponese" ha **5 carte** nel modello; "Pikachu × promo × solo giapponese" ne ha 3. Sotto le 15 carte non si può stimare un peso. Il motivo è a monte: le promo giapponesi con prezzo Cardmarket sono poche (SM-P e S-P non ci sono su TCGdex). Per queste carte la valutazione si appoggia **solo sui comparabili con i tuoi prezzi NM**, come deciso (D6).

### 2.4 Catalogo giapponese da TCGCSV (fatto, come deciso)
Ho aggiunto **2.481 carte giapponesi**, di cui 736 nel perimetro. Vengono dai 23 set vuoti su TCGdex (Shiny Star V, Eevee Heroes, VMAX Rising, 25th Anniversary…) e dalle promo SM-P, S-P e s8a-P. Si cercano nella dashboard (nome inglese, foto TCGplayer) e possono fare da comparabili. **Non hanno prezzo Cardmarket.** Esempio: cerca "pikachu 288 sm-p" per la Munch.

### 2.5 Tre variabili ancora grezze
- **Modalità di rilascio:** 654 promo nel modello restano "da classificare", di cui **159 sopra i 20 €**. Nessun indizio automatico: niente timbro, e TCGdex non dice da dove viene la promo. L'elenco è in `riepiloghi/blocco3_rilasci_da_classificare.csv`. È la parte che, con la regola Q2-A, toccherebbe a te. Prima però vorrei proporti un modo più automatico.
- **Esclusiva linguistica:** 589 carte "incerte". Il metodo (stessa specie + stesso illustratore nell'altra lingua) è grezzo e va migliorato.
- **Rarità:** gold, hyper e rainbow sono **unite** in una sola categoria, perché le fonti non le distinguono bene. Restano "da verificare" 48 "Secret Rare" giapponesi e 4 rarità nuove (Black White, Mega Attack, RGB, Futuristic).

### 2.6 Dettagli tecnici da sapere
- **Link Cardmarket nelle schede:** sono link di **ricerca** (nome + filtri lingua e Near Mint), perché non ho l'indirizzo della pagina di ogni prodotto. **Da verificare** se Cardmarket applica i filtri anche alla ricerca.
- **Dati della dashboard:** 128 file da circa 190 KB, 24 MB in tutto. Se li rigeneriamo ogni settimana, la cronologia di GitHub cresce di qualche MB a settimana. Prima di automatizzarli propongo di alleggerirli.
- **La raccolta automatica del lunedì è invariata:** salva solo la fotografia. Caratteristiche, modello e dashboard **non** si aggiornano da soli finché non approvi il modello (CLAUDE.md 6.7).
- **Fasce di età del set:** ho aggiunto 24–48 e 48+ mesi, perché "24+" metteva insieme carte del 2017 e del 2024.
- **PSA 10 e copie in vendita:** le caselle non ci sono ancora. Servono al punteggio di scarsità (blocco 6) e non compaiono nel mockup: le aggiungo nel blocco 6, con la tua approvazione su dove metterle.
- **Pulsanti disattivati:** "Correggi le caratteristiche" e "Aggiungi al monitoraggio" arrivano con i prossimi blocchi.

## 3. Tabelle e file da approvare

| File | Cosa contiene |
|---|---|
| `tabelle/set.csv` | 195 set: era, tipo (principale/speciale/sottoset/promo), collegamento a TCGplayer (27 + 7 scritti a mano) |
| `tabelle/rarita.csv` | 112 nomi di rarità → rarità armonizzata e perimetro |
| `tabelle/rilasci.csv` | timbri e set → modalità di rilascio |
| `variabili.md` | definizione e fonte delle 18 variabili |
| `riepiloghi/blocco3_2026-W41.md` | conteggi per valore, casi incerti, combinazioni, carte di controllo |
| `riepiloghi/blocco4_2026-W41.md` | confronto dei modelli, errori per segmento, sovrapprezzi, buon senso, carte di controllo |

## 4. Decisioni che ti chiederò stamattina (con le domande cliccabili)
1. Approvi le tabelle `rarita.csv`, `set.csv` e `rilasci.csv` così, o vuoi vedere prima qualche caso?
2. Modello: cosa proviamo per ridurre l'errore (media a 30 giorni, solo sopra i 10 €, nuove variabili) o lo teniamo come seconda opinione?
3. Rilasci da classificare (159 sopra i 20 €): li guardi tu o provo prima un metodo automatico?
4. Iconicità: confermi gli 8 Pokémon "da confermare" in `iconici.csv`?
5. Diluizione contro le attese: la teniamo (vince la validazione) o la togliamo?

*Valutazioni e giudizi sono stime statistiche con margine di errore, basate su dati di mercato e su carte simili: non sono certezze né consulenza finanziaria.*
