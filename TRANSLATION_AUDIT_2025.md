# 🌍 Translation Audit - Styczeń 2025

**Data:** 2025-01-15  
**Status:** Planning Phase  
**Cel:** Dodanie tłumaczeń EN dla nowych stron (Help, Terms, Privacy)

---

## 📊 Stan Obecny

### ✅ Już przetłumaczone (z października 2024):
- `index.html` - Homepage
- `pricing.html` - Cennik
- `login.html` / `register.html` - Auth
- `dashboard.html` - Dashboard
- `history.html` - Historia
- `file_details.html` - Szczegóły pliku
- `upload_audio.html` - Upload
- `subscribe.html` - Subskrypcja
- `admin_*.html` - Panel admina
- `base.html` / `base_sidebar.html` - Layout

**Statystyki (październik 2024):**
- Total strings: 179
- EN coverage: 100%
- PL coverage: 100%

---

## 🆕 Nowe strony wymagające tłumaczenia:

### 1. **help.html** (Dodana: 15.01.2025)
   - **Szacunkowa liczba stringów:** ~80-100
   - **Priorytet:** WYSOKI
   - **Sekcje:**
     - Przegląd aplikacji
     - Obsługiwane formaty (lossless/lossy)
     - Główne funkcje
     - Analiza techniczna (LUFS, True Peak)
     - WaveSurfer v7 features
     - Footer

### 2. **terms.html** (Dodana: 15.01.2025)
   - **Szacunkowa liczba stringów:** ~150-200
   - **Priorytet:** KRYTYCZNY (wymagane przed produkcją)
   - **Sekcje (13):**
     1. Definicje
     2. Postanowienia ogólne
     3. Rejestracja i konto
     4. Plany i płatności
     5. Korzystanie z serwisu
     6. Prawa i obowiązki użytkownika
     7. Przetwarzanie plików audio
     8. Polityka zwrotów
     9. Odpowiedzialność
     10. Własność intelektualna
     11. Zakaz nadużyć
     12. Zmiany regulaminu
     13. Postanowienia końcowe

### 3. **privacy.html** (Dodana: 15.01.2025)
   - **Szacunkowa liczba stringów:** ~180-220
   - **Priorytet:** KRYTYCZNY (GDPR requirement)
   - **Sekcje (12):**
     1. Wprowadzenie
     2. Administrator danych
     3. Jakie dane zbieramy
     4. Jak wykorzystujemy dane
     5. Podstawa prawna (GDPR)
     6. Udostępnianie danych
     7. Przechowywanie danych
     8. Bezpieczeństwo danych
     9. Prawa użytkownika (GDPR)
     10. Cookies policy
     11. Zmiany w polityce
     12. Kontakt

---

## 🎯 Plan Tłumaczeń - Etapy

### ETAP 1: help.html (~80-100 strings)
**Czas:** 1-2 godziny  
**Trudność:** ŁATWA

Struktura:
```
- Nagłówki sekcji (6)
- Feature descriptions (10-15)
- Format explanations (20-25)
- WaveSurfer features (30-35)
- UI elements (10-15)
```

### ETAP 2: terms.html (~150-200 strings)
**Czas:** 3-4 godziny  
**Trudność:** WYSOKA (legal language)

Struktura:
```
- Table of Contents (13)
- Section headers (13)
- Legal paragraphs (100-120)
- List items (40-50)
- UI elements (10)
```

**⚠️ UWAGA:**
- Język prawniczy wymaga precyzji
- Zalecana konsultacja z prawnikiem dla wersji EN
- Niektóre terminy mają ustalone odpowiedniki prawne

### ETAP 3: privacy.html (~180-220 strings)
**Czas:** 4-5 godzin  
**Trudność:** BARDZO WYSOKA (GDPR compliance)

Struktura:
```
- Table of Contents (12)
- Section headers (12)
- GDPR articles references (15-20)
- Data retention tables (10-15)
- Legal paragraphs (120-140)
- UI elements + badges (10-15)
```

**⚠️ UWAGA:**
- Musi być zgodny z GDPR (też w EN)
- Terminy GDPR mają oficjalne tłumaczenia
- Konsultacja prawna ZALECANA

---

## 📋 Szczegółowy Checklist

### Pre-Translation:
- [ ] Backup istniejących plików .po
- [ ] Utworzenie gałęzi git: `translations-2025-01`
- [ ] Przygotowanie workspace dla tłumaczy

### Extraction:
- [ ] Uruchomienie `pybabel extract`
- [ ] Weryfikacja czy wszystkie nowe teksty zostały złapane
- [ ] Update plików .po: `pybabel update`

### Translation (per etap):
- [ ] **ETAP 1:** help.html translations
  - [ ] Tłumaczenie wszystkich stringów
  - [ ] Weryfikacja context
  - [ ] Test na UI
  
- [ ] **ETAP 2:** terms.html translations
  - [ ] Tłumaczenie legal language
  - [ ] Konsultacja prawna (optional ale zalecane)
  - [ ] Weryfikacja terminologii
  - [ ] Test na UI
  
- [ ] **ETAP 3:** privacy.html translations
  - [ ] Tłumaczenie GDPR terms
  - [ ] Użycie oficjalnych tłumaczeń artykułów GDPR
  - [ ] Konsultacja prawna (ZALECANE)
  - [ ] Test na UI

### Compilation & Testing:
- [ ] Kompilacja: `pybabel compile`
- [ ] Restart aplikacji
- [ ] Test wszystkich 3 stron w EN
- [ ] Test wszystkich 3 stron w PL
- [ ] Screenshot verification
- [ ] Cross-browser testing

### Final:
- [ ] Code review
- [ ] Git commit z opisem
- [ ] Update TRANSLATIONS_COMPLETE.md
- [ ] Dokumentacja dla przyszłych tłumaczy

---

## 🔧 Workflow Techniczny

### 1. Przygotowanie środowiska:
```bash
cd backend
source venv/bin/activate  # lub docker exec
```

### 2. Ekstrakcja nowych stringów:
```bash
pybabel extract -F babel.cfg -k _ -o messages.pot app/
```

### 3. Update istniejących .po:
```bash
pybabel update -i messages.pot -d app/translations
```

### 4. Edycja plików .po:
```bash
# Plik do edycji:
app/translations/en/LC_MESSAGES/messages.po

# Szukaj pustych msgstr:
grep -A 1 'msgid.*help\|terms\|privacy' app/translations/en/LC_MESSAGES/messages.po | grep 'msgstr ""'
```

### 5. Kompilacja:
```bash
pybabel compile -d app/translations
```

### 6. Restart:
```bash
cd ../..
./manage.sh restart
```

---

## 📝 Template Tłumaczenia

### Format w .po:
```po
# help.html:42
msgid "Co to jest WaveBulk?"
msgstr "What is WaveBulk?"

# terms.html:15
msgid "Definicje"
msgstr "Definitions"

# privacy.html:89
msgid "Podstawa prawna przetwarzania (GDPR)"
msgstr "Legal basis for processing (GDPR)"
```

### Specjalne przypadki:

#### 1. Multi-line strings:
```po
msgid ""
"WaveBulk to profesjonalna aplikacja do konwersji i analizy plików audio, "
"zaprojektowana dla muzyków, producentów i audiofilów."
msgstr ""
"WaveBulk is a professional application for audio file conversion and "
"analysis, designed for musicians, producers, and audiophiles."
```

#### 2. Variables:
```po
#, python-format
msgid "Plan \"%(plan_name)s\" został zarchiwizowany."
msgstr "Plan \"%(plan_name)s\" has been archived."
```

#### 3. Escaped characters (%%):
```po
msgid "nie gwarantuje 100%% dostępności"
msgstr "does not guarantee 100%% availability"
```

---

## 🎓 Terminologia Kluczowa

### Tech Terms (nie tłumaczymy):
- WaveSurfer v7
- LUFS, True Peak
- FFmpeg, pyloudnorm
- Stripe, SendGrid
- GDPR
- Docker, PostgreSQL

### Legal Terms (standardowe tłumaczenia):
| Polski | English |
|--------|---------|
| Regulamin | Terms of Service |
| Polityka Prywatności | Privacy Policy |
| Administrator danych | Data Controller |
| Przetwarzanie danych | Data Processing |
| Zgoda | Consent |
| Prawo do usunięcia | Right to Erasure |
| Prawo do przenoszenia | Right to Data Portability |
| Organ nadzorczy | Supervisory Authority |

### GDPR Articles (oficjalne):
- Art. 6 ust. 1 lit. a GDPR → Art. 6(1)(a) GDPR
- Art. 15 GDPR → Art. 15 GDPR (Right of Access)
- Art. 17 GDPR → Art. 17 GDPR (Right to Erasure)

---

## ⚠️ Uwagi i Ostrzeżenia

### 1. Legal Compliance:
- **Terms of Service:** Wersja EN też musi być prawnie binding
- **Privacy Policy:** GDPR dotyczy też wersji angielskiej
- **Zalecenie:** Konsultacja z prawnikiem dla obu dokumentów

### 2. Context Awareness:
- Niektóre stringi pojawiają się w różnych kontekstach
- Sprawdzaj referencje w komentarzach `#: file.html:line`
- Test na prawdziwym UI przed zatwierdzeniem

### 3. Length Considerations:
- Polska wersja często dłuższa niż angielska
- Sprawdź czy tekst mieści się w UI (szczególnie przyciski)
- Mobile testing jest obowiązkowy

### 4. Consistency:
- Używaj tych samych terminów w całej aplikacji
- Sprawdź istniejące tłumaczenia w messages.po
- Nie wymyślaj nowych tłumaczeń dla już istniejących terminów

---

## 📈 Szacowany Czas i Priorytet

| Etap | Strona | Strings | Czas | Priorytet | Trudność |
|------|--------|---------|------|-----------|----------|
| 1 | help.html | ~90 | 2h | WYSOKI | ⭐⭐ |
| 2 | terms.html | ~180 | 4h | KRYTYCZNY | ⭐⭐⭐⭐ |
| 3 | privacy.html | ~200 | 5h | KRYTYCZNY | ⭐⭐⭐⭐⭐ |
| **TOTAL** | | **~470** | **11h** | | |

### Resource Requirements:
- **Tłumacz:** 1 osoba z dobrą znajomością EN/PL + legal terms
- **Prawnik (optional):** Review Terms + Privacy (EN/PL)
- **Tester:** 1 osoba do weryfikacji UI
- **Timeline:** 3-5 dni roboczych (z review)

---

## 🎯 Success Criteria

### Must Have:
- ✅ Wszystkie stringi z help.html przetłumaczone
- ✅ Wszystkie stringi z terms.html przetłumaczone
- ✅ Wszystkie stringi z privacy.html przetłumaczone
- ✅ Brak pustych `msgstr ""` w messages.po
- ✅ Kompilacja bez błędów
- ✅ Test switching EN ↔ PL działa
- ✅ UI wyglada dobrze w obu językach

### Should Have:
- ✅ Legal review (prawnik)
- ✅ Native speaker review (EN)
- ✅ Screenshot comparison PL vs EN
- ✅ Mobile testing

### Nice to Have:
- ✅ Automated testing (check empty translations)
- ✅ CI/CD integration
- ✅ Translation memory dla przyszłości

---

## 🚀 Next Steps

1. **Backup:** `git checkout -b translations-2025-01`
2. **Extract:** Run pybabel extract
3. **Translate:** Start with ETAP 1 (help.html)
4. **Review:** Test on staging
5. **Iterate:** ETAP 2 → ETAP 3
6. **Deploy:** Merge to main po approval

---

**Autor:** AI Assistant  
**Data utworzenia:** 2025-01-15  
**Ostatnia aktualizacja:** 2025-01-15  
**Status:** Planning Complete - Ready to Execute

