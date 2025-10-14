# WaveBulk (dawniej AudioForge)

WaveBulk to innowacyjna webowa platforma SaaS (Software as a Service) przeznaczona dla muzyków, producentów i inżynierów dźwięku. Jej głównym celem jest uproszczenie i usprawnienie procesów związanych z finalnym przygotowaniem plików audio do dystrybucji, archiwizacji i zaawansowanej analizy. Aplikacja oferuje narzędzia, które są wygodniejsze i bardziej zaawansowane niż standardowe funkcje eksportu dostępne w programach DAW (Digital Audio Workstation).

## Spis treści

1.  [Koncepcja Projektu](#1-koncepcja-projektu)
2.  [Kluczowe Funkcje](#2-kluczowe-funkcje)
3.  [Model Biznesowy](#3-model-biznesowy)
4.  [Stos Technologiczny (Backend)](#4-stos-technologiczny-backend)
5.  [Środowisko Deweloperskie](#5-srodowisko-deweloperskie)
6.  [Struktura Katalogów](#6-struktura-katalogow)
7.  [Instalacja i Uruchomienie](#7-instalacja-i-uruchomienie)
    * [Wymagania wstępne](#71-wymagania-wstępne)
    * [Konfiguracja Bazy Danych (PostgreSQL)](#72-konfiguracja-bazy-danych-postgresql)
    * [Konfiguracja Redis](#73-konfiguracja-redis)
    * [Instalacja zależności Python](#74-instalacja-zależności-python)
    * [Konfiguracja zmiennych środowiskowych (.env)](#75-konfiguracja-zmiennych-srodowiskowych-env)
    * [Migracje Bazy Danych](#76-migracje-bazy-danych)
    * [Uruchomienie Serwera Flask](#77-uruchomienie-serwera-flask)
    * [Uruchomienie Workera Celery](#78-uruchomienie-workera-celery)
8.  [Uruchomienie Testów](#8-uruchomienie-testow)
9.  [Status Projektu i Dalsze Plany](#9-status-projektu-i-dalsze-plany)

---

### 1. Koncepcja Projektu

WaveBulk ma rozwiązać problemy, z jakimi borykają się muzycy i producenci, oferując scentralizowaną platformę online do zaawansowanego przetwarzania, analizy i zarządzania plikami audio. Celem jest zapewnienie narzędzi wygodniejszych i bardziej kompleksowych niż wbudowane funkcje eksportu w programach DAW.

### 2. Kluczowe Funkcje

* **Wysokiej Jakości Konwersja:** Precyzyjna konwersja między formatami bezstratnymi (WAV, FLAC, AIFF, ALAC) i stratnymi (MP3, AAC, OGG Vorbis) z kontrolą nad jakością (bitrate, głębia bitowa).
* **Profesjonalna Analiza Audio:** Dostarczanie kluczowych metryk masteringowych: zintegrowana głośność (LUFS), True Peak (dBTP), zakres dynamiki (Loudness Range) i korelacja stereo.
* **Zaawansowane Wizualizacje:** Prezentacja danych na profesjonalnych wykresach (historia głośności, goniometr, porównanie widma z wzorcami branżowymi) w celu dogłębnego zrozumienia materiału audio.
* **Przetwarzanie Wsadowe (Batch Processing):** Możliwość jednoczesnej konwersji i analizy wielu plików, co oszczędza godziny pracy.
* **Zarządzanie Metadanymi:** Wygodna edycja tagów, w tym ISRC i okładek albumów.
* **Bezpieczne Zarządzanie Plikami:** Przechowywanie plików w chmurze i historia przetwarzania.

### 3. Model Biznesowy

Aplikacja będzie działać w modelu subskrypcyjnym z trzema planami:

* **Darmowy:** Ograniczona liczba zadań i funkcji, idealny do testów.
* **PRO (ok. 49 zł/mies.):** Dla freelancerów i artystów; odblokowuje przetwarzanie wsadowe, pełną analizę i wszystkie formaty.
* **Studio (ok. 99 zł/mies.):** Dla profesjonalistów i małych studiów; oferuje nielimitowane zadania, najwyższy priorytet i stałe przechowywanie plików.
* **Integracja Płatności:** Planowana integracja ze Stripe do obsługi subskrypcji.

### 4. Stos Technologiczny (Backend)

* **Język Programowania:** Python 3.x
* **Framework Webowy:** Flask
* **Baza Danych:** PostgreSQL (produkcja), SQLite (testy)
* **ORM:** Flask-SQLAlchemy
* **System Kolejkowy:** Celery
* **Broker Wiadomości / Backend Wyników:** Redis
* **Zarządzanie Hasłami:** Werkzeug.security
* **Autoryzacja / Sesje:** Flask-Login
* **Migracje Bazy Danych:** Flask-Migrate (Alembic)
* **Przetwarzanie Audio:** pydub (z FFmpeg), pyloudnorm, soundfile
* **Zmienne Środowiskowe:** python-dotenv

### 5. Środowisko Deweloperskie

Projekt rozwijany jest w środowisku **Ubuntu 20.04 w WSL (Windows Subsystem for Linux)**. Jest to zalecane środowisko do rozwoju backendu, bliskie środowisku produkcyjnemu.

### 6. Struktura Katalogów

vaveforgepro/
├── backend/
│   ├── app/
│   │   ├── init.py         # Inicjalizacja Flask, SQLAlchemy, Celery
│   │   ├── models.py           # Definicje modeli bazy danych
│   │   ├── auth/               # Blueprint dla autoryzacji (rejestracja, logowanie, reset hasła)
│   │   │   └── routes.py
│   │   ├── routes/             # Blueprint dla przetwarzania audio (upload, status, historia)
│   │   │   └── audio_processing.py
│   │   ├── tasks/              # Zadania Celery
│   │   │   └── audio_tasks.py
│   │   ├── static/             # Pliki statyczne (CSS, JS, obrazy)
│   │   │   └── css/
│   │   │       ├── auth.css
│   │   │       └── base.css
│   │   │       └── custom.css
│   │   └── templates/          # Szablony HTML (Jinja2)
│   │       ├── base.html
│   │       ├── index.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── reset_password_request.html
│   │       └── reset_password.html
│   │       └── upload_audio.html
│   │       └── history.html
│   │   └── uploads/            # Tymczasowy katalog na przesyłane pliki
│   ├── tests/                  # Testy jednostkowe i integracyjne
│   │   └── test_audio_processing.py
│   ├── .env.example            # Przykładowy plik zmiennych środowiskowych
│   ├── .env                    # Zmienne środowiskowe (nie w Git!)
│   ├── requirements.txt        # Zależności Python
│   ├── run.py                  # Skrypt do uruchamiania serwera Flask
│   └── migrations/             # Migracje bazy danych (zarządzane przez Flask-Migrate)
└── README.md                   # Ten plik

### 7. Instalacja i Uruchomienie

#### 7.1. Wymagania wstępne

* **Python 3.x** (najlepiej Python 3.12, jak w środowisku dev)
* **WSL (Windows Subsystem for Linux)** lub środowisko Linux.
* **FFmpeg:**
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```

#### 7.2. Konfiguracja Bazy Danych (PostgreSQL)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Utwórz bazę danych i użytkownika
sudo -i -u postgres psql
CREATE DATABASE waveforgepro;
CREATE USER waveforgepro WITH PASSWORD 'TWOJE_SILNE_HASLO';
GRANT ALL PRIVILEGES ON DATABASE waveforgepro TO waveforgepro;
GRANT USAGE ON SCHEMA public TO waveforgepro;
GRANT CREATE ON SCHEMA public TO waveforgepro;
\q

7.3. Konfiguracja Redis
Bash

sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

7.4. Instalacja zależności Python

Przejdź do katalogu backend/:
Bash

cd backend/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

7.5. Konfiguracja zmiennych środowiskowych (.env)

Utwórz plik .env w katalogu backend/ i uzupełnij go:
Fragment kodu

# backend/.env

SECRET_KEY=TWOJ_BARDZO_TAJNY_KLUCZ_BEZPIECZENSTWA_FLASKA_ZMIEN_TO
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://waveforgepro:TWOJE_SILNE_HASLO@localhost/waveforgepro

Pamiętaj, aby zmienić TWOJ_BARDZO_TAJNY_KLUCZ_BEZPIECZENSTWA_FLASKA_ZMIEN_TO i TWOJE_SILNE_HASLO na unikalne i silne wartości!
7.6. Migracje Bazy Danych

Upewnij się, że masz poprawny backend/migrations/env.py (ostatnia wersja, którą podałem) i wykonaj:
Bash

rm -rf migrations/ # Usuń stary katalog migracji
# Połącz się z psql i usuń tabelę alembic_version, jeśli istnieje:
# sudo -i -u waveforgepro psql waveforgepro
# DROP TABLE IF EXISTS alembic_version;
# \q
FLASK_APP=run.py flask db init
FLASK_APP=run.py flask db migrate -m "Initial migration"
FLASK_APP=run.py flask db upgrade

7.7. Uruchomienie Serwera Flask

W nowym terminalu, z aktywowanym venv w backend/:
Bash

FLASK_APP=run.py flask run --host=0.0.0.0

Aplikacja będzie dostępna pod http://127.0.0.1:5000/.
7.8. Uruchomienie Workera Celery

W kolejnym nowym terminalu, z aktywowanym venv w backend/:
Bash

celery -A app:celery worker --loglevel=info

8. Uruchomienie Testów

Upewnij się, że wszystkie pliki są aktualne (szczególnie tests/test_audio_processing.py).
Z aktywowanym venv w backend/:
Bash

python -m unittest tests/test_audio_processing.py

Oczekiwany wynik: OK
9. Status Projektu i Dalsze Plany

Projekt WaveBulk osiągnął stabilną fazę MVP backendu z podstawowym frontendem HTML.

Główne osiągnięcia:

    Pełna integracja backendu (Flask, PostgreSQL, Celery, Redis).
    Działające testy jednostkowe dla kluczowych funkcji.
    Zaimplementowane widoki uwierzytelniania (rejestracja, logowanie, reset hasła) z niestandardową kolorystyką.
    Działający panel główny użytkownika i strona przesyłania plików.
    Szkielet strony historii przetwarzania plików.

Kolejne etapy rozwoju:

    Dokończenie stylizacji strony historii przetwarzania plików (tabeli).
    Rozwinięcie formularza przesyłania plików o walidację po stronie klienta, postęp uploadu itp.
    Implementacja zaawansowanej analizy audio i wizualizacji wyników.
    Integracja z API płatności (Stripe) dla modelu subskrypcyjnego.
    Przeniesienie przechowywania plików na magazyn chmurowy (np. AWS S3).
    Możliwość logowania przez OAuth (np. Google Sign-In).