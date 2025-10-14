from flask import url_for
from app.models import User
import pytest # Dodajemy import pytest

def test_serve_uploads_route(logged_in_client, processed_audio_file):
    response = logged_in_client.get(url_for('serve_uploads', filename='processed.mp3'))
    assert response.status_code == 200
    assert response.data == b'dummy content'

def test_user_loader(app, test_user):
    user_loader_callback = app.login_manager._user_callback
    loaded_user = user_loader_callback(str(test_user.id))
    assert loaded_user.id == test_user.id
    nonexistent_user = user_loader_callback('999')
    assert nonexistent_user is None

# --- POPRAWIONY TEST ---
# Teraz test sprawdza, czy aplikacja poprawnie rzuca wyjątek ValueError,
# gdy SECRET_KEY nie jest ustawiony, co jest nowym, oczekiwanym zachowaniem.
def test_create_app_with_defaults(mocker):
    mocker.patch.dict('os.environ', clear=True)
    from app import create_app
    with pytest.raises(ValueError, match="Nie znaleziono SECRET_KEY"):
        create_app()
