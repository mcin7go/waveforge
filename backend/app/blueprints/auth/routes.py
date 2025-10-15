from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import gettext as _
from app.models import db, User
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from app.oauth import oauth
from app.services.email_service import send_password_reset_email
from app import limiter
from . import bp

@bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour")  # Security: Prevent registration abuse
def register():
    if current_user.is_authenticated:
        return redirect(url_for('audio_processing.get_processing_history'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        terms = request.form.get('terms')
        if password != password_confirm:
            flash(_('Hasła nie pasują do siebie.'), 'danger')
            return redirect(url_for('auth.register'))
        if not terms:
            flash(_('Musisz zaakceptować regulamin i politykę prywatności.'), 'danger')
            return redirect(url_for('auth.register'))
        user = User.query.filter_by(email=email).first()
        if user:
            flash(_('Ten adres e-mail jest już zajęty.'), 'danger')
            return redirect(url_for('auth.register'))
        new_user = User(email=email, is_admin=False)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(_('Konto zostało utworzone pomyślnie! Możesz się teraz zalogować.'), 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Security: Prevent brute force attacks
def login():
    if current_user.is_authenticated:
        return redirect(url_for('audio_processing.get_processing_history'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember_me') == 'on'
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash(_('Błędny email lub hasło. Spróbuj ponownie.'), 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=remember)
        return redirect(url_for('audio_processing.get_processing_history'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('Zostałeś wylogowany.'), 'info')
    return redirect(url_for('auth.login'))

@bp.route('/reset_password_request', methods=['GET', 'POST'])
@limiter.limit("3 per hour")  # Security: Prevent password reset abuse
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('audio_processing.get_processing_history'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(email, salt='reset-password-salt')
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            send_password_reset_email(user.email, reset_link)
            flash(_('Na Twój adres e-mail został wysłany link do zresetowania hasła.'), 'info')
        else:
            flash(_('Podany adres e-mail nie istnieje.'), 'danger')
        return redirect(url_for('auth.reset_password_request'))
    return render_template('reset_password_request.html')

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('audio_processing.get_processing_history'))
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='reset-password-salt', max_age=3600)
    except Exception:
        flash(_('Link do zresetowania hasła jest nieprawidłowy lub wygasł.'), 'danger')
        return redirect(url_for('auth.reset_password_request'))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash(_('Użytkownik nie znaleziony.'), 'danger')
        return redirect(url_for('auth.reset_password_request'))
    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        if password != password_confirm:
            flash(_('Hasła nie pasują do siebie.'), 'danger')
            return render_template('reset_password.html', token=token)
        user.set_password(password)
        db.session.commit()
        flash(_('Twoje hasło zostało zresetowane! Możesz się teraz zalogować.'), 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', token=token)

@bp.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@bp.route('/login/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.parse_id_token(token, nonce=None)
    except Exception as e:
        flash(_('Wystąpił błąd podczas autoryzacji przez Google: %(error)s', error=str(e)), 'danger')
        return redirect(url_for('auth.login'))
    google_sub = user_info.get('sub')
    if not google_sub:
        flash(_('Nie udało się uzyskać identyfikatora użytkownika od Google.'), 'danger')
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(google_sub=google_sub).first()
    if user:
        login_user(user)
        flash(_('Zalogowano pomyślnie przez Google!'), 'success')
    else:
        user_by_email = User.query.filter_by(email=user_info.get('email')).first()
        if user_by_email:
            user_by_email.google_sub = google_sub
            db.session.commit()
            login_user(user_by_email)
            flash(_('Twoje istniejące konto zostało połączone z kontem Google!'), 'success')
        else:
            new_user = User(email=user_info.get('email'), google_sub=google_sub, password_hash=None, is_admin=False)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash(_('Konto zostało utworzone i zalogowano pomyślnie przez Google!'), 'success')
    return redirect(url_for('audio_processing.get_processing_history'))
