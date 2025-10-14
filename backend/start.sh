#!/bin/bash
chmod +x start.sh

echo "Applying database migrations..."
flask db upgrade

# --- NOWY KROK: Tworzenie/aktualizacja konta admina ---
echo "Seeding admin user..."
flask seed-admin

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
