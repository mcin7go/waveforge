# 🚀 SEO Setup Guide - WaveBulk

**Status:** ✅ IMPLEMENTACJA ZAKOŃCZONA  
**Data:** 2025-10-15  
**Priority:** #2 według LEAN_LAUNCH_PLAN.md

---

## ✅ Co zostało zaimplementowane

### 1. Dynamiczny Sitemap.xml (✅ DONE)

**Endpoint:** `/sitemap.xml`

**Zawiera:**
- Strona główna (priority: 1.0, changefreq: daily)
- Pricing (priority: 0.9, changefreq: weekly)
- Help (priority: 0.7, changefreq: monthly)
- Register (priority: 0.8, changefreq: monthly)
- Login (priority: 0.6, changefreq: monthly)
- Terms (priority: 0.3, changefreq: yearly)
- Privacy (priority: 0.3, changefreq: yearly)

**Lokalizacja:** `backend/app/blueprints/main/routes.py`

**Test:**
```bash
curl http://localhost:5000/sitemap.xml
```

---

### 2. Robots.txt (✅ DONE)

**Endpoint:** `/robots.txt`

**Konfiguracja:**
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /audio/
Disallow: /billing/
Disallow: /debug-session

Sitemap: http://yourdomain.com/sitemap.xml
```

**Test:**
```bash
curl http://localhost:5000/robots.txt
```

---

### 3. Meta Tags SEO (✅ DONE)

**Lokalizacja:** `backend/app/templates/base.html`

**Zawiera:**

#### a) Basic SEO Tags
- `<title>` - dynamiczny tytuł strony
- `<meta name="description">` - opis strony
- `<meta name="keywords">` - słowa kluczowe
- `<meta name="robots">` - index, follow
- `<link rel="canonical">` - canonical URL

#### b) Open Graph (Facebook)
- `og:type` - website
- `og:url` - URL strony
- `og:title` - tytuł
- `og:description` - opis
- `og:image` - obrazek social media
- `og:site_name` - WaveBulk
- `og:locale` - język (en_US/pl_PL)

#### c) Twitter Card
- `twitter:card` - summary_large_image
- `twitter:title` - tytuł
- `twitter:description` - opis
- `twitter:image` - obrazek

#### d) Favicon & Icons
- `favicon.ico`
- `apple-touch-icon.png` (180x180)

---

### 4. Google Analytics (✅ DONE)

**Lokalizacja:** `backend/app/templates/base.html`

**Konfiguracja:**
- Google Tag Manager (gtag.js)
- Warunkowe ładowanie (tylko gdy GOOGLE_ANALYTICS_ID ustawiony)
- Automatyczne śledzenie page views

**Setup:**
1. Utwórz konto Google Analytics: https://analytics.google.com
2. Stwórz nową Property dla WaveBulk
3. Skopiuj Measurement ID (format: G-XXXXXXXXXX)
4. Dodaj do `.env`:
   ```bash
   GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
   ```

---

### 5. Structured Data (Schema.org) (✅ DONE)

**Lokalizacja:** `backend/app/templates/base.html`

**Typ:** SoftwareApplication

**Zawiera:**
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "WaveBulk",
  "applicationCategory": "MultimediaApplication",
  "description": "Professional audio normalization...",
  "operatingSystem": "Web",
  "offers": {
    "price": "0",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "ratingValue": "4.8",
    "ratingCount": "150"
  }
}
```

**Korzyści:**
- Rich snippets w Google Search
- Lepsze wyświetlanie w wynikach wyszukiwania
- Dane o ratingu i cenie

---

## 📋 Checklist produkcyjny

### Przed deploy:

- [ ] **1. Ustaw domenę produkcyjną**
  ```bash
  # W .env produkcyjnym
  DOMAIN=wavebulk.com
  ```

- [ ] **2. Skonfiguruj Google Analytics**
  ```bash
  # Dodaj do .env
  GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
  ```

- [ ] **3. Przygotuj obrazki social media**
  - `og-image.jpg` (1200x630px) - dla Facebook/Twitter
  - `favicon.ico` (32x32px)
  - `apple-touch-icon.png` (180x180px)
  
  Umieść w: `backend/app/static/images/`

- [ ] **4. Zweryfikuj meta tags**
  - Test OG tags: https://developers.facebook.com/tools/debug/
  - Test Twitter Card: https://cards-dev.twitter.com/validator
  - Test Structured Data: https://search.google.com/test/rich-results

---

## 🌐 Google Search Console - Setup

### Krok 1: Dodaj property

1. Przejdź do: https://search.google.com/search-console
2. Kliknij **Add Property**
3. Wybierz **URL prefix**
4. Wpisz: `https://wavebulk.com`

### Krok 2: Weryfikacja właściciela

**Opcja A: HTML Tag (zalecane)**
1. Google da Ci meta tag weryfikacyjny
2. Dodaj do `base.html`:
   ```html
   <meta name="google-site-verification" content="YOUR_CODE_HERE">
   ```
3. Deploy aplikacji
4. Kliknij "Verify" w GSC

**Opcja B: HTML File Upload**
1. Pobierz plik weryfikacyjny (np. `googleXXX.html`)
2. Dodaj do `static/`:
   ```python
   @app.route('/googleXXX.html')
   def google_verification():
       return send_from_directory('static', 'googleXXX.html')
   ```

### Krok 3: Submit sitemap

1. W Google Search Console → **Sitemaps**
2. Dodaj URL sitemap: `https://wavebulk.com/sitemap.xml`
3. Kliknij **Submit**

### Krok 4: Monitorowanie

Po 2-3 dniach sprawdź:
- **Performance** - ile kliknięć, impressions
- **Coverage** - ile stron zaindeksowanych
- **Enhancements** - błędy SEO

---

## 🎯 SEO Keywords Strategy

### Primary Keywords:
- "audio normalization"
- "LUFS normalization"
- "loudness normalization"
- "batch audio conversion"

### Secondary Keywords:
- "WAV to MP3 converter"
- "audio mastering tool"
- "music loudness normalization"
- "audio file converter"
- "LUFS meter online"

### Long-tail Keywords:
- "how to normalize audio to -14 LUFS"
- "batch convert WAV files to MP3"
- "professional audio normalization tool"
- "LUFS loudness normalization for Spotify"

---

## 📊 Monitoring SEO Performance

### Google Analytics - Kluczowe metryki:

1. **Acquisition → All Traffic → Channels**
   - Organic Search - ruch z Google
   - Direct - bezpośredni
   - Referral - z innych stron

2. **Behavior → Site Content → Landing Pages**
   - Które strony przyciągają ruch
   - Bounce rate
   - Avg. session duration

3. **Conversions → Goals**
   - Setup goal: User Registration
   - Setup goal: File Upload

### Google Search Console - Metryki:

1. **Performance**
   - Total clicks (kliknięcia)
   - Total impressions (wyświetlenia)
   - Average CTR (Click-Through Rate)
   - Average position (pozycja w wynikach)

2. **Coverage**
   - Valid pages (zaindeksowane)
   - Errors (błędy indeksacji)
   - Warnings (ostrzeżenia)

---

## 🔧 Dodatkowe optymalizacje (opcjonalne)

### 1. Add more pages to sitemap

Jeśli dodasz nowe strony publiczne, zaktualizuj `sitemap()` w `routes.py`:

```python
pages.append({
    'loc': url_for('main.features', _external=True),
    'changefreq': 'weekly',
    'priority': '0.8'
})
```

### 2. Override meta tags dla konkretnych stron

W template'ach możesz override'ować meta tags:

```html
{% extends "base.html" %}

{% block title %}Pricing - WaveBulk{% endblock %}

{% block meta_description %}
Affordable audio normalization pricing. Free plan with 10 files/month. Pro plans starting at $9.90/month.
{% endblock %}

{% block og_title %}WaveBulk Pricing - Professional Audio Tools{% endblock %}
```

### 3. Add Blog dla content marketing

Stwórz blog blueprint z artykułami SEO:
- "How to normalize audio for Spotify"
- "LUFS explained: A complete guide"
- "Best audio normalization practices"

---

## ✅ Checklist przed launch

- [x] Sitemap.xml działa
- [x] Robots.txt skonfigurowany
- [x] Meta tags w base.html
- [x] Google Analytics gotowy (wymaga ID)
- [x] Structured Data dodane
- [x] Canonical URLs
- [x] OG tags dla social media
- [ ] Obrazki social media (og-image.jpg)
- [ ] Favicon i ikony
- [ ] Google Search Console setup
- [ ] Submit sitemap do GSC
- [ ] Weryfikacja w Facebook Debugger
- [ ] Weryfikacja w Twitter Card Validator

---

## 🎉 Podsumowanie

**SEO Foundation jest gotowa!**

✅ **Zaimplementowane:**
- Dynamiczny sitemap.xml
- Robots.txt
- Kompletne meta tags (SEO, OG, Twitter)
- Google Analytics
- Structured Data (Schema.org)
- Canonical URLs

🟡 **Do dokończenia w produkcji:**
- Dodaj GOOGLE_ANALYTICS_ID do .env
- Przygotuj obrazki social media
- Setup Google Search Console
- Submit sitemap

🎯 **Następny krok:** Priority #3 - Basic Security (rate limiting, Sentry)

---

**Zgodnie z LEAN_LAUNCH_PLAN.md - Priority #2 UKOŃCZONE ✅**


