"""
Rozszerzone testy dla User model - pełne pokrycie metod
"""
import pytest
from datetime import datetime, UTC
from dateutil.relativedelta import relativedelta
from app.models import User

def test_user_creation_with_defaults(db):
    """Test czy User tworzy się z wartościami domyślnymi"""
    user = User(email="new@user.com")
    user.set_password("pass123")
    db.session.add(user)
    db.session.commit()
    
    assert user.monthly_upload_count == 0
    assert user.plan_name == "Free"
    assert user.last_reset_date == datetime.now(UTC).date()
    assert user.subscription_status is None
    assert user.is_admin is False

def test_user_set_password_creates_hash(db):
    """Test czy set_password tworzy hash"""
    user = User(email="hash@test.com")
    user.set_password("mypassword")
    db.session.add(user)
    db.session.commit()
    
    assert user.password_hash is not None
    assert user.password_hash != "mypassword"  # Should be hashed
    assert len(user.password_hash) > 50  # Hashes are long

def test_user_check_password_correct(db):
    """Test sprawdzania poprawnego hasła"""
    user = User(email="check@test.com")
    user.set_password("correctpass")
    db.session.add(user)
    db.session.commit()
    
    assert user.check_password("correctpass") is True

def test_user_check_password_incorrect(db):
    """Test sprawdzania błędnego hasła"""
    user = User(email="check@test.com")
    user.set_password("correctpass")
    db.session.add(user)
    db.session.commit()
    
    assert user.check_password("wrongpass") is False

def test_user_check_password_when_no_hash(db):
    """Test check_password gdy użytkownik nie ma hasła (Google OAuth)"""
    user = User(email="oauth@test.com", google_sub="google123")
    # Nie ustawiamy hasła (OAuth user)
    db.session.add(user)
    db.session.commit()
    
    assert user.password_hash is None
    assert user.check_password("anypassword") is False

def test_user_repr_method(db):
    """Test reprezentacji string użytkownika"""
    user = User(email="repr@test.com")
    db.session.add(user)
    db.session.commit()
    
    assert repr(user) == '<User repr@test.com>'
    assert str(user) == '<User repr@test.com>'

def test_user_plan_upgrade_from_free_to_pro(db):
    """Test upgrade planu z Free do Pro"""
    user = User(email="upgrade@test.com", plan_name="Free")
    user.set_password("pass")
    db.session.add(user)
    db.session.commit()
    
    assert user.get_usage_limit() == 10
    
    # Upgrade do Pro
    user.plan_name = "Pro"
    db.session.commit()
    
    assert user.get_usage_limit() == 100

def test_user_plan_upgrade_resets_dont_affect_count(db):
    """Test czy zmiana planu nie resetuje licznika"""
    user = User(email="upgrade2@test.com", plan_name="Free")
    user.set_password("pass")
    user.monthly_upload_count = 5
    db.session.add(user)
    db.session.commit()
    
    # Upgrade do Pro
    user.plan_name = "Pro"
    db.session.commit()
    
    # Licznik powinien pozostać
    assert user.monthly_upload_count == 5
    # Ale limit się zmienił
    assert user.get_usage_limit() == 100
    assert user.get_remaining_uploads() == 95  # 100 - 5

def test_user_can_upload_after_reset(db):
    """Test czy użytkownik może uploadować po miesięcznym resecie"""
    user = User(email="reset@test.com", plan_name="Free")
    user.set_password("pass")
    user.monthly_upload_count = 10  # Limit reached
    user.last_reset_date = (datetime.now(UTC) - relativedelta(months=1)).date()
    db.session.add(user)
    db.session.commit()
    
    # Przed resetem - nie powinien móc
    # (ale reset się wykona automatycznie w can_upload())
    
    # can_upload() wywołuje check_and_reset
    can_upload = user.can_upload()
    
    # Po resecie powinien móc
    assert can_upload is True
    assert user.monthly_upload_count == 0

def test_user_reset_only_happens_in_new_month(db):
    """Test czy reset NIE działa w tym samym miesiącu"""
    user = User(email="noreset@test.com", plan_name="Free")
    user.set_password("pass")
    user.monthly_upload_count = 5
    user.last_reset_date = datetime.now(UTC).date()
    db.session.add(user)
    db.session.commit()
    
    # Wywołaj reset w tym samym miesiącu
    user.check_and_reset_monthly_count()
    db.session.refresh(user)
    
    # Licznik NIE powinien się zresetować
    assert user.monthly_upload_count == 5

def test_user_reset_happens_in_new_year(db):
    """Test czy reset działa przy zmianie roku"""
    user = User(email="year@test.com", plan_name="Free")
    user.set_password("pass")
    user.monthly_upload_count = 10
    # Ustaw datę na grudzień poprzedniego roku
    user.last_reset_date = (datetime.now(UTC) - relativedelta(years=1)).date()
    db.session.add(user)
    db.session.commit()
    
    user.check_and_reset_monthly_count()
    db.session.refresh(user)
    
    assert user.monthly_upload_count == 0

def test_multiple_increments_dont_exceed_limit(db):
    """Test czy multiple incrementy działają poprawnie"""
    user = User(email="multi@test.com", plan_name="Free")
    user.set_password("pass")
    db.session.add(user)
    db.session.commit()
    
    # Increment 10 razy (do limitu)
    for i in range(10):
        assert user.can_upload() is True
        user.increment_upload_count()
        db.session.refresh(user)
    
    # Teraz powinno być 10/10 i nie można już uploadować
    assert user.monthly_upload_count == 10
    assert user.can_upload() is False

def test_user_relationships_exist(db):
    """Test czy User ma relationships do AudioFile i ProcessingTask"""
    user = User(email="rel@test.com")
    user.set_password("pass")
    db.session.add(user)
    db.session.commit()
    
    assert hasattr(user, 'audio_files')
    assert hasattr(user, 'processing_tasks')
    assert isinstance(user.audio_files, list)
    assert isinstance(user.processing_tasks, list)

def test_user_google_oauth_fields(db):
    """Test czy User może być utworzony przez Google OAuth"""
    user = User(email="google@user.com", google_sub="google_id_12345")
    # Nie ustawiamy hasła dla OAuth users
    db.session.add(user)
    db.session.commit()
    
    assert user.google_sub == "google_id_12345"
    assert user.password_hash is None
    assert user.check_password("anypass") is False

def test_user_stripe_fields(db):
    """Test czy User ma pola Stripe"""
    user = User(email="stripe@test.com", stripe_customer_id="cus_123456")
    user.set_password("pass")
    user.subscription_status = 'active'
    db.session.add(user)
    db.session.commit()
    
    assert user.stripe_customer_id == "cus_123456"
    assert user.subscription_status == 'active'

def test_user_admin_flag(db):
    """Test czy flaga admin działa"""
    admin = User(email="admin@test.com", is_admin=True)
    admin.set_password("pass")
    regular = User(email="regular@test.com", is_admin=False)
    regular.set_password("pass")
    
    db.session.add_all([admin, regular])
    db.session.commit()
    
    assert admin.is_admin is True
    assert regular.is_admin is False

def test_get_usage_limit_unknown_plan_defaults_to_free(db):
    """Test czy nieznany plan domyślnie zwraca limit Free"""
    user = User(email="unknown@test.com", plan_name="UnknownPlan")
    user.set_password("pass")
    db.session.add(user)
    db.session.commit()
    
    # Nieznany plan powinien defaultować do 10 (Free)
    assert user.get_usage_limit() == 10


