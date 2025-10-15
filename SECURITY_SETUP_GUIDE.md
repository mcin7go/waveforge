# 🔒 Security Setup Guide - WaveBulk

**Status:** ✅ IMPLEMENTACJA ZAKOŃCZONA  
**Data:** 2025-10-15  
**Priority:** #3 według LEAN_LAUNCH_PLAN.md

---

## ✅ Co zostało zaimplementowane

### 1. Rate Limiting (✅ DONE)

**Biblioteka:** Flask-Limiter 3.5.0  
**Storage:** Redis

**Limity globalne:**
- 200 requests per day (per IP)
- 50 requests per hour (per IP)

**Limity specyficzne dla endpoints:**

#### Login (`/login`)
```python
@limiter.limit("5 per minute")
```
- **5 prób logowania na minutę**
- Ochrona przed brute force attacks
- Reset: co minutę

#### Register (`/register`)
```python
@limiter.limit("10 per hour")
```
- **10 rejestracji na godzinę**
- Ochrona przed spam/bot registrations
- Reset: co godzinę

#### Password Reset (`/reset_password_request`)
```python
@limiter.limit("3 per hour")
```
- **3 próby resetu hasła na godzinę**
- Ochrona przed email flooding
- Reset: co godzinę

**Lokalizacja:** 
- Config: `backend/app/__init__.py`
- Implementation: `backend/app/blueprints/auth/routes.py`

---

### 2. Sentry Error Tracking (✅ DONE)

**Biblioteka:** sentry-sdk[flask] 2.19.2

**Integracje:**
- FlaskIntegration - śledzenie błędów Flask
- CeleryIntegration - śledzenie błędów Celery tasks

**Konfiguracja:**
```python
sentry_sdk.init(
    dsn=app.config['SENTRY_DSN'],
    integrations=[FlaskIntegration(), CeleryIntegration()],
    traces_sample_rate=0.1,    # 10% transakcji dla performance monitoring
    profiles_sample_rate=0.1,  # 10% dla profiling
)
```

**Aktywacja:**
- Tylko w produkcji (gdy `SENTRY_DSN` ustawiony)
- Nie aktywuje się w trybie testowym

**Setup:**
1. Utwórz konto: https://sentry.io
2. Stwórz nowy Project (Python/Flask)
3. Skopiuj DSN
4. Dodaj do `.env`:
   ```bash
   SENTRY_DSN=https://xxxxx@xxxxxx.ingest.sentry.io/xxxxxx
   ```

**Co Sentry śledzi:**
- Błędy aplikacji (exceptions)
- Nieudane requesty (500 errors)
- Performance issues
- Celery task failures
- User context (authenticated user ID)

---

### 3. Strong SECRET_KEY (✅ DONE)

**Generator:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Przykładowy klucz:**
```
cQ7apiqay_x55nqFSQD8jCJzUFRA3HYffLq_kD_ASmQ
```

**Wymagania:**
- Minimum 32 znaki
- Kryptograficznie bezpieczny (secrets.token_urlsafe)
- Unikalny dla każdego środowiska (dev/staging/production)

**Używany do:**
- Podpisywania sesji użytkownika
- Podpisywania ciasteczek Flask
- Tokenów resetowania hasła
- CSRF protection

**⚠️ WAŻNE:**
- NIE COMMITUJ do git
- Przechowuj w `.env`
- Różny klucz dla dev/prod
- Nie udostępniaj nikomu

---

### 4. Session Cookie Security (✅ DONE)

**Konfiguracja:**
```python
SESSION_COOKIE_SAMESITE='Lax'
SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
SESSION_COOKIE_HTTPONLY=True
PERMANENT_SESSION_LIFETIME=2592000  # 30 days
```

**Security Headers:**

#### SESSION_COOKIE_HTTPONLY (✅ TRUE)
- Ciasteczko niedostępne dla JavaScript
- Ochrona przed XSS attacks
- **Zawsze włączone**

#### SESSION_COOKIE_SAMESITE (✅ LAX)
- Ochrona przed CSRF attacks
- Ciasteczko wysyłane tylko dla same-site requests
- **Zawsze włączone**

#### SESSION_COOKIE_SECURE (⚙️ Konfigurowane)
- Ciasteczko tylko przez HTTPS
- **Development:** False (HTTP)
- **Production:** True (HTTPS)

**Setup dla produkcji:**
```bash
# W .env produkcyjnym
SESSION_COOKIE_SECURE=True
```

---

### 5. Dodatki (✅ DONE)

#### a) Walidacja SECRET_KEY przy starcie
```python
if not os.getenv('SECRET_KEY') and not test_config:
    raise ValueError("Nie znaleziono SECRET_KEY...")
```

#### b) Redis dla rate limiting
- Persistent storage dla limitów
- Współdzielony między workerami
- Automatyczne wygasanie limitów

---

## 📋 Checklist produkcyjny

### Przed deploy:

- [ ] **1. Wygeneruj silny SECRET_KEY**
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
  Dodaj do `.env` produkcyjnego:
  ```bash
  SECRET_KEY=your_generated_key_here
  ```

- [ ] **2. Skonfiguruj Sentry**
  - Utwórz konto: https://sentry.io
  - Stwórz projekt Flask
  - Dodaj do `.env`:
    ```bash
    SENTRY_DSN=https://xxxxx@xxxxxx.ingest.sentry.io/xxxxxx
    ```

- [ ] **3. Włącz HTTPS cookies**
  ```bash
  # W .env produkcyjnym
  SESSION_COOKIE_SECURE=True
  ```

- [ ] **4. Zainstaluj dependencies**
  ```bash
  pip install -r requirements.txt
  ```
  Nowe biblioteki:
  - Flask-Limiter==3.5.0
  - sentry-sdk[flask]==2.19.2

- [ ] **5. Restart aplikacji**
  ```bash
  docker-compose down
  docker-compose up --build -d
  ```

- [ ] **6. Test rate limiting**
  ```bash
  # Spróbuj 6 razy zalogować się szybko
  # Powinieneś zobaczyć 429 Too Many Requests
  ```

---

## 🔍 Monitoring

### Sentry Dashboard

Po setupie Sentry możesz monitorować:

1. **Issues** - wszystkie błędy aplikacji
   - Exception type
   - Stack trace
   - User context
   - Request info

2. **Performance** - wydajność aplikacji
   - Slow database queries
   - Slow endpoints
   - Bottlenecks

3. **Alerts** - powiadomienia
   - Email przy nowym błędzie
   - Slack integration
   - Threshold alerts

### Rate Limiting Logs

Gdy użytkownik przekroczy limit:
```
429 Too Many Requests
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1634567890
```

**W logach:**
```
Rate limit exceeded for 192.168.1.1: 5 per minute
```

---

## 🛡️ Dodatkowe rekomendacje bezpieczeństwa

### 1. HTTPS (MUST dla produkcji)

**Let's Encrypt (darmowe SSL):**
```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d wavebulk.com -d www.wavebulk.com

# Auto-renewal (runs twice daily)
systemctl enable certbot.timer
```

**Nginx config:**
```nginx
server {
    listen 443 ssl http2;
    server_name wavebulk.com;
    
    ssl_certificate /etc/letsencrypt/live/wavebulk.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wavebulk.com/privkey.pem;
    
    # Modern SSL config
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP redirect to HTTPS
server {
    listen 80;
    server_name wavebulk.com;
    return 301 https://$server_name$request_uri;
}
```

### 2. Database Security

**PostgreSQL production settings:**
```sql
-- Limit max connections
ALTER SYSTEM SET max_connections = 100;

-- Enable SSL
ALTER SYSTEM SET ssl = on;

-- Strong password for DB user
ALTER USER waveforgepro WITH PASSWORD 'super_strong_password_here';
```

**W .env:**
```bash
DATABASE_URL=postgresql://waveforgepro:password@localhost/waveforgepro?sslmode=require
```

### 3. Environment Variables Security

**NIGDY nie commituj:**
- SECRET_KEY
- Database passwords
- API keys (Stripe, Google, SendGrid)
- Sentry DSN

**Używaj:**
```bash
# .env (ignored by git)
SECRET_KEY=xxx
DATABASE_URL=xxx
STRIPE_SECRET_KEY=xxx
```

**Weryfikuj .gitignore:**
```
.env
.env.*
!.env.example
```

### 4. Firewall Configuration

**UFW (Ubuntu):**
```bash
# Allow tylko niezbędne porty
ufw default deny incoming
ufw default allow outgoing
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### 5. Regular Updates

```bash
# Update system
apt update && apt upgrade -y

# Update Python packages
pip list --outdated
pip install --upgrade package_name

# Check for security vulnerabilities
pip install safety
safety check
```

---

## 🧪 Testowanie Security

### Test 1: Rate Limiting

```bash
# Login brute force (powinno zablokować po 5 próbach)
for i in {1..10}; do
  curl -X POST http://localhost:5000/login \
    -d "email=test@test.com&password=wrong" \
    -v
done

# Powinno zwrócić 429 Too Many Requests po 5 próbie
```

### Test 2: SECRET_KEY Validation

```bash
# Start bez SECRET_KEY (powinno rzucić błąd)
unset SECRET_KEY
python3 app.py

# Powinno: ValueError("Nie znaleziono SECRET_KEY...")
```

### Test 3: HTTPS Cookies

```python
# Dev environment (HTTP)
assert app.config['SESSION_COOKIE_SECURE'] == False

# Prod environment (HTTPS)
os.environ['SESSION_COOKIE_SECURE'] = 'True'
assert app.config['SESSION_COOKIE_SECURE'] == True
```

### Test 4: Sentry Capturing

```python
# Testowy błąd w dev
@app.route('/test-sentry')
def test_sentry():
    1 / 0  # ZeroDivisionError
    
# Sprawdź w Sentry Dashboard czy błąd został złapany
```

---

## 📊 Security Metrics

### KPIs do monitorowania:

1. **Failed Login Attempts**
   - Cel: < 1% wszystkich prób
   - Alert: > 100 failed/hour z jednego IP

2. **Rate Limit Hits**
   - Monitor: ile requestów blokowanych
   - Typowo: 1-5% wszystkich requestów

3. **Sentry Errors**
   - Cel: 0 critical errors
   - Alert: nowy error type

4. **Session Security**
   - 100% sesji przez HTTPS (produkcja)
   - 0% HttpOnly bypass attempts

---

## ✅ Checklist przed launch

- [x] Flask-Limiter zainstalowany
- [x] Rate limiting na /login (5/min)
- [x] Rate limiting na /register (10/hour)
- [x] Rate limiting na /reset_password (3/hour)
- [x] Sentry SDK zainstalowany
- [x] Sentry integracja z Flask + Celery
- [x] SECRET_KEY generator udokumentowany
- [x] SESSION_COOKIE_HTTPONLY = True
- [x] SESSION_COOKIE_SAMESITE = Lax
- [x] SESSION_COOKIE_SECURE konfigurowalne
- [ ] SECRET_KEY wygenerowany dla produkcji
- [ ] Sentry DSN skonfigurowany
- [ ] HTTPS włączony (Let's Encrypt)
- [ ] SESSION_COOKIE_SECURE = True w produkcji
- [ ] Firewall skonfigurowany
- [ ] Database SSL włączony

---

## 🎉 Podsumowanie

**Security Foundation jest gotowa!**

✅ **Zaimplementowane:**
- Rate limiting (login: 5/min, register: 10/h, reset: 3/h)
- Sentry error tracking (Flask + Celery)
- Strong SECRET_KEY generation
- Secure session cookies
- Redis storage dla rate limits

🟡 **Do dokończenia w produkcji:**
- Wygeneruj SECRET_KEY i dodaj do .env
- Skonfiguruj Sentry DSN
- Włącz HTTPS (Let's Encrypt)
- Ustaw SESSION_COOKIE_SECURE=True
- Skonfiguruj firewall

🎯 **Rezultat:**
- Ochrona przed brute force (rate limiting)
- Monitorowanie błędów (Sentry)
- Bezpieczne sesje (cookies)
- Gotowe do FREE launch

---

**Zgodnie z LEAN_LAUNCH_PLAN.md - Priority #3 UKOŃCZONE ✅**


