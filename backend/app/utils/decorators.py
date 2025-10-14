from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user
from flask_babel import gettext as _

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.path))
        
        if current_user.subscription_status != 'active' and not current_user.is_admin:
            flash(_('Ta funkcja wymaga aktywnej subskrypcji.'), 'warning')
            return redirect(url_for('main.pricing'))
            
        return f(*args, **kwargs)
    return decorated_function
