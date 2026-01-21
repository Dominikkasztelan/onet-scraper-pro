# Onet Scraper

Profesjonalny scraper danych z portalu Onet.pl, przygotowany do pracy produkcyjnej (24/7). Narzędzie pobiera artykuły, czyści treść z reklam i zapisuje dane w formacie JSONL. Wykorzystuje sieć Tor do anonimizacji i rotacji IP.

## Funkcje

*   **Bypass Anti-Bot**: Wykorzystuje sieć Tor oraz `curl_cffi` (TLS Fingerprint Impersonation) do omijania zaawansowanych zabezpieczeń.
*   **Rotacja IP**: Automatyczna zmiana tożsamości Tor w przypadku wykrycia blokady (403/Redirect).
*   **Czyste Dane**: Automatyczne usuwanie sekcji "Dołącz do Premium" i reklam.
*   **Bogate Metadane**: Pobieranie autora, sekcji tematycznej, daty publikacji i modyfikacji (z JSON-LD oraz fallbacków CSS).
*   **Bezpieczeństwo**: Zarządzanie sekretami przez `.env` i brak hardcodowanych haseł.

## Wymagania

*   Python 3.10+
*   Docker (opcjonalnie, do łatwego uruchomienia z Tor)

## Instalacja

### Metoda 1: Docker Compose (Zalecane)

Najszybszy sposób na uruchomienie scrapera wraz z wymaganą usługą Tor.

1.  Sklonuj repozytorium.
2.  Skopiuj przykładowy plik środowiskowy:
    ```bash
    cp .env.example .env
    ```
3.  Uruchom usługi:
    ```bash
    docker-compose up -d --build
    ```
    To uruchomi kontener `tor` oraz `scraper`. Scraper rozpocznie pracę automatycznie.

4.  Sprawdź logi:
    ```bash
    docker-compose logs -f scraper
    ```

Dane będą zapisywane w katalogu `./data`.

### Metoda 2: Lokalnie (Python Virtualenv)

Wymaga zainstalowanego i działającego Tora na porcie 9050 (SOCKS) i 9051 (Control).

1.  Utwórz wirtualne środowisko:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    .\venv\Scripts\Activate   # Windows
    ```
2.  Zainstaluj zależności:
    ```bash
    pip install -r requirements.txt
    ```
3.  Skonfiguruj środowisko:
    Utwórz plik `.env` (wzorując się na `.env.example`) i upewnij się, że `TOR_PROXY` wskazuje na Twoją instancję Tora.

4.  Uruchom scraper:
    ```bash
    python -m scrapy crawl onet
    ```

## Development

### Formatowanie kodu
Projekt wykorzystuje `ruff` do dbania o jakość kodu. Przed commitem uruchom:
```bash
ruff format .
ruff check . --fix
```

### Testy
Uruchom testy jednostkowe:
```bash
python -m pytest
```

## Struktura Plików
*   `onet_scraper/`: Kod źródłowy Scrapy.
    *   `spiders/`: Logika pająka.
    *   `middlewares.py`: Rotacja IP i obsługa Tora.
*   `tests/`: Testy `pytest`.
*   `docker-compose.yml`: Definicja usług Docker.
*   `.env`: Konfiguracja (nie commitować!).
