# 🚀 AWS EC2 Deployment Guide - Bez S3 (Lean Launch)

**Data:** 2025-10-15  
**Strategia:** Lokalne pliki na EC2 (bez S3)  
**Koszt:** ~$10-15/miesiąc  
**Skalowanie:** OK dla <100-200 users

---

## 💰 Koszty miesięczne (oszacowanie)

| Zasób | Typ | Koszt/miesiąc |
|-------|-----|---------------|
| EC2 Instance | t3.small (2GB RAM) | $15 |
| Storage (EBS) | 30GB SSD | $3 |
| Bandwidth | 100GB transfer | $0 (w limicie) |
| Domain | .com | $12/rok (~$1/m) |
| **TOTAL** | | **~$19/miesiąc** |

**Alternatywa tańsza:**
- t3.micro (1GB RAM) = $7.50/m - OK dla startu ale mało RAM

---

## 🖥️ Rekomendowana Specyfikacja EC2

### Instance Type: **t3.small**
```
vCPUs: 2
RAM: 2 GB
Storage: 30 GB SSD (EBS gp3)
Network: Up to 5 Gbps
```

**Dlaczego t3.small:**
- ✅ 2GB RAM wystarczy dla Flask + PostgreSQL + Redis + Celery
- ✅ Burstable performance (credit system)
- ✅ Może obsłużyć 50-100 concurrent users
- ✅ Audio processing w Celery (background)

**Region:** `eu-central-1` (Frankfurt) - najbliżej Polski

### OS: **Ubuntu 24.04 LTS**
- Darmowy
- Długie wsparcie (do 2029)
- Dobrze wspiera Docker

---

## 📦 Deployment Architecture (bez S3)

```
                           Internet
                              |
                         [CloudFlare]
                         (opcjonalne)
                              |
                      [EC2 - t3.small]
                              |
                    ┌─────────┴─────────┐
                    |                   |
            [Nginx :80/:443]      [Docker Network]
            (reverse proxy)              |
                    |          ┌─────────┼─────────┐
                    |          |         |         |
                    └──────> [web]   [worker]  [redis]
                              |         |
                         [PostgreSQL]   |
                              |         |
                         [/data/]  [/uploads/]
                    (EBS Volume - persistent)
```

**Kluczowe:**
- ✅ Wszystko na jednym EC2 (bez dodatkowych kosztów)
- ✅ Docker Compose (łatwe zarządzanie)
- ✅ Lokalne pliki w `/data/uploads/` (EBS volume)
- ✅ PostgreSQL w kontenerze (persistent volume)
- ✅ Nginx reverse proxy (HTTPS)

---

## 🔧 Deployment - Krok po kroku

### KROK 1: Launch EC2 Instance (15 min)

**1. AWS Console → EC2 → Launch Instance**

```
Name: wavebulk-production
AMI: Ubuntu Server 24.04 LTS
Instance type: t3.small
Key pair: Utwórz nową (wavebulk-key.pem) - POBIERZ I ZACHOWAJ!
```

**2. Network Settings:**
```
VPC: default
Auto-assign public IP: Enable
Security Group: wavebulk-sg (utwórz nową)
```

**3. Security Group Rules:**
```
Type          Protocol  Port  Source        Description
SSH           TCP       22    Your IP       SSH access
HTTP          TCP       80    0.0.0.0/0     Web traffic
HTTPS         TCP       443   0.0.0.0/0     Secure web
Custom        TCP       5000  Your IP       Flask (tylko do testów)
```

**4. Storage:**
```
Volume Type: gp3 (General Purpose SSD)
Size: 30 GB
Delete on termination: No (persistent!)
```

**5. Launch!**

---

### KROK 2: Połącz się z EC2 (5 min)

```bash
# 1. Ustaw permissions dla klucza
chmod 400 wavebulk-key.pem

# 2. Połącz się przez SSH
ssh -i wavebulk-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# 3. Update system
sudo apt update && sudo apt upgrade -y
```

---

### KROK 3: Zainstaluj Docker (10 min)

```bash
# 1. Install Docker
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 2. Add ubuntu user to docker group
sudo usermod -aG docker ubuntu
newgrp docker

# 3. Verify
docker --version
docker compose version
```

---

### KROK 4: Zainstaluj Nginx (5 min)

```bash
# 1. Install Nginx
sudo apt install -y nginx

# 2. Enable firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

# 3. Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 4. Verify
curl http://localhost
# Powinno zwrócić "Welcome to nginx"
```

---

### KROK 5: Przygotuj katalogi (5 min)

```bash
# 1. Utwórz katalog aplikacji
sudo mkdir -p /opt/wavebulk
sudo chown ubuntu:ubuntu /opt/wavebulk
cd /opt/wavebulk

# 2. Utwórz katalogi danych (persistent)
sudo mkdir -p /data/uploads
sudo mkdir -p /data/postgres
sudo mkdir -p /data/redis
sudo chown -R ubuntu:ubuntu /data

# 3. Struktura:
# /opt/wavebulk/        - kod aplikacji
# /data/uploads/        - pliki użytkowników (persistent)
# /data/postgres/       - baza danych (persistent)
# /data/redis/          - Redis data (persistent)
```

---

### KROK 6: Deploy kodu aplikacji (15 min)

**Opcja A: Git Clone (polecane)**

```bash
cd /opt/wavebulk

# 1. Install git
sudo apt install -y git

# 2. Clone repo (jeśli masz na GitHub)
git clone https://github.com/yourusername/wavebulk.git .

# LUB Opcja B: SCP z local machine
# Na twoim local:
scp -i wavebulk-key.pem -r /srv/docker/vaveforgepro/* ubuntu@YOUR_EC2_IP:/opt/wavebulk/
```

---

### KROK 7: Konfiguracja .env produkcyjny (10 min)

```bash
cd /opt/wavebulk/backend

# 1. Skopiuj przykładowy .env
cp .env.example .env

# 2. Edytuj .env
nano .env
```

**Zawartość `/opt/wavebulk/backend/.env` (PRODUCTION):**

```bash
# === SECURITY ===
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE_32_CHARS_MIN
SESSION_COOKIE_SECURE=True

# === DATABASE ===
DATABASE_URL=postgresql://wavebulk:STRONG_DB_PASSWORD@db:5432/wavebulk

# === REDIS ===
REDIS_URL=redis://redis:6379/0

# === GOOGLE OAuth (opcjonalne) ===
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# === SEO & ANALYTICS ===
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX

# === ERROR TRACKING ===
SENTRY_DSN=https://xxxxx@o123456.ingest.sentry.io/123456

# === EMAIL (SendGrid) ===
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@wavebulk.com

# === STRIPE (na przyszłość) ===
# STRIPE_PUBLISHABLE_KEY=pk_live_xxx
# STRIPE_SECRET_KEY=sk_live_xxx
# STRIPE_WEBHOOK_SECRET=whsec_xxx

# === ADMIN ===
ADMIN_EMAIL=admin@wavebulk.com
ADMIN_PASSWORD=STRONG_ADMIN_PASSWORD_HERE
```

**Wygeneruj SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### KROK 8: Docker Compose dla produkcji (10 min)

**Edytuj `docker-compose.yml` dla produkcji:**

```bash
nano /opt/wavebulk/docker-compose.yml
```

**Zmień volumes na persistent:**

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: wavebulk
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
      POSTGRES_DB: wavebulk
    volumes:
      - /data/postgres:/var/lib/postgresql/data  # PERSISTENT!
    restart: always
    networks:
      - waveforge-net

  redis:
    image: redis:7-alpine
    volumes:
      - /data/redis:/data  # PERSISTENT!
    restart: always
    networks:
      - waveforge-net
    command: redis-server --appendonly yes

  web:
    build:
      context: ./backend
      dockerfile: Dockerfile
    volumes:
      - /data/uploads:/app/uploads  # PERSISTENT!
    environment:
      - FLASK_ENV=production
    env_file:
      - ./backend/.env
    depends_on:
      - db
      - redis
    restart: always
    networks:
      - waveforge-net
    ports:
      - "127.0.0.1:5000:5000"  # Tylko localhost (Nginx proxy)

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks.audio_tasks worker --loglevel=info
    volumes:
      - /data/uploads:/app/uploads  # PERSISTENT!
    env_file:
      - ./backend/.env
    depends_on:
      - db
      - redis
    restart: always
    networks:
      - waveforge-net

networks:
  waveforge-net:
    driver: bridge
```

---

### KROK 9: Nginx Configuration (15 min)

```bash
# 1. Usuń default config
sudo rm /etc/nginx/sites-enabled/default

# 2. Utwórz config dla WaveBulk
sudo nano /etc/nginx/sites-available/wavebulk
```

**Zawartość `/etc/nginx/sites-available/wavebulk`:**

```nginx
# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name wavebulk.com www.wavebulk.com;
    
    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect wszystko do HTTPS (po otrzymaniu SSL)
    # location / {
    #     return 301 https://$server_name$request_uri;
    # }
    
    # Tymczasowo proxy do Flask (przed SSL)
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts dla długich uploadów
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;
        
        # Upload size limit
        client_max_body_size 100M;
    }
}

# HTTPS (odkomentuj po otrzymaniu SSL)
# server {
#     listen 443 ssl http2;
#     server_name wavebulk.com www.wavebulk.com;
#     
#     ssl_certificate /etc/letsencrypt/live/wavebulk.com/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/wavebulk.com/privkey.pem;
#     
#     # Modern SSL config
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
#     ssl_prefer_server_ciphers on;
#     
#     # Security headers
#     add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
#     add_header X-Frame-Options "SAMEORIGIN" always;
#     add_header X-Content-Type-Options "nosniff" always;
#     add_header X-XSS-Protection "1; mode=block" always;
#     
#     location / {
#         proxy_pass http://127.0.0.1:5000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto https;
#         
#         proxy_connect_timeout 300;
#         proxy_send_timeout 300;
#         proxy_read_timeout 300;
#         send_timeout 300;
#         
#         client_max_body_size 100M;
#     }
#     
#     # Static files (opcjonalne - możesz serwować przez Flask)
#     location /static/ {
#         alias /opt/wavebulk/backend/app/static/;
#         expires 1y;
#         add_header Cache-Control "public, immutable";
#     }
# }
```

```bash
# 3. Enable site
sudo ln -s /etc/nginx/sites-available/wavebulk /etc/nginx/sites-enabled/

# 4. Test config
sudo nginx -t

# 5. Reload Nginx
sudo systemctl reload nginx
```

---

### KROK 10: Setup Let's Encrypt SSL (15 min)

```bash
# 1. Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# 2. Przed tym: upewnij się że DNS wskazuje na EC2!
# A record: wavebulk.com -> YOUR_EC2_PUBLIC_IP
# A record: www.wavebulk.com -> YOUR_EC2_PUBLIC_IP

# 3. Poczekaj 5-10 minut aż DNS się propaguje
# Test: ping wavebulk.com (powinno pokazać twój EC2 IP)

# 4. Uzyskaj certyfikat
sudo certbot --nginx -d wavebulk.com -d www.wavebulk.com

# Podaj email, zaakceptuj ToS
# Certbot automatycznie skonfiguruje Nginx dla HTTPS!

# 5. Test auto-renewal
sudo certbot renew --dry-run

# 6. Certbot auto-renews (systemd timer)
sudo systemctl status certbot.timer
```

**Po otrzymaniu SSL:**
- Odkomentuj sekcję HTTPS w nginx config
- Włącz redirect HTTP → HTTPS
- Reload nginx: `sudo systemctl reload nginx`

---

### KROK 11: Deploy aplikacji (20 min)

```bash
cd /opt/wavebulk

# 1. Build i uruchom kontenery
docker compose up -d --build

# 2. Poczekaj ~2-3 minuty na build

# 3. Sprawdź status
docker compose ps
# Wszystkie powinny być "Up"

# 4. Run migrations
docker compose exec web flask db upgrade

# 5. Seed plans
docker compose exec web flask seed-plans

# 6. Utwórz admin account
docker compose exec web flask create-admin

# 7. Test aplikacji
curl http://localhost:5000
# Powinno zwrócić HTML

# 8. Test przez Nginx
curl http://YOUR_EC2_PUBLIC_IP
# Powinno zwrócić HTML

# 9. Test z zewnątrz
# Wejdź na http://wavebulk.com w przeglądarce
```

---

### KROK 12: Monitoring & Logs (10 min)

```bash
# 1. Zobacz logi
docker compose logs -f web

# 2. Logi tylko błędów
docker compose logs web | grep ERROR

# 3. Logi Celery worker
docker compose logs -f worker

# 4. PostgreSQL logs
docker compose logs db

# 5. Setup log rotation (aby logi nie zapchały dysku)
sudo nano /etc/docker/daemon.json
```

**Zawartość:**
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

```bash
sudo systemctl restart docker
docker compose up -d  # Restart kontenerów
```

---

## 🔄 Backup Strategy (BEZ S3)

### Opcja 1: EBS Snapshots (zalecane)

**AWS Console → EC2 → Elastic Block Store → Snapshots**

```bash
# Lub przez AWS CLI:
aws ec2 create-snapshot \
    --volume-id vol-xxxxxxxxx \
    --description "WaveBulk backup $(date +%Y-%m-%d)"

# Automatyzacja - cronjob na EC2:
0 3 * * * /usr/local/bin/aws ec2 create-snapshot --volume-id vol-xxx --description "Daily backup"
```

**Koszt:** ~$0.05/GB/miesiąc (tanie!)

### Opcja 2: Rsync do lokalnego komputera

```bash
# Na twoim lokalnym komputerze - cron daily:
rsync -avz -e "ssh -i wavebulk-key.pem" \
    ubuntu@YOUR_EC2_IP:/data/ \
    /local/backup/wavebulk/
```

### Opcja 3: PostgreSQL dumps

```bash
# Na EC2 - cronjob:
#!/bin/bash
# /opt/wavebulk/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/data/backups

mkdir -p $BACKUP_DIR

# Backup database
docker compose exec -T db pg_dump -U wavebulk wavebulk > $BACKUP_DIR/db_$DATE.sql

# Backup uploads (tar)
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /data/uploads/

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

# Optional: upload to cheap S3 Glacier ($0.004/GB)
# aws s3 cp $BACKUP_DIR/db_$DATE.sql s3://wavebulk-backups/ --storage-class GLACIER
```

```bash
# Make executable
chmod +x /opt/wavebulk/backup.sh

# Add to crontab
crontab -e

# Add line:
0 3 * * * /opt/wavebulk/backup.sh >> /var/log/wavebulk-backup.log 2>&1
```

---

## 🧹 Cleanup Strategy (oszczędzanie miejsca)

**Problem:** Pliki audio zajmują miejsce

**Rozwiązanie:** Automatyczne usuwanie starych plików

```bash
# /opt/wavebulk/cleanup_old_files.sh

#!/bin/bash
# Usuń pliki starsze niż 7 dni

UPLOAD_DIR=/data/uploads
DAYS_TO_KEEP=7

# Usuń pliki starsze niż X dni
find $UPLOAD_DIR -type f -mtime +$DAYS_TO_KEEP -delete

# Log
echo "$(date): Cleaned files older than $DAYS_TO_KEEP days" >> /var/log/wavebulk-cleanup.log
```

```bash
chmod +x /opt/wavebulk/cleanup_old_files.sh

# Cronjob - codziennie o 4 rano
crontab -e

# Add:
0 4 * * * /opt/wavebulk/cleanup_old_files.sh
```

**Alternatywa:** Usuń pliki po 24h dla FREE users, 30 dni dla paid

---

## 📊 Monitoring Disk Space

```bash
# Sprawdź zużycie dysku
df -h

# Ile zajmują uploads
du -sh /data/uploads/

# Top 10 największych plików
find /data/uploads/ -type f -exec du -h {} + | sort -rh | head -10

# Ile plików
find /data/uploads/ -type f | wc -l
```

**Alert gdy > 80% full:**

```bash
# /opt/wavebulk/disk_alert.sh

#!/bin/bash
THRESHOLD=80
USAGE=$(df -h /data | tail -1 | awk '{print $5}' | sed 's/%//')

if [ $USAGE -gt $THRESHOLD ]; then
    echo "ALERT: Disk usage at ${USAGE}%" | mail -s "WaveBulk Disk Alert" admin@wavebulk.com
fi
```

---

## 🔐 Security Hardening

```bash
# 1. Disable password auth (tylko SSH key)
sudo nano /etc/ssh/sshd_config

# Set:
PasswordAuthentication no
PermitRootLogin no

sudo systemctl restart sshd

# 2. Install fail2ban (brute force protection)
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 3. Setup firewall rules
sudo ufw status
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw default deny incoming
sudo ufw --force enable

# 4. Automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 🔄 Update & Maintenance

### Deploy nowej wersji:

```bash
cd /opt/wavebulk

# 1. Pull nowy kod
git pull origin main

# 2. Rebuild kontenerów
docker compose down
docker compose up -d --build

# 3. Run migrations (jeśli są)
docker compose exec web flask db upgrade

# 4. Verify
docker compose ps
curl http://localhost:5000
```

### Restart aplikacji:

```bash
# Restart wszystkich kontenerów
docker compose restart

# Restart tylko web
docker compose restart web

# Restart tylko worker
docker compose restart worker
```

### Zobacz logi błędów:

```bash
# Web errors
docker compose logs web | grep ERROR

# Worker errors  
docker compose logs worker | grep ERROR

# Database logs
docker compose logs db
```

---

## 📈 Monitoring Metrics

### Sprawdź resource usage na EC2:

```bash
# CPU, RAM, Disk
htop

# Docker stats
docker stats

# Ile miejsca zajmuje każdy kontener
docker system df

# Cleanup unused images/volumes
docker system prune -a
```

### Alerty gdy problemy:

**CloudWatch Alarms (AWS - DARMOWE):**
- CPU > 80% przez 5 minut
- Disk > 80%
- StatusCheckFailed

**Setup w AWS Console:**
EC2 → Instance → Actions → Monitor → Manage CloudWatch Alarms

---

## 💾 Disk Space Management

### Oszacowanie zużycia:

**FREE plan (10 plików/miesiąc):**
- Avg file: 20MB
- Per user/month: 200MB (20MB × 10)
- 100 users = 20GB/miesiąc
- Z cleanup po 7 dniach: ~5GB max

**30GB disk wystarczy dla:**
- 150-200 FREE users
- Database (~2GB)
- Docker images (~5GB)
- System (~5GB)
- Uploads (~15GB pozostaje)

### Gdy zabraknie miejsca:

**Opcja 1: Zwiększ EBS volume**
```bash
# AWS Console → EC2 → Volumes → Modify Volume
# Zwiększ z 30GB do 50GB (+$2/m)

# Potem resize filesystem:
sudo growpart /dev/xvda 1
sudo resize2fs /dev/xvda1
```

**Opcja 2: Attach dodatkowy volume**
```bash
# AWS Console → Create Volume → Attach
# Mount jako /data2/uploads
```

**Opcja 3: Migrate do S3 (gdy konieczne)**

---

## 🔥 Emergency Procedures

### Aplikacja nie działa:

```bash
# 1. Sprawdź kontenery
docker compose ps

# 2. Restart
docker compose restart

# 3. Logi
docker compose logs web --tail=100

# 4. Jeśli trzeba rebuild
docker compose down
docker compose up -d --build

# 5. Database issues
docker compose exec db psql -U wavebulk -d wavebulk
```

### Brak miejsca na dysku:

```bash
# 1. Usuń stare pliki ręcznie
find /data/uploads -mtime +3 -delete

# 2. Cleanup Docker
docker system prune -a --volumes

# 3. Zwiększ EBS volume (AWS Console)
```

### Zbyt wolne przetwarzanie:

```bash
# 1. Dodaj więcej Celery workers
docker compose up -d --scale worker=3

# 2. Lub upgrade EC2 do t3.medium (4GB RAM)
```

---

## 📋 Pre-Launch Checklist

### DNS & Domain:
- [ ] Kup domenę (Namecheap, GoDaddy)
- [ ] A record: wavebulk.com → EC2 IP
- [ ] A record: www.wavebulk.com → EC2 IP
- [ ] Test: `ping wavebulk.com`

### EC2 Setup:
- [ ] t3.small instance launched
- [ ] Security group configured (22, 80, 443)
- [ ] 30GB EBS volume
- [ ] Elastic IP (opcjonalnie - aby IP nie zmienił się)

### Software:
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Nginx installed
- [ ] Certbot installed

### Configuration:
- [ ] .env produkcyjny utworzony
- [ ] SECRET_KEY wygenerowany
- [ ] DB_PASSWORD ustawione
- [ ] Nginx config
- [ ] SSL certificate (Let's Encrypt)

### Deployment:
- [ ] Kod na EC2
- [ ] Docker containers up
- [ ] Migrations run
- [ ] Plans seeded
- [ ] Admin account created

### Testing:
- [ ] HTTP works
- [ ] HTTPS works
- [ ] Login/Register works
- [ ] Upload works
- [ ] Processing works
- [ ] Download works

### SEO:
- [ ] Google Analytics ID w .env
- [ ] Verify /sitemap.xml
- [ ] Verify /robots.txt
- [ ] Submit to Google Search Console

### Monitoring:
- [ ] Sentry DSN w .env
- [ ] CloudWatch alarms
- [ ] Backup cronjob
- [ ] Cleanup cronjob

---

## 🚀 Quick Deploy Script

**Utwórz:** `/opt/wavebulk/deploy.sh`

```bash
#!/bin/bash
set -e

echo "🚀 Deploying WaveBulk..."

# Pull latest code
git pull origin main

# Backup database
echo "📦 Backing up database..."
docker compose exec -T db pg_dump -U wavebulk wavebulk > /data/backups/db_predeploy_$(date +%Y%m%d_%H%M%S).sql

# Stop containers
echo "🛑 Stopping containers..."
docker compose down

# Build & start
echo "🔨 Building..."
docker compose up -d --build

# Wait for DB
sleep 5

# Run migrations
echo "🗄️  Running migrations..."
docker compose exec -T web flask db upgrade

# Health check
echo "🏥 Health check..."
sleep 3
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)

if [ $STATUS -eq 200 ]; then
    echo "✅ Deployment successful!"
    docker compose ps
else
    echo "❌ Deployment failed! Status: $STATUS"
    echo "Rolling back..."
    docker compose down
    # Restore from backup if needed
    exit 1
fi
```

```bash
chmod +x /opt/wavebulk/deploy.sh

# Użycie:
./deploy.sh
```

---

## 💡 Tips & Best Practices

### 1. Use Docker logs

```bash
# Follow logs
docker compose logs -f

# Tylko last 100 linii
docker compose logs --tail=100
```

### 2. Database backups ZANIM zmiany

```bash
# Zawsze backup przed migrations!
docker compose exec db pg_dump -U wavebulk wavebulk > backup.sql
```

### 3. Environment variables

```bash
# Verify env vars w kontenerze
docker compose exec web env | grep SECRET
```

### 4. Health checks

```bash
# Endpoint do health check
# Dodaj w routes.py:

@bp.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now(UTC).isoformat()
    }), 200

# Ping co minutę:
curl http://localhost:5000/health
```

### 5. Restart policy

Wszystkie services mają `restart: always` - jeśli EC2 się zrestartuje, Docker auto-start

---

## 🎯 Kiedy migrować do S3?

**Migruj gdy:**
- ✅ Masz >100-200 active users
- ✅ /data/uploads > 20GB
- ✅ Potrzebujesz CDN (szybsze downloady)
- ✅ Masz budget ($5-10/m dla S3)

**Do tego czasu:**
- Lokalne pliki są OK
- Tańsze
- Prostsze
- Wystarczające dla FREE launch

---

## 📊 Expected Performance

**t3.small poradzi sobie z:**
- 50-100 concurrent users
- 10-20 uploads/godzinę
- 100-200 total users (FREE plan)

**Bottle necks:**
- Processing audio (Celery worker) - 1-2 pliki równolegle
- Disk I/O przy wielu uploadach

**Scaling options:**
1. Dodaj workers: `docker compose up -d --scale worker=3`
2. Upgrade EC2: t3.small → t3.medium
3. Oddzielny EC2 dla Celery workers
4. Migrate do S3

---

## ✅ Podsumowanie

**Deployment bez S3 to dobra strategia dla LEAN LAUNCH!**

**Zalety:**
- ✅ Tani (~$19/m)
- ✅ Prosty (wszystko na jednym EC2)
- ✅ Szybki setup (1 dzień)
- ✅ Wystarczający dla 100-200 users
- ✅ Łatwe backupy (EBS snapshots)

**Wady:**
- ❌ Nie skaluje się dla 1000+ users
- ❌ Brak CDN (wolniejsze downloady)
- ❌ Single point of failure

**Rekomendacja:**
- START z tym setupem
- Migrate do S3 gdy >100 users
- Dodaj load balancer gdy >500 users

---

**READY TO DEPLOY?** 🚀

Następne kroki:
1. Setup DNS (A records)
2. Launch EC2 t3.small
3. Follow steps 1-12
4. LAUNCH!


