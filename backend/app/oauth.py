from authlib.integrations.flask_client import OAuth

# Utworzenie globalnej instancji OAuth
oauth = OAuth()

def init_oauth(app):
    """Inicjalizuje i konfiguruje serwis OAuth z aplikacją Flask."""
    oauth.init_app(app)
    
    # Rejestracja zdalnego serwisu Google
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        # Authlib automatycznie znajdzie wszystkie potrzebne endpointy Google z tego adresu
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            # Określamy, o jakie dane użytkownika prosimy
            'scope': 'openid email profile'
        }
    )