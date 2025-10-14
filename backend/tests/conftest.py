import pytest
import io
import numpy as np
import soundfile as sf
import os
from app import create_app, db as _db
from app.models import User, AudioFile, ProcessingTask, Plan

@pytest.fixture(scope='function')
def app(tmp_path_factory):
    uploads_path = tmp_path_factory.mktemp('uploads')
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.local',
        'CELERY_ALWAYS_EAGER': True,
        'SECRET_KEY': 'test-secret-key-for-pytest',
        'UPLOAD_FOLDER': str(uploads_path),
        'BABEL_DEFAULT_LOCALE': 'en',
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def test_user(db):
    user = User(email='test@example.com', is_admin=False)
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def admin_user(db):
    user = User(email='admin@example.com', is_admin=True)
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def user_with_stripe_id(db):
    user = User(email='stripe@example.com', stripe_customer_id='cus_test123')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def logged_in_client(client, test_user):
    client.post('/login', data={'email': test_user.email, 'password': 'password123'})
    return client

@pytest.fixture
def active_subscriber_client(client, test_user, db):
    test_user.subscription_status = 'active'
    db.session.add(test_user)
    db.session.commit()
    client.post('/login', data={'email': test_user.email, 'password': 'password123'})
    return client

@pytest.fixture
def logged_in_admin_client(client, admin_user):
    client.post('/login', data={'email': admin_user.email, 'password': 'password123'})
    return client

@pytest.fixture
def dummy_wav_file():
    samplerate = 44100
    data = np.zeros(samplerate, dtype=np.int16)
    buffer = io.BytesIO()
    sf.write(buffer, data, samplerate, format='WAV', subtype='PCM_16')
    buffer.seek(0)
    return (buffer, 'test.wav')

@pytest.fixture
def processed_audio_file(db, test_user, app):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.mp3')
    with open(filepath, 'w') as f:
        f.write('dummy content')
    audio_file = AudioFile(user_id=test_user.id, original_filename='original.wav', original_file_path='/tmp/original.wav', processed_filename='processed.mp3', processed_file_path=filepath)
    db.session.add(audio_file)
    db.session.commit()
    return audio_file

@pytest.fixture
def plan_in_db(db):
    plan = Plan(name='PRO', stripe_product_id='prod_pro', stripe_price_id='price_pro', price=4900, interval='month')
    db.session.add(plan)
    db.session.commit()
    return plan
