# backend/run.py

from app import create_app, db # Importujemy db

# Utwórz instancję aplikacji Flask
app = create_app()

# KLUCZOWA ZMIANA:
# Utwórz instancję Celery, która będzie używana przez workera.
# Ta instancja Celery jest już skonfigurowana poprzez app.config w create_app().
# Nazywamy ją 'celery_app' aby była dostępna dla Celery CLI.
from app import celery as celery_app # Importujemy globalną instancję 'celery' i nazywamy ją 'celery_app'

if __name__ == '__main__':
    # Jeśli uruchamiamy 'python run.py' (bez CLI), to uruchom serwer Flask
    # W normalnym użyciu będziemy uruchamiać 'flask run' lub 'gunicorn'
    app.run(debug=True, host='0.0.0.0')