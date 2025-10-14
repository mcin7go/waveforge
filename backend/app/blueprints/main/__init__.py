from flask import Blueprint

# Definicja Blueprintu dla modułu głównego
bp = Blueprint('main', __name__)

# Importujemy widoki (routes), aby zostały zarejestrowane
from . import routes
