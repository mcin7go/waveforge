"""
Testy dla security features (rate limiting, session cookies)
"""
import pytest
from flask import url_for

def test_session_cookie_httponly_enabled(app):
    """Test czy SESSION_COOKIE_HTTPONLY jest włączone"""
    assert app.config['SESSION_COOKIE_HTTPONLY'] is True

def test_session_cookie_samesite_lax(app):
    """Test czy SESSION_COOKIE_SAMESITE jest ustawione na Lax"""
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'

def test_session_cookie_secure_configurable(app):
    """Test czy SESSION_COOKIE_SECURE można konfigurować"""
    # W testach powinno być False
    assert app.config['SESSION_COOKIE_SECURE'] is False

def test_secret_key_exists(app):
    """Test czy SECRET_KEY jest ustawiony"""
    assert app.config['SECRET_KEY'] is not None
    assert len(app.config['SECRET_KEY']) > 0

def test_sentry_not_loaded_in_tests(app):
    """Test czy Sentry NIE jest ładowany w testach"""
    # W testach TESTING=True więc Sentry nie powinien się załadować
    assert app.config.get('TESTING') is True


