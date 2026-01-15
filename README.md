# Onet Scraper Pro

Profesjonalny scraper danych z portalu Onet.pl, przygotowany do pracy produkcyjnej (24/7). Narzędzie pobiera artykuły, czyści treść z reklam i zapisuje dane w formacie JSONL.

## Funkcje

*   **Bypass Anti-Bot**: Wykorzystuje hybrydowe podejście (Scrapy + `urllib`) do omijania prostych blokad i przekierowań.
*   **Czyste Dane**: Automatyczne usuwanie sekcji "Dołącz do Premium" i reklam.
*   **Bogate Metadane**: Pobieranie autora, sekcji tematycznej, daty publikacji i modyfikacji (z JSON-LD oraz fallbacków CSS).
*   **Bezpieczeństwo**: Skonfigurowany User-Agent, opóźnienia (throttling) i wyłączone cookies.

## Wymagania

*   Python 3.10+
*   Biblioteki w `requirements.txt`

## Instalacja

1.  Sklonuj repozytorium lub skopiuj pliki na serwer.
2.  Utwórz wirtualne środowisko (zalecane):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    .\venv\Scripts\Activate   # Windows
    ```
3.  Zainstaluj zależności:
    ```bash
    pip install -r requirements.txt
    ```

## Uruchomienie

### Lokalnie (Testy)
Aby uruchomić scraper i zobaczyć logi w konsoli:
```bash
python -m scrapy crawl onet
```
Dane trafią do nowo utworzonego pliku z sygnaturą czasową, np. `data_2026-01-15_18-30-00.jsonl`.

### Na Serwerze (Produkcja / Linux VPS)
Aby uruchomić proces w tle (nohup), który nie zostanie przerwany po wylogowaniu:

```bash
nohup python -m scrapy crawl onet > /dev/null 2>&1 &
```
*Uwaga: Logi w tym trybie są zapisywane do pliku `scraper.log` (zgodnie z ustawieniami w `settings.py`).*

Monitorowanie logów na żywo:
```bash
tail -f scraper.log
```

## Testy
Projekt posiada zestaw testów jednostkowych (pytest).
```bash
python -m pytest
```

## Struktura Plików
*   `onet_scraper/spiders/onet.py`: Główna logika pająka.
*   `onet_scraper/middlewares.py`: Logika omijania blokad sieciowych.
*   `onet_scraper/items.py`: Model danych (walidacja Pydantic).
*   `onet_scraper/settings.py`: Konfiguracja produkcyjna (User-Agent, Throttling).
*   `tests/`: Testy jednostkowe.
