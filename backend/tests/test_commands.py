from flask.testing import FlaskCliRunner
from app.models import User

def test_seed_admin_command(app, db):
    """Testuje tworzenie admina przez CLI."""
    app.config['ADMIN_EMAIL'] = 'cli_admin@test.com'
    app.config['ADMIN_PASSWORD'] = 'secret'
    
    runner = app.test_cli_runner()
    result = runner.invoke(args=['seed-admin'])

    assert 'Admin account for cli_admin@test.com created' in result.output
    admin = User.query.filter_by(email='cli_admin@test.com').first()
    assert admin is not None
    assert admin.is_admin is True

def test_seed_users_command(app, db):
    """Testuje tworzenie 10 losowych użytkowników."""
    initial_count = User.query.count()
    runner = app.test_cli_runner()
    result = runner.invoke(args=['seed-users'])

    assert f'Added 10 new users' in result.output
    assert User.query.count() == initial_count + 10
