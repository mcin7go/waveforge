# 🧪 WaveBulk - Manual Testing Guide

## Data: 2025-10-14

---

## 🎯 Co testujemy:

### QUICK WINS (5 funkcji):
1. AAC/M4A format
2. Extended bitrate (128k, 256k, VBR)
3. Sample rate selector
4. Fade in/out
5. Auto-trim silence

### PROFESSIONAL AUDIO PLAYER (9 funkcji):
6. Waveform visualization
7. Spectrogram
8. Live frequency analyzer
9. Phase correlation meter
10. A/B comparison
11. Smart markers
12. Zoom & controls
13. Timeline & minimap
14. Advanced playback

---

## 📋 STEP-BY-STEP TEST PLAN

### ✅ TEST 1: Quick Wins - Upload Options (5 min)

**Przejdź do:** http://localhost:5000/

1. **Zaloguj się** (lub zarejestruj nowe konto)
   - Email: test@test.com
   - Password: test123

2. **Kliknij "Upload"** w menu

3. **Sprawdź Format selector:**
   ```
   ☐ MP3 widoczny
   ☐ AAC/M4A widoczny (NEW!)
   ☐ WAV widoczny  
   ☐ FLAC widoczny
   ```

4. **Wybierz MP3, sprawdź Bitrate:**
   ```
   ☐ 320 kbps (Najwyższa)
   ☐ 256 kbps (Bardzo dobra) ← NEW!
   ☐ 192 kbps (Dobra)
   ☐ 128 kbps (Streaming) ← NEW!
   ☐ VBR V0 (Variable, najlepsza) ← NEW!
   ☐ VBR V2 (Variable, dobra) ← NEW!
   ```

5. **Sprawdź Sample Rate:**
   ```
   ☐ Oryginalna ← NEW!
   ☐ 44.1 kHz (CD)
   ☐ 48 kHz (Video) ← NEW!
   ☐ 88.2 kHz (Hi-Res) ← NEW!
   ☐ 96 kHz (Studio) ← NEW!
   ```

6. **Scroll w dół, sprawdź checkboxy:**
   ```
   ☐ ☑ Auto-trim ciszy (początek/koniec) ← NEW!
   ☐ ☑ Fade In/Out ← NEW!
   ```

7. **Kliknij "Fade In/Out", sprawdź inputs:**
   ```
   ☐ Fade In (sekundy): [2]
   ☐ Fade Out (sekundy): [2]
   ☐ Inputs się pokazują/ukrywają
   ```

**✅ RESULT:** Wszystkie 5 opcji widoczne i działają!

---

### ✅ TEST 2: Processing Test (10 min)

**Test AAC conversion:**

1. **Prześlij test.wav** (dowolny plik WAV)

2. **Ustaw opcje:**
   - Format: **AAC/M4A**
   - Bitrate: **192 kbps**
   - Sample Rate: **48 kHz**
   - ☑ Fade In/Out (1s / 2s)
   - ☑ Auto-trim silence
   - LUFS: **Spotify (-14)**

3. **Kliknij "Rozpocznij Przetwarzanie"**

4. **Poczekaj na ukończenie** (progress bar)

5. **Sprawdź wynik:**
   ```
   ☐ Status: COMPLETED
   ☐ Nazwa pliku: *.m4a (nie *.aac!)
   ☐ LUFS: ~-14.0
   ☐ Przycisk "Pobierz"
   ```

6. **Pobierz i sprawdź w ffprobe:**
   ```bash
   ffprobe plik.m4a
   # Check:
   # - Format: AAC
   # - Sample rate: 48000 Hz
   # - Bitrate: ~192k
   ```

**✅ RESULT:** AAC conversion działa!

---

### ✅ TEST 3: Professional Audio Player (15 min)

**Po przetworzeniu pliku:**

1. **Kliknij nazwę pliku** w History

2. **Scroll do "Profesjonalny Odtwarzacz Audio"**

3. **TEST: Podstawowy Player**
   ```
   ☐ Waveform widoczny (niebieskie fale)
   ☐ Minimap widoczny (mały overview)
   ☐ Timeline z czasem (0s, 1s, 2s...)
   ☐ Przyciski: ▶ ⏹
   ☐ Time display: 0:00 / X:XX
   ☐ Volume slider
   ☐ Speed selector (0.5x - 2x)
   ☐ Zoom slider (1x - 500x)
   ```

4. **KLIKNIJ ▶ (play):**
   ```
   ☐ Audio odtwarza się
   ☐ Progress bar się przesuwa
   ☐ Time aktualizuje się
   ☐ Ikona zmienia się na ⏸
   ```

5. **KLIKNIJ waveform (seek):**
   ```
   ☐ Playback przeskakuje do klikniętego miejsca
   ☐ Progress bar aktualizuje się
   ```

6. **TEST: Zoom**
   ```
   ☐ Przesuń slider Zoom na 50x
   ☐ Waveform się powiększa
   ☐ Zoom value pokazuje: 50x
   ☐ Scroll waveform w lewo/prawo
   ☐ Ustaw 500x - zobacz pojedyncze sample!
   ```

7. **TEST: Speed**
   ```
   ☐ Zmień Speed na 2x
   ☐ Audio odtwarza się szybciej
   ☐ Zmień na 0.5x
   ☐ Audio zwolnione
   ```

8. **TEST: Volume**
   ```
   ☐ Przesuń volume slider
   ☐ Głośność się zmienia
   ```

**✅ RESULT:** Podstawowy player działa!

---

### ✅ TEST 4: Spectrogram (5 min)

1. **Kliknij przycisk "📊 Spectrogram"**
   ```
   ☐ Przycisk highlightuje się (active)
   ☐ Pod waveform pojawia się spectrogram
   ☐ Heatmapa częstotliwości widoczna
   ☐ Wysokie częstotliwości na górze
   ☐ Niskie częstotliwości na dole
   ☐ Czas horyzontalnie
   ```

2. **KLIKNIJ ▶ i obserwuj:**
   ```
   ☐ Spectrogram "gra się" razem z audio
   ☐ Ciepłe kolory = więcej energii
   ☐ Zimne kolory = mniej energii
   ```

3. **Kliknij ponownie aby ukryć**
   ```
   ☐ Spectrogram znika
   ☐ Przycisk dezaktywuje się
   ```

**✅ RESULT:** Spectrogram działa!

---

### ✅ TEST 5: Frequency Analyzer (5 min)

1. **Kliknij "📈 Analizer częstotliwości"**
   ```
   ☐ Przycisk active
   ☐ Poniżej pojawia się sekcja z 2 kartami
   ☐ Lewa karta: Frequency Analyzer
   ☐ Canvas widoczny
   ```

2. **KLIKNIJ ▶ aby odtworzyć:**
   ```
   ☐ Bars zaczynają się ruszać (live!)
   ☐ Animacja 60fps, smooth
   ☐ Lewo = bas (czerwone)
   ☐ Środek = mids (zielone)
   ☐ Prawo = treble (niebieskie)
   ☐ Wysokość bars = energia na częstotliwości
   ```

3. **Obserwuj podczas playback:**
   ```
   ☐ Bars reagują na muzykę
   ☐ Bębny = wysokie bars w basie
   ☐ Wokale = wysokie bars w mid
   ☐ Cymbals = wysokie bars w treble
   ```

**✅ RESULT:** Frequency analyzer działa real-time!

---

### ✅ TEST 6: Phase Correlation Meter (5 min)

1. **Włącz analyzer (jeśli nie jest)**

2. **Prawa karta: Phase Correlation**
   ```
   ☐ Canvas widoczny
   ☐ Siatka (vertical + horizontal lines)
   ☐ Correlation value: X.XX
   ```

3. **KLIKNIJ ▶ i obserwuj:**
   ```
   ☐ Lissajous figure rysuje się
   ☐ Linia 45° = perfect stereo
   ☐ Pionowa = mono
   ☐ Figura się rusza w czasie rzeczywistym
   ☐ Correlation value aktualizuje się
   ```

4. **Interpretacja:**
   ```
   ☐ < 0.3 (green) = Good stereo ✅
   ☐ 0.3-0.7 (yellow) = Moderate
   ☐ > 0.7 (red) = Mono-like
   ```

**✅ RESULT:** Phase correlation działa!

---

### ✅ TEST 7: Smart Markers (3 min)

1. **Kliknij "📍 Markery"**
   ```
   ☐ Przycisk active
   ☐ Poniżej pojawia się legenda
   ☐ 6 rodzajów markers z kolorami
   ```

2. **Sprawdź waveform:**
   ```
   ☐ Tło waveform ma kolor (green/yellow/red)
   ☐ Kolor zależy od LUFS:
      • Green: -23 to -14 LUFS
      • Yellow: -14 to -10 LUFS
      • Red: > -10 LUFS
   ```

3. **Sprawdź legenda:**
   ```
   ☐ 🔴 True Peaks > -1dB
   ☐ ⚠️ Clipping Detected (migające)
   ☐ 🔇 Silence Sections
   ☐ LUFS OK/Border/High
   ```

**✅ RESULT:** Markers działają!

---

### ✅ TEST 8: A/B Comparison Mode (10 min)

1. **Kliknij "Porównanie A/B"** w mode switcher
   ```
   ☐ View zmienia się
   ☐ 2 waveforms obok siebie
   ☐ Lewy: "Przed" (orange)
   ☐ Prawy: "Po" (teal)
   ☐ Prawy ma border (active)
   ```

2. **KLIKNIJ ▶:**
   ```
   ☐ Aktywny player odtwarza się
   ☐ Time display aktualizuje się
   ```

3. **KLIKNIJ "🔄 Przełącz A/B":**
   ```
   ☐ Audio natychmiast przełącza się
   ☐ Drugi player zaczyna grać
   ☐ Border zmienia się
   ☐ Czas synchronizowany
   ```

4. **Słuchaj różnicy:**
   ```
   ☐ Przełączaj A/B kilka razy
   ☐ Słyszysz różnicę w LUFS?
   ☐ Słyszysz różnicę w jakości?
   ```

5. **Włącz Spectrogram na obu:**
   ```
   ☐ Oba spectrogramy widoczne
   ☐ Porównaj wizualnie różnice
   ```

**✅ RESULT:** A/B comparison działa!

---

### ✅ TEST 9: Combined Features (5 min)

**Ultimate test - wszystko naraz:**

1. **Mode: A/B Comparison**
2. **Włącz wszystkie toggles:**
   - ✅ Spectrogram
   - ✅ Frequency Analyzer
   - ✅ Phase Correlation
   - ✅ Markery

3. **KLIKNIJ ▶:**
   ```
   ☐ Oba waveforms z spectrogramem
   ☐ Frequency bars animowane
   ☐ Lissajous figure rysuje się
   ☐ Markers widoczne
   ☐ Wszystko działa synchronicznie
   ```

4. **Przełącz A/B kilka razy podczas playback:**
   ```
   ☐ Smooth transition
   ☐ Analyzers kontynuują
   ☐ No glitches
   ```

**✅ RESULT:** Wszystkie funkcje działają razem!

---

## 🐛 Znane Issues (Do sprawdzenia)

### Issue 1: Upload wymaga logowania
- **Expected:** Tak, Flask-Login @login_required
- **Fix:** N/A (security feature)

### Issue 2: A/B uses same file
- **Temporary:** Obie strony ładują przetworzony plik
- **Future:** Load original + processed
- **Location:** audio-player.js line 88
- **Fix:** Backend musi zwracać URL do obu plików

### Issue 3: Markers są symulowane
- **Current:** Markers based tylko na LUFS z page
- **Future:** Backend musi wysłać peak data
- **Fix:** Dodać peak_times[] do JSON

---

## 📊 Expected Results

### Upload Page:
```
Format: [MP3▼] → 4 opcje
Bitrate: [320k▼] → 6 opcji (4 NEW!)
Sample Rate: [44.1k▼] → 5 opcji (4 NEW!)
☑ Trim silence (NEW!)
☑ Fade In/Out (NEW!)
  └ Inputs: [2s] [2s]
```

### File Details Page:
```
┌─── Profesjonalny Odtwarzacz Audio ───┐
│ [Pojedynczy] [A/B] <-- modes         │
│ [📊] [📈] [🎯] [📍] <-- toggles      │
│ ┌────────────────────────────────┐   │
│ │ ▂▃▅▆█▆▅▃▂ <-- waveform         │   │
│ │ ━━━█━━━━━ <-- progress         │   │
│ └────────────────────────────────┘   │
│ ┌────────────────────────────────┐   │
│ │ ▂▃█▆▃▂ <-- minimap              │   │
│ └────────────────────────────────┘   │
│ [▶] [⏹] 0:23/1:45 🔊▬○ 1x 🔍5x    │
└────────────────────────────────────┘
```

Gdy włączysz wszystko:
```
+ Spectrogram pod waveform
+ 2 canvasy (Frequency + Phase)
+ Legenda markers (6 typów)
```

---

## ✅ Checklist - Kompletny Test

### Upload Page (Quick Wins):
- [ ] AAC/M4A format visible
- [ ] 128k bitrate visible
- [ ] 256k bitrate visible  
- [ ] VBR V0, V2 visible
- [ ] Sample Rate selector (5 opcji)
- [ ] Fade In/Out toggle + inputs
- [ ] Trim silence toggle
- [ ] Help texts wyświetlają się

### File Details (Audio Player):
- [ ] "Profesjonalny Odtwarzacz Audio" header
- [ ] Mode switcher (Single/A/B)
- [ ] 4 feature toggle buttons
- [ ] Waveform renders
- [ ] Minimap renders
- [ ] Play/Pause działa
- [ ] Seek działa (kliknij waveform)
- [ ] Volume działa
- [ ] Speed działa (0.5x-2x)
- [ ] Zoom działa (1x-500x)
- [ ] Time display aktualizuje się

### Advanced Features:
- [ ] Spectrogram toggle działa
- [ ] Spectrogram wyświetla się
- [ ] Frequency Analyzer toggle działa
- [ ] Frequency bars animują się
- [ ] Phase Correlation toggle działa
- [ ] Lissajous figure wyświetla się
- [ ] Correlation value aktualizuje się
- [ ] Markers toggle działa
- [ ] LUFS regions wyświetlają się
- [ ] Legend wyświetla się

### A/B Comparison:
- [ ] Przełącz na "Porównanie A/B"
- [ ] 2 waveforms obok siebie
- [ ] Lewy: "Przed" (orange)
- [ ] Prawy: "Po" (teal)
- [ ] Play działa
- [ ] Switch A/B działa
- [ ] Audio przełącza się natychmiast

### Translations:
- [ ] Przełącz na EN
- [ ] Wszystkie labels po angielsku
- [ ] Przełącz na PL
- [ ] Wszystkie labels po polsku

---

## 🎯 Performance Check

### Loading Times:
- [ ] Waveform loads < 2s
- [ ] Spectrogram loads < 3s
- [ ] Page interactive < 1s

### Smoothness:
- [ ] Waveform smooth (no lag)
- [ ] Frequency analyzer 60fps
- [ ] Phase correlation 60fps
- [ ] No freezing during playback

### Browser Compatibility:
- [ ] Chrome/Edge - test
- [ ] Firefox - test
- [ ] Safari - test (if available)

---

## 🎊 Success Criteria

**MINIMUM (Basic):**
- 20/30 tests pass
- Player loads and plays
- No console errors

**GOOD:**
- 25/30 tests pass
- All basic features work
- Minor visual issues OK

**PERFECT:**
- 30/30 tests pass
- All features work smoothly
- Professional appearance
- No bugs

---

## 📝 Notes & Observations

*Tutaj zapisz swoje uwagi podczas testów:*

```
Test 1 (Upload): 
  - 

Test 2 (Processing):
  - 

Test 3 (Audio Player):
  - 

Issues found:
  - 

Suggestions:
  - 
```

---

**Autor:** AI Assistant  
**Data:** 2025-10-14  
**Czas trwania testu:** ~45 min  
**Status:** Ready to test! 🚀
