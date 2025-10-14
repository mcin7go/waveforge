from datetime import datetime, UTC
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    google_sub = db.Column(db.String(256), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    stripe_customer_id = db.Column(db.String(120), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    subscription_status = db.Column(db.String(50), nullable=True, default=None)

    audio_files = db.relationship('AudioFile', backref='owner', lazy=True)
    processing_tasks = db.relationship('ProcessingTask', backref='assigned_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None: 
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    stripe_product_id = db.Column(db.String(120), unique=True, nullable=False)
    stripe_price_id = db.Column(db.String(120), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<Plan {self.name}>'

class AudioFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    processed_filename = db.Column(db.String(255), nullable=True)
    file_size_bytes = db.Column(db.BigInteger, nullable=True)
    loudness_lufs = db.Column(db.Float, nullable=True)
    true_peak_db = db.Column(db.Float, nullable=True)
    duration_seconds = db.Column(db.Float, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.now(UTC))
    original_file_path = db.Column(db.String(512), nullable=False)
    processed_file_path = db.Column(db.String(512), nullable=True)
    
    processing_task = db.relationship('ProcessingTask', backref='processed_audio', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<AudioFile {self.original_filename}>'

class ProcessingTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    audio_file_id = db.Column(db.Integer, db.ForeignKey('audio_file.id'), nullable=False)
    celery_task_id = db.Column(db.String(100), unique=True, nullable=True)
    status = db.Column(db.String(50), default='PENDING', nullable=False)
    result_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<ProcessingTask {self.celery_task_id}>'
