from flask import Blueprint

# Definicja Blueprintu dla modułu audio
bp = Blueprint('audio_processing', __name__, url_prefix='/audio')

# Importujemy widoki (routes), aby zostały zarejestrowane
from . import routes
