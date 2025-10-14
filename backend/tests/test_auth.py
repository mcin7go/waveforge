import pytest
from flask import url_for, session
from app.models import User
from itsdangerous import URLSafeTimedSerializer

def test_authenticated_user_redirects_from_auth_pages(logged_in_client):
    auth_endpoints = ['auth.login', 'auth.register', 'auth.reset_password_request']
    for endpoint in auth_endpoints:
        response = logged_in_client.get(url_for(endpoint), follow_redirects=True)
        assert response.request.path == url_for('audio_processing.get_processing_history')

def test_password_reset_with_nonexistent_user_valid_token(client, test_user, app, db):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps(test_user.email, salt='reset-password-salt')
    db.session.delete(test_user)
    db.session.commit()
    response = client.post(
        url_for('auth.reset_password', token=token),
        data={'password': 'new', 'password_confirm': 'new'},
        follow_redirects=True
    )
    assert 'Użytkownik nie znaleziony' in response.data.decode('utf-8')

def test_google_callback_creates_new_user(client, db, mocker):
    assert User.query.count() == 0
    mock_google = mocker.patch('app.oauth.oauth.google')
    mock_google.authorize_access_token.return_value = {'id_token': 'dummy'}
    mock_google.parse_id_token.return_value = {'sub': 'completely_new_sub', 'email': 'new.google.user@example.com'}
    response = client.get(url_for('auth.google_callback'), follow_redirects=True)
    assert 'Konto zostało utworzone i zalogowano pomyślnie przez Google!' in response.data.decode('utf-8')
    assert User.query.count() == 1
    new_user = User.query.filter_by(email='new.google.user@example.com').first()
    assert new_user is not None
    assert new_user.google_sub == 'completely_new_sub'

def test_session_is_modified_on_login(client, test_user):
    with client:
        client.get(url_for('auth.login'))
        assert '_user_id' not in session

        client.post(url_for('auth.login'), data={'email': test_user.email, 'password': 'password123'})
        
        assert '_user_id' in session
        assert session['_user_id'] == str(test_user.id)

def test_logout(logged_in_client):
    with logged_in_client:
        response = logged_in_client.get(url_for('auth.logout'), follow_redirects=True)
        assert 'Zostałeś wylogowany' in response.data.decode('utf-8')
        assert '_user_id' not in session

def test_login_nonexistent_user(client, db):
    response = client.post(url_for('auth.login'), data={'email': 'no@user.com', 'password': 'password'}, follow_redirects=True)
    assert 'Błędny email lub hasło' in response.data.decode('utf-8')

def test_registration_without_terms(client, db):
    response = client.post(url_for('auth.register'), data={'email': 'new@test.com', 'password': 'p', 'password_confirm': 'p'}, follow_redirects=True)
    assert 'Musisz zaakceptować regulamin' in response.data.decode('utf-8')

def test_password_reset_invalid_token(client):
    response = client.get(url_for('auth.reset_password', token='invalidtoken'), follow_redirects=True)
    assert 'Link do zresetowania hasła jest nieprawidłowy lub wygasł' in response.data.decode('utf-8')

def test_google_callback_existing_google_user(client, db, mocker):
    existing_user = User(email='google@user.com', google_sub='12345')
    db.session.add(existing_user)
    db.session.commit()
    mock_google = mocker.patch('app.oauth.oauth.google')
    mock_google.authorize_access_token.return_value = {'id_token': 'dummy'}
    mock_google.parse_id_token.return_value = {'sub': '12345', 'email': 'google@user.com'}
    response = client.get(url_for('auth.google_callback'), follow_redirects=True)
    assert 'Zalogowano pomyślnie przez Google!' in response.data.decode('utf-8')
    assert User.query.count() == 1

def test_google_callback_link_existing_email_user(client, test_user, mocker, db):
    assert test_user.google_sub is None
    mock_google = mocker.patch('app.oauth.oauth.google')
    mock_google.authorize_access_token.return_value = {'id_token': 'dummy'}
    mock_google.parse_id_token.return_value = {'sub': 'new_sub_123', 'email': test_user.email}
    response = client.get(url_for('auth.google_callback'), follow_redirects=True)
    assert 'Twoje istniejące konto zostało połączone z kontem Google!' in response.data.decode('utf-8')
    db.session.refresh(test_user)
    assert test_user.google_sub == 'new_sub_123'

def test_google_callback_google_error(client, mocker):
    mocker.patch('app.oauth.oauth.google.authorize_access_token', side_effect=Exception('Google Auth Error'))
    response = client.get(url_for('auth.google_callback'), follow_redirects=True)
    assert 'Wystąpił błąd podczas autoryzacji przez Google' in response.data.decode('utf-8')

def test_google_callback_no_sub(client, mocker):
    mock_google = mocker.patch('app.oauth.oauth.google')
    mock_google.authorize_access_token.return_value = {'id_token': 'dummy'}
    mock_google.parse_id_token.return_value = {'email': 'no_sub@google.com'}
    response = client.get(url_for('auth.google_callback'), follow_redirects=True)
    assert 'Nie udało się uzyskać identyfikatora użytkownika od Google' in response.data.decode('utf-8')
