# 🚀 Lean Launch Plan - WaveBulk FREE

**Data:** 2025-01-15  
**Strategia:** Minimal Viable Launch → Test rynku → Iterate  
**Timeline:** 1-2 tygodnie

---

## 🎯 Twoja Strategia (SMART!)

**"Uruchomić z planem FREE, zrobić SEO, zobaczyć zainteresowanie"**

✅ **Dlaczego to dobry pomysł:**
- Niski koszt startu (bez payment integration)
- Szybki launch (1-2 tygodnie zamiast 2 miesięcy)
- Test product-market fit
- Zbieranie feedback od real users
- Iterate based on data, not assumptions
- Można dodać paid plans później

---

## 📊 Jak Działają Plany - Obecny Stan

### ✅ Co JUŻ DZIAŁA:

**1. Plan Model w bazie**
```python
# backend/app/models.py
class Plan(db.Model):
    name = db.Column(db.String)        # 'Free', 'Pro', 'Enterprise'
    stripe_product_id = db.Column()    # Stripe Product ID
    stripe_price_id = db.Column()      # Stripe Price ID
    price = db.Column(db.Integer)      # Cena w centach ($9.90 → 990)
    interval = db.Column()             # 'month' lub 'year'
    is_active = db.Column(db.Boolean)  # Czy widoczny na stronie
```

**2. User Subscription Status**
```python
class User(UserMixin, db.Model):
    subscription_status = db.Column(db.String)  # None, 'active', 'canceled', 'trialing'
    stripe_customer_id = db.Column()            # Stripe customer ID
```

**3. Decorator `@subscription_required`**
```python
# Sprawdza czy user.subscription_status == 'active'
# Jeśli nie → redirect do /pricing
```

**4. Seed Plans Command**
```bash
flask seed-plans  # Tworzy 5 planów w DB
```

---

### ❌ Co NIE DZIAŁA (BRAK IMPLEMENTACJI):

**🔴 CRITICAL: Limity użytkowania NIE SĄ WYMUSZANE!**

Obecnie:
- Free user może uploadować **UNLIMITED** plików
- Pro user może uploadować **UNLIMITED** plików
- Brak licznika "użyłeś 5/10 plików"
- Brak blokady po przekroczeniu limitu

**Co powinno być:**
- Free: 10 plików/miesiąc
- Starter: 50 plików/miesiąc
- Pro: 100 plików/miesiąc
- Enterprise: Unlimited

**Co trzeba dodać:**
1. Licznik uploaded files per month
2. Check before upload
3. Display "5/10 używanych" w UI
4. Block upload jeśli limit exceeded
5. Monthly reset (1st of month)

---

## 🎯 Lean Launch - Co MINIMALNIE Potrzebne?

### Scenariusz: FREE-Only Launch (bez paid plans)

**Zalety:**
- ✅ Nie potrzebujesz Stripe (payment processing)
- ✅ Nie potrzebujesz webhooks
- ✅ Prostszy onboarding
- ✅ Focus na product, nie billing
- ✅ Szybszy launch (1-2 tygodnie)

**Wady:**
- ❌ Zero revenue initially
- ❌ Trudniej monetize później
- ❌ Abuse risk (unlimited usage)

---

## 📋 MINIMUM VIABLE LAUNCH CHECKLIST

### 🔴 ABSOLUTNIE KONIECZNE (tydzień 1):

#### 1. Usage Limits Implementation (2 dni) **←PRIORYTET #1**

**A) Dodaj do User model:**
```python
# backend/app/models.py
class User(UserMixin, db.Model):
    # ... existing fields ...
    
    # Usage tracking
    monthly_upload_count = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.Date, default=datetime.now(UTC).date)
    plan_name = db.Column(db.String(50), default='Free')  # 'Free', 'Starter', 'Pro', 'Enterprise'
    
    def get_usage_limit(self):
        """Return monthly upload limit based on plan"""
        limits = {
            'Free': 10,
            'Starter': 50,
            'Pro': 100,
            'Enterprise': None  # Unlimited
        }
        return limits.get(self.plan_name, 10)
    
    def check_and_reset_monthly_count(self):
        """Reset count if new month"""
        today = datetime.now(UTC).date()
        if today.month != self.last_reset_date.month or today.year != self.last_reset_date.year:
            self.monthly_upload_count = 0
            self.last_reset_date = today
            db.session.commit()
    
    def can_upload(self):
        """Check if user can upload more files"""
        self.check_and_reset_monthly_count()
        limit = self.get_usage_limit()
        if limit is None:  # Unlimited (Enterprise)
            return True
        return self.monthly_upload_count < limit
    
    def increment_upload_count(self):
        """Increment upload counter"""
        self.monthly_upload_count += 1
        db.session.commit()
```

**B) Migration:**
```bash
docker-compose exec web flask db migrate -m "Add usage limits to User model"
docker-compose exec web flask db upgrade
```

**C) Update upload route:**
```python
# backend/app/blueprints/audio/routes.py
@bp.route('/upload-and-process', methods=['POST'])
@login_required
def upload_and_process_audio():
    user = db.session.get(User, current_user.id)
    
    # CHECK LIMIT
    if not user.can_upload():
        limit = user.get_usage_limit()
        return jsonify({
            "error": f"Monthly limit reached ({user.monthly_upload_count}/{limit} files). "
                    f"Upgrade your plan or wait until next month.",
            "limit_reached": True,
            "used": user.monthly_upload_count,
            "limit": limit
        }), 403
    
    # ... existing upload logic ...
    
    # INCREMENT COUNTER after successful upload
    user.increment_upload_count()
    
    # ... rest of code ...
```

**D) Show usage in Dashboard:**
```html
<!-- dashboard.html -->
<div class="usage-card">
    <h3>Monthly Usage</h3>
    <div class="progress">
        <div class="progress-bar" style="width: {{ (current_user.monthly_upload_count / current_user.get_usage_limit() * 100)|round }}%">
            {{ current_user.monthly_upload_count }} / {{ current_user.get_usage_limit() or '∞' }}
        </div>
    </div>
    <p class="text-muted">
        {% if current_user.get_usage_limit() %}
            {{ current_user.get_usage_limit() - current_user.monthly_upload_count }} plików pozostało
        {% else %}
            Unlimited
        {% endif %}
    </p>
</div>
```

---

#### 2. SEO Basics (4-6h) **←PRIORYTET #2**

**Minimalny SEO dla launch:**

A) **sitemap.xml** (30 min)
B) **robots.txt** (15 min)
C) **Meta tags** w base.html (1h)
   - Description
   - OG tags dla social sharing
D) **Submit do Google Search Console** (30 min)
E) **Google Analytics** (1h)

*Szczegóły w POLISH_AND_OPTIMIZE.md sekcja 3.1-3.2*

---

#### 3. Basic Security (4h) **←PRIORYTET #3**

**Minimum security dla FREE plan:**

A) **Rate limiting** - tylko login (2h)
   ```python
   @limiter.limit("5 per minute")
   def login():
   ```

B) **Strong SECRET_KEY** (15 min)
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

C) **SESSION_COOKIE_SECURE=True** jeśli HTTPS (5 min)

---

### 🟡 WAŻNE ALE MOŻNA POCZEKAĆ (tydzień 2):

#### 4. Error Tracking - Sentry (2h)
```bash
pip install sentry-sdk[flask]
```
*Żeby widzieć błędy od users*

#### 5. Cookie Consent Banner (2h)
*EU requirement, ale możesz dodać po launch*

#### 6. Favicon (1h)
*Branding, ale nie blocking*

---

### 🟢 MOŻNA POMINĄĆ NA START:

- ❌ Stripe integration (bo tylko FREE plan)
- ❌ Paid subscriptions (add later)
- ❌ S3 storage (lokalne pliki OK na start, jeśli mały ruch)
- ❌ CDN (niepotrzebne dla małego ruchu)
- ❌ Load testing (zrób jak będzie 100+ users)
- ❌ CI/CD (nice to have)

---

## 🚀 LEAN LAUNCH TIMELINE (1-2 tygodnie)

### Week 1: Implementation

**Day 1-2: Usage Limits** (MUST)
- Migration: Add usage tracking fields
- Logic: can_upload(), increment_count()
- UI: Display usage counter
- Testing: Verify limits work

**Day 3: SEO** (MUST)
- sitemap.xml
- robots.txt
- Meta tags
- Google Analytics
- Submit to Google Search Console

**Day 4: Security** (MUST)
- Rate limiting (login)
- Strong SECRET_KEY
- Basic security review

**Day 5: Testing & Polish**
- Full test suite run
- Fix any bugs
- Cross-browser smoke test
- Mobile responsive check

**Day 6-7: Deploy Setup**
- .env configuration
- Domain setup
- HTTPS (Let's Encrypt)
- DNS configuration

### Week 2: Launch & Monitor

**Day 8-10: Soft Launch**
- Deploy to production
- Test all flows
- Seed database (plans, admin)
- Monitor errors

**Day 11-14: Marketing & Iteration**
- SEO submission
- Social media announcement
- Monitor analytics
- Gather feedback
- Fix urgent bugs

---

## 📊 FREE Plan Strategy

### Jak to będzie działać:

**1. Rejestracja:**
```
User rejestruje się → Automatycznie plan_name='Free'
                    → subscription_status=None (no Stripe)
                    → monthly_upload_count=0
```

**2. Upload:**
```
User upload file → Check: can_upload()?
                 → If YES: Process + increment_count()
                 → If NO: Show "Limit reached, upgrade or wait"
```

**3. Limit Display:**
```
Dashboard shows: "5 / 10 plików użytych w tym miesiącu"
Upload page shows: "Pozostało 5 plików"
```

**4. Monthly Reset:**
```
Automatic: 1st of each month, counter resets to 0
Check happens in can_upload() method
```

**5. Upgrade Path (future):**
```
User hits limit → "Upgrade to Starter (50 files) for $9.90/mo"
                → Click → Stripe checkout
                → Webhook → subscription_status='active'
                → plan_name='Starter'
                → New limit: 50 files
```

---

## 🎯 Po Launch - Jak Dodać Paid Plans?

### Gdy zobaczysz zainteresowanie (100+ signups):

**Week 3-4: Add Payments**
1. Stripe setup (test mode first)
2. Create products/prices in Stripe Dashboard
3. Subscribe page implementation
4. Webhook handling
5. Test payment flow
6. Switch to live mode

**Week 5: Iterate**
1. Analyze conversion data
2. Optimize pricing
3. A/B test different limits
4. Add features based on feedback

---

## ⚠️ POTENCJALNE PROBLEMY

### 1. Abuse bez Payment
**Problem:** Free users mogą tworzyć wiele kont  
**Solution:** 
- Rate limiting (IP-based)
- Email verification required
- reCAPTCHA na signup
- Monitoring unusual patterns

### 2. Brak revenue
**Problem:** Tylko FREE = $0 income  
**Solution:**
- Quick iteration do paid (2-3 tygodnie)
- Freemium model works jeśli > 5% converts
- Monitor conversion funnel

### 3. Storage costs
**Problem:** Pliki zajmują miejsce  
**Solution:**
- Aggressive cleanup (7 dni zamiast 30)
- Limit file size (50MB for Free)
- Migrate do S3 gdy > 100 users

### 4. Skalowanie
**Problem:** Lokalne pliki nie skalują  
**Solution:**
- OK dla <100 users
- Plan migration do S3 when needed
- Single server OK na start

---

## 💡 Rekomendowany Plan: LEAN START

### Week 1: Minimum Launch (5 dni roboczych)

**Must Have:**
1. ✅ **Usage limits** - 10 plików/miesiąc FREE (2 dni)
2. ✅ **SEO basics** - sitemap, meta, GA (4-6h)
3. ✅ **Rate limiting** - login only (2h)
4. ✅ **Basic security** - SECRET_KEY, HTTPS (4h)
5. ✅ **Error tracking** - Sentry (2h)

**Nice to Have:**
- ⚡ Cookie consent (2h)
- ⚡ Favicon (1h)
- ⚡ Better error messages (3h)

**Total:** ~3-4 dni intensywnej pracy

### Week 2: Deploy & Launch

**Day 1-2: Setup Production**
- Domain + DNS
- HTTPS/SSL
- Environment variables
- Database setup (PostgreSQL)

**Day 3: Deploy**
- Docker deploy
- Migrations
- Seed plans
- Create admin account

**Day 4: Test**
- Full flow test
- SEO verification
- Analytics check

**Day 5: LAUNCH! 🚀**
- Announce
- Monitor
- Gather feedback

---

## 📋 IMPLEMENTATION PRIORITY

### TERAZ (przed launch):

```
Priority 1: Usage Limits ⚠️ CRITICAL
├── Add fields to User model
├── Migration
├── can_upload() logic
├── Dashboard UI pokazuje usage
├── Upload blocker gdy limit exceeded
└── Test limits work

Priority 2: SEO Foundation
├── sitemap.xml
├── robots.txt
├── Meta tags (description, OG)
├── Google Analytics
└── Submit to Search Console

Priority 3: Basic Security
├── Rate limiting (login: 5/min)
├── Strong SECRET_KEY
└── Sentry error tracking
```

### PÓŹNIEJ (po launch, na podstawie feedback):

```
Phase 2: Monetization (gdy masz users)
├── Stripe integration
├── Paid plans (Starter $9.90, Pro $19.90)
├── Payment flow
├── Webhook handling
└── Upgrade prompts

Phase 3: Scale (gdy rośniesz)
├── S3 storage migration
├── CDN
├── Multiple workers
└── Database optimization

Phase 4: Polish (iterate)
├── Advanced features
├── Better UX
├── Performance optimization
└── More integrations
```

---

## 🎯 FREE Plan Configuration

### Zdefiniuj limity dla FREE:

```python
FREE_PLAN_LIMITS = {
    'files_per_month': 10,
    'max_file_size_mb': 50,  # Zamiast 100MB
    'max_duration_seconds': 600,  # 10 minut max
    'concurrent_uploads': 1,  # Jeden na raz
    'features': {
        'batch_upload': False,  # Tylko pojedyncze pliki
        'lufs_normalization': True,
        'format_conversion': True,
        'waveform_player': True,
        'spectrogram': True,  # lub False - premium feature?
        'frequency_analyzer': False,  # Premium?
        'api_access': False,
        'priority_queue': False,
    }
}
```

### Upgrade prompts:

```
Gdy user hit limit:
┌─────────────────────────────────────────┐
│ 🎵 Monthly Limit Reached                │
│                                         │
│ You've used all 10 files this month.   │
│                                         │
│ Upgrade to Starter:                     │
│ • 50 files/month                        │
│ • Larger files (500MB)                  │
│ • Priority processing                   │
│                                         │
│ Only $9.90/month                        │
│                                         │
│ [Upgrade Now]  [Maybe Later]            │
└─────────────────────────────────────────┘
```

---

## 🚀 LAUNCH DAY CHECKLIST

### Pre-Launch (T-1 day):
- [ ] Usage limits tested
- [ ] SEO configured
- [ ] Google Analytics working
- [ ] Error tracking (Sentry) active
- [ ] Domain pointed
- [ ] HTTPS working
- [ ] Database migrated
- [ ] Seed plans run
- [ ] Admin account created
- [ ] Test user flow works

### Launch (T-0):
- [ ] Deploy to production
- [ ] Smoke test all features
- [ ] Submit sitemap to Google
- [ ] Social media post
- [ ] Monitor errors (Sentry)
- [ ] Monitor analytics (GA)

### Post-Launch (T+7 days):
- [ ] Check signup count
- [ ] Check conversion rate
- [ ] Check error rate
- [ ] Gather user feedback
- [ ] Fix critical bugs
- [ ] Plan next iteration

---

## 📈 Success Metrics

### Week 1 (Soft Launch):
- Target: 10-20 signups
- Goal: Test if product works
- Measure: Errors, completion rate

### Week 2-4 (Initial Traction):
- Target: 50-100 signups
- Goal: Product-market fit validation
- Measure: Conversion rate (signup → file uploaded)

### Month 2 (Growth):
- Target: 200-500 users
- Goal: Test monetization
- Measure: Free → Paid conversion (aim: 5-10%)

### Month 3 (Scale):
- Target: 1000+ users
- Goal: Sustainable growth
- Decision: Scale infrastructure or pivot

---

## 💰 Monetization Path

### Phase 1: FREE Only (Month 1)
- Goal: Get users, validate product
- Revenue: $0
- Focus: Product quality, SEO

### Phase 2: Freemium (Month 2)
- Add Starter ($9.90) + Pro ($19.90)
- Goal: 5-10% conversion rate
- Revenue: If 100 users, 5 paid = $50-100/month

### Phase 3: Optimize (Month 3+)
- Optimize limits (test different tiers)
- Add annual plans (discount)
- Enterprise sales (custom pricing)
- Revenue: Scale with user growth

---

## 🎯 MOJA REKOMENDACJA

**Start z FREE-only, ale przygotuj się na szybkie dodanie paid:**

### Immediate (Week 1-2):
1. ✅ **Usage limits implementation** (MUST)
2. ✅ **SEO basics** (MUST)
3. ✅ **Sentry** (MUST)
4. ✅ **Rate limiting** (login) (SHOULD)
5. ✅ **Launch FREE-only**

### Quick Follow-up (Week 3-4):
6. ✅ **Add Stripe** (gdy masz >50 users)
7. ✅ **Enable paid plans**
8. ✅ **Test payment flow**
9. ✅ **Monitor conversions**

### Why?
- Validujesz product SZYBKO (2 tygodnie)
- Nie tracisz czasu na payment jeśli product nie działa
- ALE masz plan dodania paid gdy zobaczysz traction
- Limits prevent abuse even bez payment

---

## 🔧 Quick Implementation Guide

### Day 1: Usage Limits
```bash
# 1. Add fields to User model
# 2. Create migration
docker-compose exec web flask db migrate -m "Add usage limits"
docker-compose exec web flask db upgrade

# 3. Update upload route with limit check
# 4. Add usage display to dashboard
# 5. Test limits work
```

### Day 2: SEO
```bash
# 1. Create sitemap.xml
# 2. Create robots.txt  
# 3. Add meta tags to base.html
# 4. Setup Google Analytics
# 5. Submit to Google Search Console
```

### Day 3: Security & Deploy Prep
```bash
# 1. Add Sentry
# 2. Rate limiting
# 3. Generate SECRET_KEY
# 4. SSL setup
# 5. .env production config
```

### Day 4-5: Deploy
```bash
# 1. Domain + DNS
# 2. Docker deploy
# 3. Database setup
# 4. Test everything
# 5. LAUNCH!
```

---

## ✅ TO-DO LIST dla LEAN LAUNCH

### MUST DO (blocking launch):
- [ ] Usage limits implementation
- [ ] Migration + database update
- [ ] Usage counter UI
- [ ] Limit exceeded handling
- [ ] sitemap.xml + robots.txt
- [ ] Meta tags (basic SEO)
- [ ] Google Analytics
- [ ] Sentry error tracking
- [ ] Rate limiting (login)
- [ ] SECRET_KEY generation
- [ ] .env production config
- [ ] HTTPS/SSL setup
- [ ] Domain configuration
- [ ] Production deploy
- [ ] Smoke test

### NICE TO HAVE (can add later):
- [ ] Cookie consent banner
- [ ] Favicon
- [ ] Better error messages
- [ ] Onboarding flow
- [ ] Remaining format tests
- [ ] Load testing

---

## 💡 Pytanie do Ciebie

**Chcesz iść tą drogą (Lean Launch)?**

Jeśli TAK, zacznijmy od:
1. **Usage limits implementation** (najpilniejsze!)
2. Potem SEO
3. Potem security
4. Deploy

Zaczynamy od usage limits? To 2 dni pracy ale KLUCZOWE dla FREE planu.

EOF
