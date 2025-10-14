from flask import Blueprint

# Definicja Blueprintu dla modułu autoryzacji
bp = Blueprint('auth', __name__)

# Importujemy widoki (routes), aby zostały zarejestrowane
from . import routes
