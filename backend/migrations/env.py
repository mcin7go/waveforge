# backend/migrations/env.py

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# To jest kluczowe: Dodaj ścieżkę do katalogu 'backend' do sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importuj swoją aplikację Flask i instancję bazy danych
from app import create_app, db # Importujemy create_app i globalne db

# --- ZMIANA: Nie tworzymy aplikacji globalnie tutaj, ani nie wpychamy kontekstu ---
# create_app() zostanie wywołane przez Flask-Migrate automatycznie.
# `db` jest już globalne i zostanie zainicjowane przez `create_app`.

# this is the Alembic Config object, which provides
# access to values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = db.metadata # Używamy globalnego db.metadata

# other values from the config
# my_important_option = config.get_main_option("my_important_option")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario, we need to create an Engine
    and associate a connection with the context.
    """
    # Uzyskujemy konfigurację SQLAlchemy z aplikacji Flask
    # Flask-Migrate wywoła create_app() w tle, więc możemy użyć app.config
    # Ale najpierw musimy stworzyć aplikację, aby mieć do niej dostęp.
    # W testach i CLI, Flask-Migrate często robi to za nas,
    # ale explicitne stworzenie aplikacji tutaj jest bezpieczniejsze.

    # Tworzymy aplikację Flask (nie wpychamy do kontekstu, tylko tworzymy instancję)
    app = create_app() 
    
    # Upewniamy się, że Flask-SQLAlchemy jest zainicjalizowane z tą aplikacją
    # To jest już robione w create_app(), ale ważne, by db miało dostęp do configu.
    
    configuration = config.get_section(config.config_ini_section, {})
    # Użyj DATABASE_URL z configu aplikacji Flask, która jest tworzona.
    configuration['sqlalchemy.url'] = app.config.get('SQLALCHEMY_DATABASE_URI')

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()