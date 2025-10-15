from flask import render_template, session, redirect, request, url_for, current_app
from flask_login import current_user
from datetime import datetime, UTC
from . import bp
from app.models import Plan

@bp.route('/')
def index():
    user_email = current_user.email if current_user.is_authenticated else None
    current_year = datetime.now(UTC).year
    return render_template('index.html', user_email=user_email, current_year=current_year)

@bp.route('/pricing')
def pricing():
    user_email = current_user.email if current_user.is_authenticated else None
    current_year = datetime.now(UTC).year
    plans = Plan.query.filter_by(is_active=True).order_by(Plan.price).all()
    return render_template('pricing.html', user_email=user_email, current_year=current_year, plans=plans)

@bp.route('/help')
def help():
    user_email = current_user.email if current_user.is_authenticated else None
    current_year = datetime.now(UTC).year
    return render_template('help.html', user_email=user_email, current_year=current_year)

@bp.route('/terms')
def terms():
    user_email = current_user.email if current_user.is_authenticated else None
    current_year = datetime.now(UTC).year
    return render_template('terms.html', user_email=user_email, current_year=current_year)

@bp.route('/privacy')
def privacy():
    user_email = current_user.email if current_user.is_authenticated else None
    current_year = datetime.now(UTC).year
    return render_template('privacy.html', user_email=user_email, current_year=current_year)

@bp.route('/debug-session')
def debug_session():
    """Endpoint do debugowania sesji i języka"""
    from flask import jsonify
    from flask_babel import get_locale as babel_get_locale
    
    return jsonify({
        'session_language': session.get('language'),
        'babel_locale': str(babel_get_locale()),
        'all_session_data': dict(session),
        'available_languages': current_app.config['LANGUAGES'],
        'default_locale': current_app.config['BABEL_DEFAULT_LOCALE']
    })

# --- SEO ENDPOINTS ---
@bp.route('/sitemap.xml')
def sitemap():
    """Dynamiczny sitemap.xml dla SEO"""
    from flask import Response
    
    pages = []
    
    # Główne strony publiczne
    pages.append({
        'loc': url_for('main.index', _external=True),
        'changefreq': 'daily',
        'priority': '1.0'
    })
    pages.append({
        'loc': url_for('main.pricing', _external=True),
        'changefreq': 'weekly',
        'priority': '0.9'
    })
    pages.append({
        'loc': url_for('main.help', _external=True),
        'changefreq': 'monthly',
        'priority': '0.7'
    })
    pages.append({
        'loc': url_for('auth.register', _external=True),
        'changefreq': 'monthly',
        'priority': '0.8'
    })
    pages.append({
        'loc': url_for('auth.login', _external=True),
        'changefreq': 'monthly',
        'priority': '0.6'
    })
    pages.append({
        'loc': url_for('main.terms', _external=True),
        'changefreq': 'yearly',
        'priority': '0.3'
    })
    pages.append({
        'loc': url_for('main.privacy', _external=True),
        'changefreq': 'yearly',
        'priority': '0.3'
    })
    
    # Generuj XML sitemap
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    
    return Response(sitemap_xml, mimetype='application/xml')

@bp.route('/robots.txt')
def robots():
    """robots.txt dla crawlerów"""
    from flask import Response
    
    robots_txt = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /audio/
Disallow: /billing/
Disallow: /debug-session

Sitemap: {url_for('main.sitemap', _external=True)}
"""
    
    return Response(robots_txt, mimetype='text/plain')

# --- TRASA DO ZMIANY JĘZYKA ---
@bp.route('/set-language/<lang>')
def set_language(lang):
    """Change the user interface language"""
    # Check if selected language is supported
    if lang in current_app.config['LANGUAGES']:
        # Save language choice in session
        session['language'] = lang
        session.permanent = True  # Make session permanent (30 days)
    
    # Redirect back to the referring page or to home
    return redirect(request.referrer or url_for('main.index'))
