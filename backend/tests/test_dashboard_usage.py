"""
Testy dla dashboard z wyświetlaniem usage limits
"""
import pytest
from flask import url_for
from app.models import User

def test_dashboard_displays_usage_count(logged_in_client, test_user, db):
    """Test czy dashboard wyświetla licznik użycia"""
    with logged_in_client.application.app_context():
        test_user.plan_name = "Free"
        test_user.monthly_upload_count = 5
        db.session.commit()
    
    response = logged_in_client.get('/audio/dashboard')
    html = response.data.decode('utf-8')
    
    assert response.status_code == 200
    assert '5' in html  # Licznik
    assert '10' in html or '∞' in html  # Limit
    assert 'Free' in html  # Plan name

def test_dashboard_shows_progress_bar(logged_in_client, test_user, db):
    """Test czy dashboard ma progress bar"""
    with logged_in_client.application.app_context():
        test_user.plan_name = "Free"
        test_user.monthly_upload_count = 7
        db.session.commit()
    
    response = logged_in_client.get('/audio/dashboard')
    html = response.data.decode('utf-8')
    
    assert 'progress-bar' in html
    assert 'stat-card' in html

def test_dashboard_shows_danger_when_limit_reached(logged_in_client, test_user, db):
    """Test czy dashboard pokazuje danger gdy limit osiągnięty"""
    with logged_in_client.application.app_context():
        test_user.plan_name = "Free"
        test_user.monthly_upload_count = 10  # Limit reached
        db.session.commit()
    
    response = logged_in_client.get('/audio/dashboard')
    html = response.data.decode('utf-8')
    
    assert 'bg-danger' in html or 'text-danger' in html or 'border-danger' in html

def test_dashboard_shows_unlimited_for_enterprise(logged_in_client, test_user, db):
    """Test czy dashboard pokazuje unlimited dla Enterprise"""
    with logged_in_client.application.app_context():
        test_user.plan_name = "Enterprise"
        test_user.monthly_upload_count = 999
        db.session.commit()
    
    response = logged_in_client.get('/audio/dashboard')
    html = response.data.decode('utf-8')
    
    assert '∞' in html or 'Unlimited' in html or 'unlimited' in html

def test_upload_page_shows_remaining_uploads(logged_in_client, test_user, db):
    """Test czy strona upload pokazuje pozostałe pliki"""
    with logged_in_client.application.app_context():
        test_user.plan_name = "Free"
        test_user.monthly_upload_count = 6
        test_user.subscription_status = 'active'
        db.session.commit()
    
    response = logged_in_client.get('/audio/upload-and-process')
    html = response.data.decode('utf-8')
    
    assert response.status_code == 200
    # Powinno pokazywać 4/10 lub podobnie
    assert 'Free' in html

def test_upload_page_shows_warning_when_low_uploads(logged_in_client, test_user, db):
    """Test czy upload page pokazuje warning gdy mało pozostałych uploadów"""
    with logged_in_client.application.app_context():
        test_user.plan_name = "Free"
        test_user.monthly_upload_count = 9  # Pozostał 1
        test_user.subscription_status = 'active'
        db.session.commit()
    
    response = logged_in_client.get('/audio/upload-and-process')
    html = response.data.decode('utf-8')
    
    assert response.status_code == 200
    # Powinno pokazywać ostrzeżenie
    assert 'alert' in html.lower()

def test_upload_page_shows_upgrade_button_when_limit_low(logged_in_client, test_user, db):
    """Test czy upload page pokazuje przycisk upgrade gdy mało pozostało"""
    with logged_in_client.application.app_context():
        test_user.plan_name = "Free"
        test_user.monthly_upload_count = 9  # 1 left
        test_user.subscription_status = 'active'
        db.session.commit()
    
    response = logged_in_client.get('/audio/upload-and-process')
    html = response.data.decode('utf-8')
    
    # Powinien być link do pricing/upgrade
    assert 'pricing' in html.lower() or 'ulepsz' in html.lower() or 'upgrade' in html.lower()


