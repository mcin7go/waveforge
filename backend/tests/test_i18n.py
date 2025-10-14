import pytest
from flask import url_for

def test_language_selection(client):
    response_pl = client.get(url_for('auth.login'), headers={'Accept-Language': 'pl'})
    assert 'Zaloguj się' in response_pl.data.decode('utf-8')

    response_en = client.get(url_for('auth.login'), headers={'Accept-Language': 'en'})
    assert 'Sign In' in response_en.data.decode('utf-8')
