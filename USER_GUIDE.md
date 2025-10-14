# 📖 WaveBulk - Przewodnik Użytkownika

## 🎯 Szybki start

### 1. Logowanie
```
http://localhost:5000/login
```

### 2. Dashboard (strona główna po zalogowaniu)
```
http://localhost:5000/audio/dashboard
```

**Co zobaczysz:**
- 📊 **Statystyki:** liczba plików, ukończonych zadań, średnia LUFS, zajęta przestrzeń
- 🚀 **Szybkie akcje:** prześlij pliki, zobacz historię, ulepsz plan
- 📁 **Ostatnie pliki:** 5 najnowszych konwersji z quick actions

---

## 🎵 Jak przetworzyć pliki?

### Krok 1: Upload plików
1. Kliknij **"Upload"** w menu górnym
2. Przeciągnij pliki .WAV na obszar drop lub kliknij "Wybierz pliki"
3. Skonfiguruj opcje przetwarzania (opcjonalnie)
4. Kliknij **"Rozpocznij Przetwarzanie"**

### Krok 2: Śledź postęp
- Pliki procesują się automatycznie w tle
- Zobacz status na żywo (ikony ✓, ⏳, ✗)
- Dashboard pokazuje liczbę zadań w trakcie

### Krok 3: Pobierz wyniki
**Opcja A - Pojedynczo:**
- Historia → kliknij "Pobierz" przy pliku

**Opcja B - Grupowo (ZIP):**
- Historia → zaznacz checkboxy
- Kliknij "Pobierz zaznaczone (ZIP)"

---

## 📊 Historia i wyszukiwanie

### Wyszukiwanie:
1. Wpisz nazwę pliku w search box
2. Filtry działają real-time

### Filtry statusu:
- **Wszystkie** - pokaż wszystko
- **Ukończone** - tylko gotowe
- **W trakcie** - przetwarzane teraz
- **Błędy** - nieudane konwersje

### Sortowanie:
- Tabela pokazuje najnowsze pliki na górze
- Kliknij nagłówki kolumn aby sortować (jeśli włączone)

---

## 🔍 Szczegóły pliku

Kliknij nazwę pliku w tabeli historii aby zobaczyć:

### 📈 Analiza techniczna:
- **LUFS** (głośność zintegrowana)
- **True Peak** (maksymalny szczyt w dBTP)
- **Czas trwania** utworu
- **Zakres dynamiki** (LRA)

### 📊 Wizualizacja LUFS:
- Kolorowy miernik głośności
- Porównanie z targetami platform:
  - Spotify: -14 LUFS
  - YouTube: -14 LUFS  
  - Apple Music: -16 LUFS
  - Broadcast: -23 LUFS
- **Interpretacja wyniku** z rekomendacjami

### 📋 Informacje szczegółowe:
- Nazwa oryginaln/przetworzona
- Rozmiar pliku
- Daty (upload, ukończenie)
- Pełne dane JSON z przetwarzania

---

## ⚙️ Opcje przetwarzania

### Format wyjściowy:
- **MP3** - uniwersalny, mały rozmiar
- **WAV** - bezstratny, duży
- **FLAC** - bezstratny, skompresowany

### Jakość:
- **MP3:** 320kbps (najwyższa) lub 192kbps
- **WAV/FLAC:** 16-bit, 24-bit, 32-bit float

### Normalizacja LUFS:
- **Spotify** (-14 LUFS)
- **Apple Music** (-16 LUFS)
- **YouTube** (-14 LUFS)
- **Własne ustawienia** (custom)

### Zaawansowane:
- **Dithering** (dla 16-bit)
- **Resampling** quality
- **True Peak Limiter** (zalecane: ON)

### Metadane (opcjonalne):
- Wykonawca, Album, Tytuł
- Numer utworu, ISRC
- Okładka albumu (JPG/PNG)

---

## 🎨 Przełączanie języków

**EN ↔ PL** - kliknij w prawym górnym rogu:
- **EN** - angielski
- **PL** - polski

Wybór języka zapisuje się w sesji (30 dni).

---

## 💾 Bulk operations

### Pobieranie wielu plików (ZIP):
1. W historii zaznacz checkboxy przy plikach
2. Kliknij **"Pobierz zaznaczone (ZIP)"**
3. Otrzymasz archiwum `wavebulk_files_2025-10-14.zip`

### Usuwanie wielu plików:
1. Zaznacz checkboxy
2. Kliknij **"Usuń zaznaczone"**
3. Potwierdź w oknie dialogowym
4. Pliki zostaną usunięte (nie można cofnąć!)

### Select All:
- Checkbox w nagłówku tabeli zaznacza **tylko widoczne pliki** (po filtrowaniu)

---

## 🐛 Rozwiązywanie problemów

### Przełączanie języków nie działa:
- Wyczyść cookies przeglądarki
- Spróbuj w trybie incognito
- Sprawdź czy pliki `.mo` istnieją w `/backend/app/translations/*/LC_MESSAGES/`

### Upload nie działa:
- Sprawdź format pliku (tylko .WAV)
- Sprawdź rozmiar (max 100 MB)
- Sprawdź czy Redis i Celery worker działają

### Przetwarzanie wisi:
- Sprawdź logi: `./manage.sh logs worker`
- Sprawdź Redis: `./manage.sh status`
- Zrestartuj worker: `docker-compose restart worker`

### Brak statystyk na Dashboard:
- Przetwórz conajmniej 1 plik
- Poczekaj na ukończenie zadania
- Odśwież stronę

---

## 🔐 Bezpieczeństwo

### Sesje:
- Cookies HTTPOnly (ochrona przed XSS)
- SameSite=Lax (ochrona przed CSRF)
- 30-dniowa ważność
- Secure=True w produkcji (HTTPS)

### Pliki:
- Tylko zalogowani użytkownicy mogą upload
- Walidacja typu i rozmiaru pliku
- Secure filename (usuwanie niebezpiecznych znaków)
- Izolacja użytkowników (nie widzą cudzych plików)

---

## 📱 Urządzenia mobilne

Aplikacja jest w pełni responsywna:

### Mobile (telefon):
- Uproszczone menu (ukryta nawigacja)
- Touch-friendly przyciski
- Scrollable tabele
- Zoptymalizowane layouty

### Tablet:
- 2-kolumnowe gridy
- Wszystkie funkcje dostępne
- Landscape/portrait support

### Desktop:
- Pełne gridy (3-4 kolumny)
- Wszystkie funkcje widoczne
- Hover effects

---

## 🎓 Tips & Tricks

### Szybkie workflow:
1. **Ctrl+Click** na plik w historii → nowa karta z szczegółami
2. **Select All** → "Pobierz ZIP" → cały album jednym klikiem
3. **Filtry** → szybko znajdź nieukończone zadania
4. **Dashboard** → szybki przegląd bez klikania

### Oszczędzanie czasu:
- Ustaw opcje raz, przetwórz 20 plików wsadowo
- Użyj presetów LUFS dla platformy docelowej
- Dodaj metadane raz dla całego albumu

### Monitorowanie jakości:
- Dashboard → "Średnia LUFS" pokazuje ogólny profil Twojej muzyki
- File details → porównaj z targetami platform
- LUFS meter → wizualna interpretacja jakości

---

## 📊 Interpretacja wyników LUFS

### Zakresy głośności:

| LUFS | Interpretacja | Rekomendacja |
|------|---------------|--------------|
| 0 do -6 | 🔴 Bardzo głośne | Prawdopodobnie przesterowane, zmniejsz |
| -6 do -10 | 🟡 Głośne | Dobry dla agresywnej muzyki |
| -10 do -14 | 🟢 Optymalny | Perfekcyjny dla Spotify/YouTube |
| -14 do -18 | 🔵 Dobry | Optymalny dla Apple Music |
| -18 do -23 | ℹ️ Cichy | Rozważ normalizację |
| Poniżej -23 | ⚠️ Bardzo cichy | Definitywnie normalizuj |

### Platformy streamingowe:
- **Spotify/YouTube:** Target -14 LUFS
- **Apple Music:** Target -16 LUFS
- **Tidal:** Target -14 LUFS
- **Amazon Music:** Target -14 LUFS

Głośniejsze pliki będą automatycznie ściszane przez platformy!

---

## 🎛️ Najlepsze praktyki

### Przed uplodem:
- Eksportuj z DAW w najwyższej jakości (24-bit/48kHz)
- Zostaw headroom (~-3dB peak)
- Nie kompresuj do MP3 przed uplodem

### Podczas przetwarzania:
- Wybierz właściwy target LUFS dla platformy
- Włącz True Peak Limiter (zapobiega clipping)
- Dla 16-bit zawsze użyj dithering

### Po przetworzeniu:
- Sprawdź LUFS meter
- Posłuchaj wyniku przed publikacją
- Porównaj z referencyjnymi utworami

---

## ⌨️ Skróty klawiszowe (planowane)

- `Ctrl+U` - Upload
- `Ctrl+H` - Historia
- `Ctrl+D` - Dashboard
- `Ctrl+A` - Select all w tabeli

---

## 💬 FAQ

**Q: Dlaczego tylko .WAV?**  
A: WAV to bezstratny format - najlepsza jakość wejściowa = najlepsza jakość wyjściowa.

**Q: Czy mogę konwertować MP3 → MP3?**  
A: Nie zalecamy - każda konwersja stratn→stratna pogarsza jakość.

**Q: Co to jest LUFS?**  
A: Loudness Units Full Scale - standard pomiaru głośności. -14 LUFS = głośność Spotify.

**Q: Dlaczego mój plik jest za głośny?**  
A: Użyj presetów normalizacji lub zmniejsz gain w DAW.

**Q: Ile plików mogę przetworzyć naraz?**  
A: Plan FREE: ograniczony. Plan PRO/Studio: nielimitowany.

---

## 📞 Support

Problemy? Zobacz:
1. Logi: `./manage.sh logs web`
2. Debug session: `http://localhost:5000/debug-session`
3. Testy: `./manage.sh test`

---

Miłego użytkowania WaveBulk! 🎵✨

