# 🧪 Przewodnik Testowania - Naprawy M4A i Background Processing

## ✅ Co zostało naprawione?

### Problem 1: M4A nie był akceptowany ❌ → NAPRAWIONY ✅
### Problem 2: Blokada strony podczas przetwarzania ❌ → NAPRAWIONA ✅

---

## 🚀 Szybki Test

### PRZED rozpoczęciem:
```bash
# Upewnij się, że aplikacja działa:
cd /srv/docker/vaveforgepro
./manage.sh status

# Powinno pokazać:
# ✅ waveforge_web      Up
# ✅ waveforge_worker   Up
# ✅ waveforge_db       Up
# ✅ waveforge_redis    Up
```

---

## 📋 Test 1: Upload M4A (2 minuty)

### Krok po kroku:

**1. Otwórz aplikację**
```
http://localhost:5000
```

**2. Zaloguj się** (lub zarejestruj nowe konto)

**3. Przejdź do Upload**
```
Menu → Upload
lub bezpośrednio:
http://localhost:5000/audio/upload-and-process
```

**4. Przygotuj plik M4A**
- Użyj swojego: `Nagranie (6).m4a`
- Lub stwórz testowy:
```bash
# W terminalu:
ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -c:a aac -b:a 128k test.m4a
```

**5. Upload pliku M4A**
- Przeciągnij M4A na stronę
- LUB kliknij "Wybierz pliki" i wybierz M4A

**6. Weryfikacja ✅**
```
PRZED (błąd):
  ❌ "Only WAV files are supported"
  
PO (poprawnie):
  ✅ Plik pojawia się w kolejce
  ✅ Przycisk "Rozpocznij Przetwarzanie" aktywny
  ✅ Brak komunikatów o błędzie
```

**7. Wybierz opcje (opcjonalnie)**
```
Format: MP3
Bitrate: 320k
LUFS: Spotify (-14)
```

**8. Kliknij "Rozpocznij Przetwarzanie"**

**9. Obserwuj:**
```
✅ Banner na górze:
   "Zadania przetwarzają się w tle
    Możesz bezpiecznie opuścić tę stronę."
    
✅ Przycisk: [Zobacz Historię]

✅ Status pliku: "Przetwarzanie w tle..."

✅ Progress bar
```

---

## 📋 Test 2: Brak Blokady Strony (1 minuta)

### Podczas gdy plik się przetwarza:

**Test A: Próba opuszczenia strony**
```
1. Podczas przetwarzania kliknij:
   - Back button przeglądarki
   - LUB naciśnij Ctrl+W (zamknij kartę)
   - LUB przejdź do innej strony w menu

2. WERYFIKACJA:
   PRZED (błąd):
     ❌ Popup: "Czy na pewno chcesz opuścić stronę?"
     ❌ Musisz kliknąć "Zostań" lub "Opuść"
     
   PO (poprawnie):
     ✅ BRAK popup-a!
     ✅ Możesz swobodnie nawigować
     ✅ Zadania dalej się przetwarzają w tle
```

**Test B: Przejście do Historii**
```
1. Kliknij "Zobacz Historię" w bannerze
   LUB Menu → Historia

2. WERYFIKACJA:
   ✅ Strona Historia się otwiera
   ✅ Widzisz swoje pliki
   ✅ Status: "PROCESSING" lub "COMPLETED"
   ✅ Real-time refresh (co 10s)
```

**Test C: Całkowite opuszczenie**
```
1. Podczas przetwarzania zamknij całkowicie przeglądarkę
2. Poczekaj 30 sekund (kawa ☕)
3. Otwórz ponownie aplikację
4. Przejdź do Historia

WERYFIKACJA:
  ✅ Plik przetworzony!
  ✅ Status: "COMPLETED"
  ✅ LUFS, Duration wyświetlone
  ✅ Przycisk [Pobierz] działa
```

---

## 📋 Test 3: Różne Formaty (5 minut)

### Sprawdź wszystkie obsługiwane formaty:

```bash
# Wygeneruj testowe pliki:
cd /tmp

# WAV
ffmpeg -f lavfi -i "sine=frequency=440:duration=3" test.wav

# MP3
ffmpeg -f lavfi -i "sine=frequency=440:duration=3" -c:a libmp3lame -b:a 192k test.mp3

# M4A
ffmpeg -f lavfi -i "sine=frequency=440:duration=3" -c:a aac -b:a 128k test.m4a

# FLAC
ffmpeg -f lavfi -i "sine=frequency=440:duration=3" -c:a flac test.flac

# OGG
ffmpeg -f lavfi -i "sine=frequency=440:duration=3" -c:a libvorbis test.ogg
```

### Upload każdego formatu:
```
✅ test.wav  → Powinien działać
✅ test.mp3  → Powinien działać
✅ test.m4a  → Powinien działać ⭐ NOWE
✅ test.flac → Powinien działać
✅ test.ogg  → Powinien działać
```

### Nieprawidłowy format (test negatywny):
```bash
echo "fake audio" > test.txt
```

```
Upload test.txt:
❌ "Niewłaściwy typ pliku: test.txt"
```

---

## 📋 Test 4: Multiple Files Batch (3 minuty)

**1. Upload wielu plików jednocześnie:**
```
- Zaznacz 3-5 plików M4A/MP3/WAV
- Przeciągnij wszystkie na stronę
```

**2. WERYFIKACJA:**
```
✅ Wszystkie pliki w kolejce
✅ Podsumowanie: "Kolejka Plików (5)"
```

**3. Rozpocznij przetwarzanie**

**4. PODCZAS przetwarzania:**
```
✅ Banner: "Zadania przetwarzają się w tle"
✅ Każdy plik ma osobny progress bar
✅ Status aktualizuje się: "Przetwarzanie w tle..."
```

**5. Opuść stronę w połowie**
```
- Kliknij "Zobacz Historię"
- ✅ BRAK blokady!
```

**6. W Historii:**
```
✅ Widzisz wszystkie 5 zadań
✅ Niektóre "PROCESSING", niektóre "COMPLETED"
✅ Real-time updates
```

---

## 🎯 Expected Results Summary

### ✅ Upload M4A:
- [x] Plik akceptowany bez błędu
- [x] Backend wykrywa format (AAC codec)
- [x] Automatyczna konwersja do WAV
- [x] Przetwarzanie LUFS działa
- [x] Export do MP3/M4A/WAV
- [x] Quality warning jeśli lossy→lossy

### ✅ Background Processing:
- [x] Banner informacyjny pojawia się
- [x] BRAK popup "Opuść stronę?"
- [x] Można nawigować swobodnie
- [x] Link "Zobacz Historię" działa
- [x] Zadania dalej się przetwarzają
- [x] Real-time updates w Historii

---

## 🐛 Troubleshooting

### Problem: "Connection refused"
```bash
./manage.sh status
# Jeśli kontenery nie działają:
./manage.sh start
```

### Problem: Pliki nie przetwarzają się
```bash
# Sprawdź logi worker:
./manage.sh logs worker

# Sprawdź logi web:
./manage.sh logs web
```

### Problem: M4A dalej nie działa
```bash
# Restart kontenerów:
./manage.sh restart

# Lub rebuild:
./manage.sh rebuild
```

### Problem: Banner nie pokazuje się
```bash
# Hard refresh w przeglądarce:
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)

# Clear cache
```

### Problem: Celery nie działa
```bash
# Sprawdź Redis:
docker-compose exec redis redis-cli ping
# Powinno zwrócić: PONG

# Sprawdź worker logs:
./manage.sh logs worker
```

---

## 📊 Test Report Template

Po zakończeniu testów, wypełnij:

```
# TEST REPORT - M4A & Background Processing Fixes
Data: ___________
Tester: ___________

## Test 1: Upload M4A
- [ ] Plik M4A zaakceptowany
- [ ] Przetwarzanie zakończone sukcesem
- [ ] Wyniki poprawne (LUFS, Duration)
- [ ] Quality warning wyświetlone
Status: ✅ PASS / ❌ FAIL
Uwagi: _________________

## Test 2: Brak Blokady
- [ ] Banner pojawił się
- [ ] Brak popup przy opuszczeniu
- [ ] Link do Historii działa
- [ ] Zadania dalej się przetwarzają
Status: ✅ PASS / ❌ FAIL
Uwagi: _________________

## Test 3: Różne Formaty
- [ ] WAV: ___
- [ ] MP3: ___
- [ ] M4A: ___
- [ ] FLAC: ___
- [ ] OGG: ___
Status: ✅ PASS / ❌ FAIL
Uwagi: _________________

## Test 4: Batch Processing
- [ ] Wiele plików uploadowane
- [ ] Wszystkie przetworzone
- [ ] Historia aktualizowana
Status: ✅ PASS / ❌ FAIL
Uwagi: _________________

## Overall Status: ✅ PASS / ❌ FAIL
Recommended for production: YES / NO
```

---

## 🎉 Success Criteria

### ✅ Wszystko działa, jeśli:

1. **M4A Upload**
   - ✅ Brak błędu "Only WAV files supported"
   - ✅ Plik przetwarza się poprawnie
   - ✅ Wyniki są dostępne w Historii

2. **Background Processing**
   - ✅ Banner informacyjny wyświetla się
   - ✅ Brak popup przy próbie opuszczenia strony
   - ✅ Zadania przetwarzają się mimo opuszczenia strony
   - ✅ Real-time updates w Historii działają

3. **Multiple Formats**
   - ✅ Wszystkie 9 formatów są akceptowane
   - ✅ Quality warnings są wyświetlane prawidłowo

---

## 📞 Support

### Jeśli coś nie działa:

1. **Sprawdź logi:**
   ```bash
   ./manage.sh logs web
   ./manage.sh logs worker
   ```

2. **Restart:**
   ```bash
   ./manage.sh restart
   ```

3. **Check dokumentację:**
   - `FIXES_COMPLETE.md` - Szczegóły zmian
   - `UNIVERSAL_CONVERTER_COMPLETE.md` - Format support
   - `USER_GUIDE.md` - User documentation

---

**Happy Testing! 🎉**

Aplikacja powinna teraz działać płynnie z M4A i innymi formatami,
bez irytujących popup-ów podczas przetwarzania!

