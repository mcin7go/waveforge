from app.models import User, Plan, AudioFile, ProcessingTask

def test_user_repr(test_user):
    assert repr(test_user) == f'<User {test_user.email}>'

def test_check_password_for_google_user(db):
    google_user = User(email='google@user.com', password_hash=None)
    db.session.add(google_user)
    db.session.commit()
    assert not google_user.check_password('anypassword')

def test_plan_repr(plan_in_db):
    assert repr(plan_in_db) == f'<Plan {plan_in_db.name}>'

def test_audio_file_repr(processed_audio_file):
    assert repr(processed_audio_file) == f'<AudioFile {processed_audio_file.original_filename}>'

def test_processing_task_repr(db, test_user):
    task = ProcessingTask(user_id=test_user.id, audio_file_id=1, celery_task_id='task123', status='PENDING')
    db.session.add(task)
    db.session.commit()
    assert repr(task) == f'<ProcessingTask {task.celery_task_id}>'
