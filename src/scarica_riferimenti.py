"""Blocco 3 - Tabelle di riferimento (cambiano raramente, non ogni settimana).

1. TCGCSV (TCGplayer): elenco dei prodotti dei set moderni, inglesi (categoria 3) e
   giapponesi (categoria 85), con numero, rarita' e nome. Serve per:
   - completare le rarita' giapponesi mancanti su TCGdex (set + numero);
   - riconoscere le alternate art di Spada e Scudo ("Alternate Full Art" nel nome);
   - indizi sulla modalita' di rilascio e sulle esclusive linguistiche.
   Scarica solo i prodotti (niente prezzi): una richiesta per set, con pausa.
2. PokeAPI: specie Pokemon con generazione, leggendario, misterioso e nomi en/ja
   (due file CSV pubblici, una richiesta ciascuno).

Uso:
    Mac:     .venv/bin/python src/scarica_riferimenti.py
    Windows: .venv\\Scripts\\python src\\scarica_riferimenti.py
"""

import datetime as dt
import io
import json
import time
from pathlib import Path

import pandas as pd
import requests

RADICE = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RADICE / "config.json").read_text(encoding="utf-8"))
DEST = RADICE / "data" / "riferimento"
OGGI = dt.date.today().isoformat()
INIZIO_ERA = "2016-11-01"  # SM-P giapponese esce a novembre 2016
POKEAPI_CSV = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv"

sessione = requests.Session()
sessione.headers["User-Agent"] = CONFIG["user_agent"]


def scarica_json(url):
    for tentativo in range(1, CONFIG["tentativi"] + 1):
        try:
            r = sessione.get(url, timeout=30)
            r.raise_for_status()
            time.sleep(1)
            return r.json().get("results", [])
        except (requests.RequestException, ValueError) as e:
            if tentativo == CONFIG["tentativi"]:
                print(f"ERRORE {url}: {e}")
                return None
            time.sleep(2 ** tentativo)


def prodotti_tcgcsv(categoria, lingua):
    gruppi = scarica_json(f"https://tcgcsv.com/tcgplayer/{categoria}/groups") or []
    moderni = [g for g in gruppi if (g.get("publishedOn") or "")[:10] >= INIZIO_ERA]
    print(f"TCGCSV {lingua}: {len(moderni)} set moderni su {len(gruppi)}", flush=True)
    righe = []
    for i, g in enumerate(moderni, 1):
        prodotti = scarica_json(f"https://tcgcsv.com/tcgplayer/{categoria}/{g['groupId']}/products")
        if prodotti is None:
            continue
        for p in prodotti:
            extra = {e["name"]: e["value"] for e in p.get("extendedData", [])}
            righe.append({
                "data": OGGI,
                "fonte": "TCGCSV (TCGplayer)",
                "lingua": lingua,
                "gruppo_id": g["groupId"],
                "gruppo_nome": g["name"],
                "gruppo_sigla": g.get("abbreviation"),
                "gruppo_data": (g.get("publishedOn") or "")[:10],
                "prodotto_id": p["productId"],
                "nome": p.get("name"),
                "numero": extra.get("Number"),
                "rarita": extra.get("Rarity"),
                "tipo_carta": extra.get("CardType"),
                "stadio": extra.get("Stage"),
                "hp": extra.get("HP"),
            })
        if i % 25 == 0:
            print(f"  {i}/{len(moderni)} set", flush=True)
    return pd.DataFrame(righe)


def specie_pokeapi():
    specie = pd.read_csv(io.StringIO(sessione.get(f"{POKEAPI_CSV}/pokemon_species.csv", timeout=30).text))
    nomi = pd.read_csv(io.StringIO(sessione.get(f"{POKEAPI_CSV}/pokemon_species_names.csv", timeout=30).text))
    # Lingue PokeAPI: 9 = inglese, 1 = giapponese (katakana), 11 = giapponese (romaji/kanji)
    en = nomi[nomi.local_language_id == 9].set_index("pokemon_species_id")["name"]
    ja = nomi[nomi.local_language_id == 1].set_index("pokemon_species_id")["name"]
    tab = specie[["id", "identifier", "generation_id", "is_legendary", "is_mythical"]].copy()
    tab["nome_en"] = tab.id.map(en)
    tab["nome_ja"] = tab.id.map(ja)
    tab.insert(0, "fonte", "PokeAPI")
    tab.insert(1, "data", OGGI)
    return tab


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    specie = specie_pokeapi()
    specie.to_csv(DEST / "pokeapi_specie.csv", index=False)
    print(f"PokeAPI: {len(specie)} specie", flush=True)
    for categoria, lingua in ((85, "ja"), (3, "en")):
        tab = prodotti_tcgcsv(categoria, lingua)
        tab.to_parquet(DEST / f"tcgcsv_prodotti_{lingua}.parquet", index=False, compression="zstd")
        print(f"Salvata: data/riferimento/tcgcsv_prodotti_{lingua}.parquet ({len(tab)} prodotti)", flush=True)


if __name__ == "__main__":
    main()
