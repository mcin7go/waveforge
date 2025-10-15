from datetime import datetime, UTC
from dateutil.relativedelta import relativedelta
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
    
    # Usage tracking fields
    monthly_upload_count = db.Column(db.Integer, default=0, nullable=False)
    last_reset_date = db.Column(db.Date, default=lambda: datetime.now(UTC).date(), nullable=False)
    plan_name = db.Column(db.String(50), default='Free', nullable=False)

    audio_files = db.relationship('AudioFile', backref='owner', lazy=True)
    processing_tasks = db.relationship('ProcessingTask', backref='assigned_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None: 
            return False
        return check_password_hash(self.password_hash, password)
    
    def get_usage_limit(self):
        """Zwraca miesięczny limit uploadów na podstawie planu"""
        limits = {
            'Free': 10,
            'Starter': 50,
            'Pro': 100,
            'Enterprise': None  # Unlimited
        }
        return limits.get(self.plan_name, 10)
    
    def check_and_reset_monthly_count(self):
        """Resetuje licznik jeśli jest nowy miesiąc"""
        today = datetime.now(UTC).date()
        if today.month != self.last_reset_date.month or today.year != self.last_reset_date.year:
            self.monthly_upload_count = 0
            self.last_reset_date = today
            db.session.commit()
    
    def can_upload(self):
        """Sprawdza czy użytkownik może uploadować więcej plików"""
        self.check_and_reset_monthly_count()
        limit = self.get_usage_limit()
        if limit is None:  # Unlimited (Enterprise)
            return True
        return self.monthly_upload_count < limit
    
    def increment_upload_count(self):
        """Zwiększa licznik uploadów"""
        self.monthly_upload_count += 1
        db.session.commit()
    
    def get_remaining_uploads(self):
        """Zwraca liczbę pozostałych uploadów"""
        limit = self.get_usage_limit()
        if limit is None:
            return None  # Unlimited
        return max(0, limit - self.monthly_upload_count)

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
