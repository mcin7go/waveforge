"""
Testy dla relationships między modelami
"""
import pytest
from app.models import User, AudioFile, ProcessingTask, Plan
import os

def test_user_audiofiles_relationship(db, test_user):
    """Test czy relationship User -> AudioFile działa"""
    audio1 = AudioFile(
        user_id=test_user.id,
        original_filename='test1.wav',
        original_file_path='/tmp/test1.wav'
    )
    audio2 = AudioFile(
        user_id=test_user.id,
        original_filename='test2.wav',
        original_file_path='/tmp/test2.wav'
    )
    db.session.add_all([audio1, audio2])
    db.session.commit()
    
    assert len(test_user.audio_files) == 2
    assert audio1 in test_user.audio_files
    assert audio2 in test_user.audio_files
    assert audio1.owner == test_user
    assert audio2.owner == test_user

def test_user_processing_tasks_relationship(db, test_user):
    """Test czy relationship User -> ProcessingTask działa"""
    audio = AudioFile(
        user_id=test_user.id,
        original_filename='test.wav',
        original_file_path='/tmp/test.wav'
    )
    db.session.add(audio)
    db.session.commit()
    
    task1 = ProcessingTask(user_id=test_user.id, audio_file_id=audio.id, status='PENDING')
    task2 = ProcessingTask(user_id=test_user.id, audio_file_id=audio.id, status='COMPLETED')
    db.session.add_all([task1, task2])
    db.session.commit()
    
    assert len(test_user.processing_tasks) == 2
    assert task1.assigned_user == test_user
    assert task2.assigned_user == test_user

def test_audiofile_processing_task_relationship(db, test_user):
    """Test czy relationship AudioFile -> ProcessingTask działa"""
    audio = AudioFile(
        user_id=test_user.id,
        original_filename='test.wav',
        original_file_path='/tmp/test.wav'
    )
    db.session.add(audio)
    db.session.commit()
    
    task = ProcessingTask(
        user_id=test_user.id,
        audio_file_id=audio.id,
        status='COMPLETED',
        celery_task_id='task123'
    )
    db.session.add(task)
    db.session.commit()
    
    assert audio.processing_task == task
    assert task.processed_audio == audio

def test_audiofile_repr(db, test_user):
    """Test reprezentacji AudioFile"""
    audio = AudioFile(
        user_id=test_user.id,
        original_filename='myfile.wav',
        original_file_path='/tmp/myfile.wav'
    )
    db.session.add(audio)
    db.session.commit()
    
    assert repr(audio) == '<AudioFile myfile.wav>'

def test_processing_task_repr(db, test_user):
    """Test reprezentacji ProcessingTask"""
    audio = AudioFile(
        user_id=test_user.id,
        original_filename='test.wav',
        original_file_path='/tmp/test.wav'
    )
    db.session.add(audio)
    db.session.commit()
    
    task = ProcessingTask(
        user_id=test_user.id,
        audio_file_id=audio.id,
        celery_task_id='celery_abc123'
    )
    db.session.add(task)
    db.session.commit()
    
    assert repr(task) == '<ProcessingTask celery_abc123>'

def test_plan_repr(db):
    """Test reprezentacji Plan"""
    plan = Plan(
        name='TestPlan',
        stripe_product_id='prod_test',
        stripe_price_id='price_test',
        price=990,
        interval='month'
    )
    db.session.add(plan)
    db.session.commit()
    
    assert repr(plan) == '<Plan TestPlan>'

def test_plan_is_active_default(db):
    """Test czy Plan ma domyślnie is_active=True"""
    plan = Plan(
        name='ActivePlan',
        stripe_product_id='prod_active',
        stripe_price_id='price_active',
        price=1990,
        interval='month'
    )
    db.session.add(plan)
    db.session.commit()
    
    assert plan.is_active is True

def test_plan_can_be_deactivated(db):
    """Test czy Plan można dezaktywować"""
    plan = Plan(
        name='InactivePlan',
        stripe_product_id='prod_inactive',
        stripe_price_id='price_inactive',
        price=2990,
        interval='year',
        is_active=False
    )
    db.session.add(plan)
    db.session.commit()
    
    assert plan.is_active is False

def test_audiofile_stores_metadata(db, test_user):
    """Test czy AudioFile przechowuje metadata"""
    audio = AudioFile(
        user_id=test_user.id,
        original_filename='metadata.wav',
        original_file_path='/tmp/metadata.wav',
        processed_filename='processed.mp3',
        processed_file_path='/tmp/processed.mp3',
        file_size_bytes=1024000,
        loudness_lufs=-14.5,
        true_peak_db=-1.2,
        duration_seconds=180.5
    )
    db.session.add(audio)
    db.session.commit()
    
    assert audio.file_size_bytes == 1024000
    assert audio.loudness_lufs == -14.5
    assert audio.true_peak_db == -1.2
    assert audio.duration_seconds == 180.5

def test_processing_task_result_json(db, test_user):
    """Test czy ProcessingTask może przechowywać result JSON"""
    audio = AudioFile(
        user_id=test_user.id,
        original_filename='test.wav',
        original_file_path='/tmp/test.wav'
    )
    db.session.add(audio)
    db.session.commit()
    
    result_data = {
        'loudness': -14.0,
        'peak': -1.0,
        'format': 'mp3',
        'success': True
    }
    
    task = ProcessingTask(
        user_id=test_user.id,
        audio_file_id=audio.id,
        status='COMPLETED',
        result_json=result_data
    )
    db.session.add(task)
    db.session.commit()
    
    assert task.result_json == result_data
    assert task.result_json['loudness'] == -14.0

def test_user_cannot_be_deleted_with_files(db, test_user):
    """Test czy User z plikami nie może być usunięty bez ręcznego usunięcia plików"""
    audio = AudioFile(
        user_id=test_user.id,
        original_filename='test.wav',
        original_file_path='/tmp/test.wav'
    )
    db.session.add(audio)
    db.session.commit()
    
    # Usuń użytkownika - powinno wywołać IntegrityError
    # bo AudioFile.user_id ma NOT NULL constraint
    db.session.delete(test_user)
    
    with pytest.raises(Exception):  # IntegrityError lub InternalError
        db.session.commit()
    
    # Rollback po błędzie
    db.session.rollback()
    
    # Prawidłowy sposób: najpierw usuń pliki
    db.session.delete(audio)
    db.session.delete(test_user)
    db.session.commit()
    
    # Teraz obydwa powinny być usunięte
    assert db.session.get(User, test_user.id) is None
    assert db.session.get(AudioFile, audio.id) is None

