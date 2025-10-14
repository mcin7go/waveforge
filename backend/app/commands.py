import click
from faker import Faker
from flask.cli import with_appcontext
from . import db
from .models import User
from flask import current_app

@click.command('seed-admin')
@with_appcontext
def seed_admin_command():
    admin_email = current_app.config.get('ADMIN_EMAIL')
    admin_password = current_app.config.get('ADMIN_PASSWORD')
    if not admin_email or not admin_password:
        click.echo('Admin credentials not set in .env. Skipping.')
        return
    user = User.query.filter_by(email=admin_email).first()
    if user:
        if not user.is_admin:
            user.is_admin = True
            db.session.commit()
            click.echo(f'Granted admin privileges to {admin_email}.')
        else:
            click.echo(f'Admin {admin_email} already exists.')
    else:
        new_admin = User(email=admin_email, is_admin=True)
        new_admin.set_password(admin_password)
        db.session.add(new_admin)
        db.session.commit()
        click.echo(f'Admin account for {admin_email} created.')

@click.command('seed-users')
@with_appcontext
def seed_users_command():
    """Tworzy 10 losowych użytkowników."""
    fake = Faker()
    user_count = User.query.count()
    for i in range(10):
        email = fake.unique.email()
        if not User.query.filter_by(email=email).first():
            user = User(email=email)
            user.set_password('password') # Ustawiamy proste hasło dla wszystkich
            db.session.add(user)
    db.session.commit()
    final_count = User.query.count()
    click.echo(f'Added {final_count - user_count} new users. Total users: {final_count}.')

def register_commands(app):
    app.cli.add_command(seed_admin_command)
    app.cli.add_command(seed_users_command)
