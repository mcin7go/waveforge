import pytest
from flask import g, url_for
from flask_login import login_user, logout_user
from werkzeug.exceptions import Forbidden
from app.utils.decorators import admin_required, subscription_required

def test_admin_required_decorator(app, test_user, admin_user):
    protected_view = admin_required(lambda: "SUCCESS")
    with app.test_request_context():
        login_user(admin_user)
        assert protected_view() == "SUCCESS"
        logout_user()

        login_user(test_user)
        with pytest.raises(Forbidden):
            protected_view()
        logout_user()
        
        if hasattr(g, 'user'): delattr(g, 'user')
        with pytest.raises(Forbidden):
            protected_view()

def test_subscription_required_decorator(app, db, test_user, admin_user):
    protected_view = subscription_required(lambda: "SUCCESS")

    with app.test_request_context('/protected'):
        response_guest = protected_view()
        assert response_guest.status_code == 302
        assert response_guest.location == url_for('auth.login', next='/protected')

        login_user(test_user)
        test_user.subscription_status = 'canceled'
        db.session.commit()
        response_no_sub = protected_view()
        assert response_no_sub.status_code == 302
        assert response_no_sub.location == url_for('main.pricing')
        logout_user()

        login_user(test_user)
        test_user.subscription_status = 'active'
        db.session.commit()
        assert protected_view() == "SUCCESS"
        logout_user()
        
        login_user(admin_user)
        assert protected_view() == "SUCCESS"
        logout_user()
