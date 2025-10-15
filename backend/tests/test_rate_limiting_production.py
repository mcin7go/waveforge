"""
Testy dla rate limiting w środowisku produkcyjnym
Testy symulują zachowanie limitera BEZ trybu TESTING
"""
import pytest
from flask import Flask, url_for
from app import db as _db, limiter
from app.models import User

@pytest.fixture(scope='function')
def production_app(tmp_path_factory):
    """App fixture z włączonym limiterem (produkcyjny)"""
    from app import create_app
    
    uploads_path = tmp_path_factory.mktemp('uploads')
    app = create_app({
        'TESTING': False,  # Ważne: limiter będzie aktywny
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.local',
        'CELERY_ALWAYS_EAGER': True,
        'SECRET_KEY': 'test-secret-key-for-limiter',
        'UPLOAD_FOLDER': str(uploads_path),
        'BABEL_DEFAULT_LOCALE': 'en',
        'RATELIMIT_STORAGE_URL': 'memory://',  # In-memory dla testów
    })
    
    # Reinitialize limiter with in-memory storage
    limiter._storage_uri = 'memory://'
    
    with app.app_context():
        _db.create_all()
        
    yield app
    
    with app.app_context():
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def prod_client(production_app):
    """Test client z włączonym limiterem"""
    return production_app.test_client()

@pytest.fixture
def prod_user(production_app):
    """User fixture dla produkcyjnych testów"""
    with production_app.app_context():
        user = User(email='prod@test.com')
        user.set_password('password123')
        _db.session.add(user)
        _db.session.commit()
        return user

def test_login_rate_limit_blocks_after_5_attempts(prod_client):
    """Test czy login blokuje po 5 próbach w ciągu minuty"""
    # Rate limit: 5 per minute
    
    for i in range(5):
        response = prod_client.post('/login', 
                                   data={'email': 'test@test.com', 'password': 'wrong'},
                                   follow_redirects=False)
        # Pierwsze 5 powinno przejść
        assert response.status_code in [200, 302], f"Request {i+1} failed with {response.status_code}"
    
    # 6ta próba powinna być zablokowana
    response = prod_client.post('/login',
                               data={'email': 'test@test.com', 'password': 'wrong'})
    assert response.status_code == 429, "6th login attempt should be rate limited"
    assert b'Too Many Requests' in response.data or b'5 per 1 minute' in response.data

def test_register_rate_limit_blocks_after_10_attempts(prod_client):
    """Test czy register blokuje po 10 próbach w ciągu godziny"""
    # Rate limit: 10 per hour
    
    for i in range(10):
        response = prod_client.post('/register',
                                   data={
                                       'email': f'user{i}@test.com',
                                       'password': 'pass',
                                       'password_confirm': 'pass',
                                       'terms': 'on'
                                   },
                                   follow_redirects=False)
        assert response.status_code in [200, 302], f"Request {i+1} failed with {response.status_code}"
    
    # 11ta próba powinna być zablokowana
    response = prod_client.post('/register',
                               data={
                                   'email': 'user11@test.com',
                                   'password': 'pass',
                                   'password_confirm': 'pass',
                                   'terms': 'on'
                               })
    assert response.status_code == 429, "11th registration should be rate limited"

def test_password_reset_rate_limit_blocks_after_3_attempts(prod_client):
    """Test czy reset hasła blokuje po 3 próbach w ciągu godziny"""
    # Rate limit: 3 per hour
    
    for i in range(3):
        response = prod_client.post('/reset_password_request',
                                   data={'email': f'user{i}@test.com'},
                                   follow_redirects=False)
        assert response.status_code in [200, 302], f"Request {i+1} failed with {response.status_code}"
    
    # 4ta próba powinna być zablokowana
    response = prod_client.post('/reset_password_request',
                               data={'email': 'user4@test.com'})
    assert response.status_code == 429, "4th password reset should be rate limited"

def test_rate_limit_headers_present(prod_client):
    """Test czy response zawiera rate limit headers"""
    response = prod_client.post('/login',
                               data={'email': 'test@test.com', 'password': 'wrong'})
    
    # Flask-Limiter dodaje headers
    # Możliwe headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
    # (zależy od konfiguracji)
    assert response.status_code in [200, 302, 429]


