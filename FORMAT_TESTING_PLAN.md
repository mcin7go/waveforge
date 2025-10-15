# 🎵 Format Testing Strategy - WaveBulk

**Data:** 2025-01-15  
**Cel:** Comprehensive testing of all supported audio formats

---

## 📊 Obecny Stan Testów

### ✅ Co mamy:
- `test_upload_accepts_multiple_formats` - testuje 9 formatów (MOCKED)
  - Sprawdza tylko czy upload przyjmuje format
  - **NIE testuje** rzeczywistej konwersji FFmpeg
  
### ❌ Co brakuje:
- Testy **end-to-end** konwersji format → format
- Weryfikacja jakości po konwersji
- Test real FFmpeg dla każdego formatu

---

## 🎯 Formaty do Przetestowania

### Priorytet 1: CORE Formats (Must Test)
Najczęściej używane - **obowiązkowo testować**:

1. **WAV** (lossless, standard)
   - Input: ✅ (już testowane)
   - Output: ✅ (już testowane)
   - Priority: **CRITICAL**

2. **MP3** (lossy, universal)
   - Input: ⚠️ (tylko upload mock)
   - Output: ✅ (testowane)
   - Priority: **HIGH**

3. **FLAC** (lossless, compressed)
   - Input: ⚠️ (tylko upload mock)
   - Output: ⚠️ (nie testowane)
   - Priority: **HIGH**

4. **AAC/M4A** (lossy, Apple/streaming)
   - Input: ⚠️ (tylko upload mock)
   - Output: ⚠️ (nie testowane)
   - Priority: **HIGH**

5. **OGG** (lossy, open-source)
   - Input: ⚠️ (tylko upload mock)
   - Output: ⚠️ (nie testowane)
   - Priority: **MEDIUM**

### Priorytet 2: EXTENDED Formats (Should Test)
Mniej popularne ale wspierane:

6. **AIFF** (lossless, Apple)
   - Input: ⚠️ (tylko upload mock)
   - Output: ⚠️ (nie testowane)
   - Priority: **MEDIUM**

7. **WMA** (lossy, Microsoft)
   - Input: ⚠️ (tylko upload mock)
   - Output: ⚠️ (nie testowane)
   - Priority: **LOW**

8. **OPUS** (lossy, modern)
   - Input: ⚠️ (tylko upload mock)
   - Output: ⚠️ (nie testowane)
   - Priority: **MEDIUM**

---

## 🧪 Test Strategy - Co Testować?

### Scenariusze Konwersji (10 najważniejszych):

#### Grupa A: Lossless → Lossy (najpopularniejsze)
1. **WAV → MP3** ✅ (już testowane)
2. **FLAC → MP3** ⚠️ (do dodania)
3. **WAV → AAC/M4A** ⚠️ (do dodania)
4. **FLAC → AAC/M4A** ⚠️ (do dodania)

#### Grupa B: Lossy → Lossless (re-encoding)
5. **MP3 → WAV** ⚠️ (do dodania)
6. **AAC → WAV** ⚠️ (do dodania)
7. **OGG → FLAC** ⚠️ (do dodania)

#### Grupa C: Lossy → Lossy (warning scenario)
8. **MP3 → AAC** ⚠️ (do dodania)
9. **AAC → MP3** ⚠️ (do dodania)
10. **OGG → MP3** ⚠️ (do dodania)

---

## 🎯 Rekomendowane 10 Formatów do Testowania

### Top 10 Test Cases (w kolejności ważności):

| # | Input | Output | Typ | Priorytet | Powód |
|---|-------|--------|-----|-----------|-------|
| 1 | WAV | MP3 | lossless→lossy | ✅ CRITICAL | Najpopularniejsza konwersja |
| 2 | FLAC | MP3 | lossless→lossy | 🔥 HIGH | Drugie miejsce |
| 3 | MP3 | WAV | lossy→lossless | 🔥 HIGH | Reverse, quality check |
| 4 | WAV | AAC | lossless→lossy | 🔥 HIGH | Apple/streaming standard |
| 5 | M4A | MP3 | lossy→lossy | ⚠️ MEDIUM | Warning scenario |
| 6 | FLAC | AAC | lossless→lossy | ⚠️ MEDIUM | Alternative to MP3 |
| 7 | AAC | FLAC | lossy→lossless | ⚠️ MEDIUM | Archiving scenario |
| 8 | OGG | MP3 | lossy→lossy | ⚠️ MEDIUM | Cross-format |
| 9 | AIFF | MP3 | lossless→lossy | 💡 LOW | Apple format |
| 10 | OPUS | WAV | lossy→lossless | 💡 LOW | Modern codec |

---

## 🔧 Jak Testować? - Implementacja

### Opcja 1: Real FFmpeg Tests (zalecane)
```python
@pytest.mark.parametrize("input_format,output_format,expected_quality", [
    ('wav', 'mp3', 'good'),      # lossless → lossy
    ('flac', 'mp3', 'good'),     # lossless → lossy
    ('mp3', 'wav', 'degraded'),  # lossy → lossless (quality warning)
    ('wav', 'aac', 'good'),      # lossless → lossy (streaming)
    ('m4a', 'mp3', 'warning'),   # lossy → lossy (quality warning)
])
def test_format_conversion_real_ffmpeg(input_format, output_format, expected_quality, ...):
    # 1. Create real audio file in input_format (generate with FFmpeg)
    # 2. Run process_audio_file task
    # 3. Verify output file exists and is valid
    # 4. Check LUFS/True Peak in result
    # 5. Verify quality_warning if lossy→lossy
```

### Opcja 2: Integration Tests
```python
def test_flac_to_mp3_conversion(app, test_user, db):
    # Generate real FLAC file
    input_file = generate_test_audio('flac', duration=2)
    
    # Process
    task = process_audio_file(...)
    
    # Verify
    assert task.status == 'COMPLETED'
    assert output exists
    assert is_valid_mp3(output)
    assert has_lufs_analysis(task.result_json)
```

---

## 🚨 Potencjalne Problemy do Wykrycia

### 1. Format Detection
- ❌ FFprobe fails to detect format
- ❌ Codec not recognized
- ✅ Test: Verify `_detect_audio_format()` for all formats

### 2. Conversion Errors
- ❌ FFmpeg conversion fails
- ❌ Unsupported codec parameters
- ❌ Container vs codec mismatch (e.g., AAC in M4A container)
- ✅ Test: End-to-end conversion for each format

### 3. LUFS Analysis
- ❌ pyloudnorm fails on specific format
- ❌ Silence/empty file edge case
- ✅ Test: LUFS measurement on all input formats

### 4. Metadata
- ❌ mutagen fails to read/write metadata
- ❌ Cover art embedding fails for specific format
- ✅ Test: Metadata preservation

### 5. Quality Warnings
- ❌ Lossy→lossy not flagged
- ❌ Bitrate degradation not detected
- ✅ Test: quality_warning field in result

---

## 📝 Rekomendowany Plan Implementacji

### Faza 1: Test Helpers (1 dzień)
```python
# backend/tests/helpers/audio_generator.py
def generate_test_audio(format, duration_seconds=2, sample_rate=44100):
    """Generate real audio file using FFmpeg for testing"""
    # Use FFmpeg to create valid audio file with sine wave
    pass

def verify_audio_format(filepath, expected_format):
    """Verify file is valid and in expected format"""
    pass

def extract_lufs_from_result(result_json):
    """Parse LUFS from task result"""
    pass
```

### Faza 2: Core Format Tests (2 dni)
Dodać do `test_tasks.py`:
```python
@pytest.mark.parametrize("input_ext,output_ext", [
    ('wav', 'mp3'),   # Test 1
    ('flac', 'mp3'),  # Test 2
    ('mp3', 'wav'),   # Test 3
    ('wav', 'aac'),   # Test 4
    ('m4a', 'mp3'),   # Test 5
])
def test_real_format_conversion(input_ext, output_ext, app, test_user, db):
    # Implementation
    pass
```

### Faza 3: Edge Cases (1 dzień)
- Bardzo krótkie pliki (<1s)
- Bardzo długie pliki (>5min)
- Niski bitrate (64kbps)
- Wysoki bitrate (320kbps)
- Mono vs Stereo
- Różne sample rates (22050, 44100, 48000, 96000)

---

## ⚡ Quick Win - Minimalna Implementacja

**Jeśli czas ograniczony, zrób przynajmniej to:**

### TOP 5 Must-Test Conversions:
1. ✅ WAV → MP3 (już jest)
2. ⚠️ **FLAC → MP3** (dodać)
3. ⚠️ **MP3 → WAV** (dodać - reverse)
4. ⚠️ **WAV → AAC** (dodać - streaming)
5. ⚠️ **M4A → MP3** (dodać - lossy→lossy warning)

### Kod (minimal):
```python
@pytest.mark.parametrize("input_format,output_format", [
    ('flac', 'mp3'),
    ('mp3', 'wav'),
    ('wav', 'aac'),
    ('m4a', 'mp3'),
])
def test_critical_format_conversions(input_format, output_format, app, test_user, db):
    # Generate test file
    test_file = create_sine_wave_file(input_format, duration=2)
    
    # Create task
    audio_file = AudioFile(...)
    task = ProcessingTask(...)
    db.session.add_all([audio_file, task])
    db.session.commit()
    
    # Process
    options = {'format': output_format, 'limit_true_peak': True}
    result = process_audio_file.apply(args=[task.id, test_file, f'test.{input_format}', test_user.id, options])
    
    # Verify
    db.session.refresh(task)
    assert task.status == 'COMPLETED'
    
    result_data = json.loads(task.result_json)
    assert 'loudness_lufs' in result_data
    assert 'true_peak_db' in result_data
    
    # Check quality warning for lossy→lossy
    if input_format in LOSSY_FORMATS and output_format in LOSSY_FORMATS:
        assert result_data.get('quality_warning') is not None
```

---

## 🎓 Wnioski i Rekomendacje

### 1. Obecny stan:
- ✅ Upload validation działa dla 9 formatów
- ⚠️ Real conversion testowana tylko dla WAV
- ❌ Brak testów dla większości formatów

### 2. Ryzyko:
- 🔴 **WYSOKIE:** FLAC, AAC/M4A mogą nie działać w production
- 🟡 **ŚREDNIE:** OGG, AIFF, OPUS - mniej krytyczne
- 🟢 **NISKIE:** WAV, MP3 - już testowane

### 3. Rekomendacja:
**Dodaj minimum 4-5 real FFmpeg tests dla core formatów**

Dlaczego?
- FFmpeg może mieć różne wersje
- Kodeki mogą być missing (AAC, OPUS)
- Container vs codec issues (M4A/AAC)
- Metadata handling różni się per format

### 4. Timeline:
- **Quick win:** 4 godziny (TOP 5 tests)
- **Complete:** 2-3 dni (wszystkie 10 + edge cases)
- **Comprehensive:** 1 tydzień (helpers + all formats + CI)

---

## 🚀 Następne Kroki

### Immediate (dzisiaj):
1. Dodać TOP 5 real conversion tests
2. Generate test audio files (FFmpeg sine wave)
3. Verify FFmpeg codecs available in Docker

### Short-term (ten tydzień):
1. Dodać wszystkie 10 conversions
2. Edge case testing
3. Quality warning verification
4. CI integration

### Long-term (przyszłość):
1. Performance benchmarks
2. Large file tests (>100MB)
3. Concurrent processing tests
4. Format-specific metadata tests

---

## 💡 Propozycja: Generator Audio dla Testów

```python
# backend/tests/helpers/audio_generator.py
import subprocess
import tempfile
import os

def generate_sine_wave(format, duration=2, frequency=440, sample_rate=44100):
    """
    Generate test audio file with sine wave using FFmpeg.
    
    Args:
        format: 'wav', 'mp3', 'flac', 'aac', 'm4a', 'ogg', 'opus', etc.
        duration: Length in seconds
        frequency: Tone frequency in Hz (440 = A4)
        sample_rate: Sample rate in Hz
    
    Returns:
        Path to generated file
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False)
    output_path = temp_file.name
    temp_file.close()
    
    # FFmpeg command to generate sine wave
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f'sine=frequency={frequency}:duration={duration}:sample_rate={sample_rate}',
        '-ac', '2',  # stereo
    ]
    
    # Format-specific parameters
    if format == 'mp3':
        cmd.extend(['-codec:a', 'libmp3lame', '-b:a', '320k'])
    elif format == 'flac':
        cmd.extend(['-codec:a', 'flac'])
    elif format in ['aac', 'm4a']:
        cmd.extend(['-codec:a', 'aac', '-b:a', '256k'])
    elif format == 'ogg':
        cmd.extend(['-codec:a', 'libvorbis', '-q:a', '5'])
    elif format == 'opus':
        cmd.extend(['-codec:a', 'libopus', '-b:a', '128k'])
    elif format == 'wma':
        cmd.extend(['-codec:a', 'wmav2', '-b:a', '192k'])
    elif format == 'aiff':
        cmd.extend(['-codec:a', 'pcm_s16be'])
    # WAV default
    
    cmd.append(output_path)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")
    
    return output_path
```

---

## 📋 Checklist Implementacji

### Pre-work:
- [ ] Sprawdź dostępne kodeki w Docker: `ffmpeg -codecs`
- [ ] Test FFmpeg sine wave generation
- [ ] Utworzyć `tests/helpers/audio_generator.py`

### Core Tests (TOP 5):
- [ ] Test 1: FLAC → MP3
- [ ] Test 2: MP3 → WAV  
- [ ] Test 3: WAV → AAC
- [ ] Test 4: M4A → MP3 (warning)
- [ ] Test 5: AAC → FLAC

### Extended Tests (5 more):
- [ ] Test 6: OGG → MP3
- [ ] Test 7: FLAC → AAC
- [ ] Test 8: AIFF → MP3
- [ ] Test 9: OPUS → WAV
- [ ] Test 10: WMA → MP3

### Verification:
- [ ] All 10 tests pass
- [ ] Quality warnings work
- [ ] LUFS calculated for all
- [ ] Metadata preserved where possible
- [ ] No FFmpeg errors in logs

---

## 🎯 Pytania do Rozważenia

### 1. Które formaty są najbardziej krytyczne?
**Odpowiedź:** WAV, MP3, FLAC, AAC/M4A - te 4 to 90% use cases

### 2. Czy testować wszystkie kombinacje?
**Odpowiedź:** NIE - to 9×9 = 81 kombinacji. Wybierz 10-15 najważniejszych.

### 3. Real files czy generated?
**Odpowiedź:** Generated (FFmpeg sine wave) - szybsze, powtarzalne, bez copyright issues

### 4. Jak długie pliki?
**Odpowiedź:** 2 sekundy dla unit tests, 10-30s dla integration

### 5. Czy testować metadata?
**Odpowiedź:** TAK dla formatów wspierających (MP3, FLAC, M4A). NIE dla WAV.

### 6. Czy testować edge cases?
**Odpowiedź:** TAK:
- Mono vs Stereo
- Różne sample rates (22050, 44100, 48000)
- Niski bitrate (64kbps)
- Wysoki bitrate (320kbps)
- Bardzo krótkie (<1s)

---

## 💰 Koszt/Benefit Analysis

### Minimalna opcja (TOP 5):
- **Czas:** 4-6 godzin
- **Testy:** 5 conversions
- **Coverage:** 70% real-world scenarios
- **Benefit:** 🟢 HIGH - wykryje większość problemów

### Średnia opcja (TOP 10):
- **Czas:** 1-2 dni
- **Testy:** 10 conversions + edge cases
- **Coverage:** 90% real-world scenarios  
- **Benefit:** 🟢 VERY HIGH - comprehensive coverage

### Maksymalna opcja (ALL):
- **Czas:** 1 tydzień
- **Testy:** 15-20 conversions + all edge cases + benchmarks
- **Coverage:** 95%+ wszystkich scenariuszy
- **Benefit:** 🟡 MEDIUM - diminishing returns

---

## 🎯 Moja Rekomendacja

**Zrób TOP 5 jako minimum viable:**

1. **FLAC → MP3** (najpopularniejsza po WAV→MP3)
2. **MP3 → WAV** (reverse, quality check)
3. **WAV → AAC** (streaming standard)
4. **M4A → MP3** (test lossy→lossy warning)
5. **AAC → FLAC** (archiving scenario)

**Dlaczego te 5?**
- Pokrywają wszystkie scenariusze (lossless→lossy, lossy→lossless, lossy→lossy)
- Testują najczęstsze use cases (MP3, FLAC, AAC)
- Weryfikują quality warnings
- Zajmą ~4-6 godzin
- Wykryją 80% potencjalnych problemów

**Co pomiń na razie:**
- OGG, OPUS, WMA - mniej używane
- AIFF - similar to WAV
- Exotic combinations

---

**Pytanie do Ciebie:**
Czy chcesz:
- **A) Quick Win** - TOP 5 tests (~4-6h)
- **B) Comprehensive** - TOP 10 tests (~1-2 dni)
- **C) Full Coverage** - ALL formats + edge cases (~1 tydzień)

Jaka jest Twoja preferencja?

