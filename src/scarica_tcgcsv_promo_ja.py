"""Blocco 1 - Promo giapponesi da TCGCSV (prezzi TCGplayer, USD, mercato USA).

TCGdex non ha i set promo giapponesi SM-P e S-P e ha pochi prezzi per SV-P:
questo script scarica da TCGCSV (categoria 85 "Pokemon Japan") prodotti e prezzi
dei set promo giapponesi moderni, per misurare quanto copre la fonte di riserva
(CLAUDE.md 4.2 e 4.7). Scarica solo cio' che serve: 2 richieste per set.

Uso:
    Mac:     .venv/bin/python src/scarica_tcgcsv_promo_ja.py
    Windows: .venv\\Scripts\\python src\\scarica_tcgcsv_promo_ja.py
"""

import datetime as dt
import json
import time
from pathlib import Path

import pandas as pd
import requests

RADICE = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RADICE / "config.json").read_text(encoding="utf-8"))
OGGI = dt.date.today()
ANNO_ISO, SETTIMANA_ISO, _ = OGGI.isocalendar()
NOME_SETTIMANA = f"{ANNO_ISO}-W{SETTIMANA_ISO:02d}"

# Set promo giapponesi dell'era moderna su TCGCSV (verificati l'8/10/2026).
GRUPPI_PROMO = {
    23881: "SM-P: Sun & Moon Promos",
    23847: "s8a-P: Promo Card Pack 25th Anniversary Edition",
    23876: "S-P: Sword & Shield Promos",
    23779: "SV-P Promotional Cards",
    24423: "M-P Promotional Cards",
}

sessione = requests.Session()
sessione.headers["User-Agent"] = CONFIG["user_agent"]


def scarica(url):
    risposta = sessione.get(url, timeout=30)
    risposta.raise_for_status()
    time.sleep(1)
    return risposta.json().get("results", [])


def main():
    destinazione = RADICE / "data" / "mercato" / f"{NOME_SETTIMANA}_tcgcsv_promo_ja.parquet"
    if destinazione.exists():
        print(f"{destinazione.name} esiste gia': non la sovrascrivo.")
        return

    righe = []
    for gruppo, nome_gruppo in GRUPPI_PROMO.items():
        base = f"https://tcgcsv.com/tcgplayer/85/{gruppo}"
        prodotti = scarica(f"{base}/products")
        prezzi = scarica(f"{base}/prices")
        prezzi_per_prodotto = {}
        for p in prezzi:
            prezzi_per_prodotto.setdefault(p["productId"], []).append(p)
        for prod in prodotti:
            extra = {e["name"]: e["value"] for e in prod.get("extendedData", [])}
            for p in prezzi_per_prodotto.get(prod["productId"], [{}]):
                righe.append({
                    "data_fotografia": OGGI.isoformat(),
                    "fonte": "TCGCSV (TCGplayer)",
                    "gruppo_id": gruppo,
                    "gruppo_nome": nome_gruppo,
                    "prodotto_id": prod["productId"],
                    "nome": prod.get("name"),
                    "numero": extra.get("Number"),
                    "rarita": extra.get("Rarity"),
                    "tipo_carta": extra.get("CardType"),
                    "sottotipo": p.get("subTypeName"),
                    "market_usd": p.get("marketPrice"),
                    "low_usd": p.get("lowPrice"),
                    "mid_usd": p.get("midPrice"),
                    "immagine": prod.get("imageUrl"),
                    "url_tcgplayer": prod.get("url"),
                })
        print(f"{nome_gruppo}: {len(prodotti)} prodotti", flush=True)

    tabella = pd.DataFrame(righe)
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    tabella.to_parquet(destinazione, index=False, compression="zstd")
    print(f"Salvata: {destinazione.relative_to(RADICE)} ({len(tabella)} righe)")


if __name__ == "__main__":
    main()
