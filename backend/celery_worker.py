#!/usr/bin/env python
from app import create_app, celery

# Ten plik służy jako dedykowany punkt wejściowy dla workera Celery.
# Tworzy on instancję aplikacji, aby Celery miało dostęp do jej kontekstu,
# konfiguracji, modeli i innych komponentów.

app = create_app()
app.app_context().push()
