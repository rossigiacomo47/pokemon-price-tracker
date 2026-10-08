"""Blocco 1 - Fotografia del mercato da TCGdex.

Scarica le carte delle ere moderne (Sole e Luna in poi), internazionali (en) e
giapponesi (ja), con prezzi Cardmarket (EUR), prezzi TCGplayer (USD, quando ci
sono) e caratteristiche di base. Salva UNA RIGA PER VARIANTE (normale, reverse,
holo, stamped...) perche' su Cardmarket ogni variante ha il suo prezzo.

Uso (dalla cartella del progetto):
    Mac:     .venv/bin/python src/scarica_tcgdex.py
    Windows: .venv\\Scripts\\python src\\scarica_tcgdex.py
Opzioni:
    --prova N   scarica solo N carte per lingua e salva in cache/prova/ (per i test)

Regole (CLAUDE.md 4.1, 4.6):
- nessun prezzo inventato: un valore 0 o mancante diventa "vuoto";
- se una richiesta fallisce: registra l'errore, salta, continua;
- le fotografie gia' salvate non vengono mai sovrascritte.
"""

import argparse
import datetime as dt
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests

RADICE = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RADICE / "config.json").read_text(encoding="utf-8"))
API = "https://api.tcgdex.net/v2"

OGGI = dt.date.today()
ANNO_ISO, SETTIMANA_ISO, _ = OGGI.isocalendar()
NOME_SETTIMANA = f"{ANNO_ISO}-W{SETTIMANA_ISO:02d}"
CARTELLA_CACHE = RADICE / "cache" / OGGI.isoformat()

sessione = requests.Session()
sessione.headers["User-Agent"] = CONFIG["user_agent"]
errori = []
blocco_errori = threading.Lock()


def nome_file_sicuro(testo):
    return quote(testo, safe="")


def scarica_json(percorso_api, tipo, chiave):
    """Scarica un JSON da TCGdex usando una copia locale del giorno, se c'e'."""
    file_cache = CARTELLA_CACHE / tipo / f"{nome_file_sicuro(chiave)}.json"
    if file_cache.exists():
        return json.loads(file_cache.read_text(encoding="utf-8"))

    url = f"{API}/{percorso_api}"
    for tentativo in range(1, CONFIG["tentativi"] + 1):
        try:
            risposta = sessione.get(url, timeout=30)
            if risposta.status_code == 404:
                registra_errore(url, "404 non trovata")
                return None
            if risposta.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {risposta.status_code}")
            risposta.raise_for_status()
            dati = risposta.json()
            file_cache.parent.mkdir(parents=True, exist_ok=True)
            file_cache.write_text(json.dumps(dati, ensure_ascii=False), encoding="utf-8")
            time.sleep(CONFIG["pausa_secondi"])
            return dati
        except (requests.RequestException, ValueError) as e:
            if tentativo == CONFIG["tentativi"]:
                registra_errore(url, str(e))
                return None
            time.sleep(2 ** tentativo)


def registra_errore(url, messaggio):
    with blocco_errori:
        errori.append({"data": OGGI.isoformat(), "url": url, "errore": messaggio})


def prezzo(valore):
    """0, valori negativi o mancanti = dato mancante (mai un prezzo)."""
    if isinstance(valore, (int, float)) and valore > 0:
        return float(valore)
    return None


# ---------------------------------------------------------------- set e serie

def elenco_set(lingua):
    """Restituisce i set da scaricare per una lingua, con i loro dettagli."""
    serie = scarica_json(f"{lingua}/series", "serie", f"{lingua}_elenco") or []
    moderne = set(CONFIG["serie_moderne"][lingua])
    escluse = set(CONFIG["serie_escluse"])
    inizio = CONFIG["data_inizio_altre_serie"]

    scelti = []
    for s in serie:
        if s["id"] in escluse:
            continue
        dettaglio = scarica_json(f"{lingua}/series/{quote(s['id'], safe='')}", "serie", f"{lingua}_{s['id']}")
        if not dettaglio:
            continue
        for st in dettaglio.get("sets", []):
            info = scarica_json(f"{lingua}/sets/{quote(st['id'], safe='')}", "set", f"{lingua}_{st['id']}")
            if not info:
                continue
            data_uscita = info.get("releaseDate") or ""
            # Serie moderne: tutto (anche Sole e Luna giapponese di dic. 2016, decisione D2).
            # Altre serie (McDonald's, varie): solo i set usciti dalla data di inizio.
            if s["id"] in moderne or (data_uscita and data_uscita >= inizio):
                scelti.append(info)
    return scelti


# ---------------------------------------------------------------- carte

def righe_carta(carta, info_set, lingua):
    """Trasforma una carta TCGdex in una riga per ogni variante."""
    base = {
        "data_fotografia": OGGI.isoformat(),
        "fonte": "TCGdex",
        "lingua": lingua,
        "id": carta.get("id"),
        "numero": carta.get("localId"),
        "nome": carta.get("name"),
        "categoria": carta.get("category"),
        "rarita_tcgdex": carta.get("rarity"),
        "dex_id": ",".join(str(x) for x in (carta.get("dexId") or [])) or None,
        "illustratore": carta.get("illustrator"),
        "stadio": carta.get("stage"),
        "suffisso": carta.get("suffix"),
        "hp": carta.get("hp"),
        "tipi": ",".join(carta.get("types") or []) or None,
        "regulation_mark": carta.get("regulationMark"),
        "legale_standard": (carta.get("legal") or {}).get("standard"),
        "legale_expanded": (carta.get("legal") or {}).get("expanded"),
        "immagine": carta.get("image"),
        "varianti_tcgdex": json.dumps(carta.get("variants") or {}),
        "set_id": info_set.get("id"),
        "set_nome": info_set.get("name"),
        "set_data_uscita": info_set.get("releaseDate"),
        "serie_id": (info_set.get("serie") or {}).get("id"),
        "serie_nome": (info_set.get("serie") or {}).get("name"),
        "set_carte_ufficiali": (info_set.get("cardCount") or {}).get("official"),
        "set_carte_totali": (info_set.get("cardCount") or {}).get("total"),
    }

    varianti = carta.get("variants_detailed") or []
    if not varianti:
        # Carta senza dettaglio per variante: una sola riga con i prezzi generali.
        flags = carta.get("variants") or {}
        tipo = next((t for t in ("holo", "normal", "reverse") if flags.get(t)), None)
        varianti = [{"type": tipo, "pricing": carta.get("pricing") or {}, "_senza_dettaglio": True}]

    # Prodotti Cardmarket condivisi da una variante "reverse": li' il campo -holo e' la reverse.
    prodotti_con_reverse = {
        (v.get("thirdParty") or {}).get("cardmarket")
        for v in varianti if v.get("type") == "reverse"
    }

    righe = []
    for n, v in enumerate(varianti):
        cm = (v.get("pricing") or {}).get("cardmarket") or {}
        tp = (v.get("pricing") or {}).get("tcgplayer") or {}
        riga = dict(base)
        riga.update({
            "variante_n": n,
            "variante_tipo": v.get("type"),
            "variante_formato": v.get("size"),
            "variante_timbro": ",".join(v.get("stamp") or []) or None,
            "variante_foil": v.get("foil"),
            "variante_senza_dettaglio": bool(v.get("_senza_dettaglio")),
            "cm_id_prodotto": cm.get("idProduct") or (v.get("thirdParty") or {}).get("cardmarket"),
            "cm_aggiornato": cm.get("updated"),
        })
        for campo in ("avg", "low", "trend", "avg1", "avg7", "avg30"):
            riga[f"cm_{campo}"] = prezzo(cm.get(campo))
            riga[f"cm_{campo}_holo"] = prezzo(cm.get(f"{campo}-holo"))

        # Regola del prezzo di riferimento (vedi README, "Prezzo di riferimento").
        t, th = riga["cm_trend"], riga["cm_trend_holo"]
        if v.get("type") == "reverse":
            campo_usato = "trend-holo" if th else "nessuno"
        elif riga["cm_id_prodotto"] in prodotti_con_reverse:
            campo_usato = "trend" if t else "nessuno"
        elif t and th:
            campo_usato = "ambiguo"
        elif t:
            campo_usato = "trend"
        elif th:
            campo_usato = "trend-holo"
        else:
            campo_usato = "nessuno"
        suff = "_holo" if campo_usato == "trend-holo" else ""
        valido = campo_usato in ("trend", "trend-holo")
        riga["campo_prezzo"] = campo_usato
        riga["prezzo_rif_eur"] = riga[f"cm_trend{suff}"] if valido else None
        riga["avg7_rif_eur"] = riga[f"cm_avg7{suff}"] if valido else None
        riga["avg30_rif_eur"] = riga[f"cm_avg30{suff}"] if valido else None
        riga["low_rif_eur"] = riga[f"cm_low{suff}"] if valido else None

        # TCGplayer (USD): sottotipo coerente con la variante, se c'e'.
        preferito = {"normal": "normal", "reverse": "reverse-holofoil", "holo": "holofoil"}.get(v.get("type"))
        sottotipi = [k for k in tp if isinstance(tp[k], dict)]
        scelto = preferito if preferito in sottotipi else (sottotipi[0] if len(sottotipi) == 1 else None)
        riga["tcgp_sottotipo"] = scelto
        riga["tcgp_market_usd"] = prezzo((tp.get(scelto) or {}).get("marketPrice")) if scelto else None
        riga["tcgp_low_usd"] = prezzo((tp.get(scelto) or {}).get("lowPrice")) if scelto else None
        riga["tcgp_aggiornato"] = tp.get("updated")
        righe.append(riga)
    return righe


def scarica_lingua(lingua, limite=None):
    print(f"\n=== {lingua}: elenco dei set ===", flush=True)
    sets = elenco_set(lingua)
    print(f"{lingua}: {len(sets)} set selezionati", flush=True)

    lavori = []
    visti = set()
    for info in sets:
        for c in info.get("cards", []):
            if c["id"] not in visti:
                visti.add(c["id"])
                lavori.append((c["id"], info))
    if limite:
        lavori = lavori[:limite]
    print(f"{lingua}: {len(lavori)} carte da scaricare", flush=True)

    righe = []
    inizio = time.time()
    with ThreadPoolExecutor(max_workers=CONFIG["richieste_parallele"]) as pool:
        futuri = {
            pool.submit(scarica_json, f"{lingua}/cards/{quote(cid, safe='')}", f"carte_{lingua}", cid): (cid, info)
            for cid, info in lavori
        }
        for i, futuro in enumerate(as_completed(futuri), 1):
            cid, info = futuri[futuro]
            carta = futuro.result()
            if carta:
                righe.extend(righe_carta(carta, info, lingua))
            if i % 500 == 0 or i == len(lavori):
                minuti = (time.time() - inizio) / 60
                print(f"{lingua}: {i}/{len(lavori)} carte ({minuti:.1f} min)", flush=True)
    return righe


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prova", type=int, default=None, help="scarica solo N carte per lingua")
    args = parser.parse_args()

    if args.prova:
        destinazione = RADICE / "cache" / "prova" / f"{NOME_SETTIMANA}.parquet"
    else:
        destinazione = RADICE / "data" / "mercato" / f"{NOME_SETTIMANA}.parquet"
        if destinazione.exists():
            print(f"La fotografia {destinazione.name} esiste gia': non la sovrascrivo (CLAUDE.md, sezione 14).")
            return

    tutte = []
    for lingua in CONFIG["lingue"]:
        tutte.extend(scarica_lingua(lingua, args.prova))

    tabella = pd.DataFrame(tutte)
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    tabella.to_parquet(destinazione, index=False, compression="zstd")
    print(f"\nSalvata: {destinazione.relative_to(RADICE)} "
          f"({len(tabella)} righe, {destinazione.stat().st_size / 1e6:.2f} MB)")

    if errori:
        file_errori = destinazione.parent.parent / "log" / f"errori_{NOME_SETTIMANA}.csv"
        if args.prova:
            file_errori = destinazione.parent / f"errori_{NOME_SETTIMANA}.csv"
        file_errori.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(errori).to_csv(file_errori, index=False)
        print(f"Errori registrati: {len(errori)} -> {file_errori.relative_to(RADICE)}")
    else:
        print("Nessun errore.")


if __name__ == "__main__":
    main()
