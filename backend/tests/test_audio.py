import os
import io
import pytest
from flask import url_for
from app.models import AudioFile, ProcessingTask, User

def test_upload_page_requires_login(client):
    response = client.get(url_for('audio_processing.upload_and_process_audio'), follow_redirects=True)
    assert response.status_code == 200
    assert b'name="password"' in response.data

def test_upload_redirects_non_subscriber(logged_in_client):
    response = logged_in_client.get(url_for('audio_processing.upload_and_process_audio'), follow_redirects=True)
    assert response.request.path == url_for('main.pricing')
    assert 'Ta funkcja wymaga aktywnej subskrypcji' in response.data.decode('utf-8')

@pytest.mark.parametrize("data, expected_error", [
    (None, 'No file part in the request'),
    ({'options': '{}'}, 'No file part in the request'),
    ({'file': (io.BytesIO(b''), ''), 'options': '{}'}, 'No selected file'),
])
def test_upload_structure_failures(active_subscriber_client, data, expected_error):
    response = active_subscriber_client.post(
        url_for('audio_processing.upload_and_process_audio'),
        data=data,
        content_type='multipart/form-data' if data else None
    )
    assert response.status_code == 400
    assert response.get_json()['error'] == expected_error

@pytest.mark.parametrize("file_tuple, options, expected_error", [
    ((io.BytesIO(b'mp3 data'), 'test.mp3'), '{}', 'Only WAV files are supported'),
    ((io.BytesIO(b'wav data'), 'test.wav'), 'invalid-json', 'Invalid options format'),
])
def test_upload_content_failures(active_subscriber_client, file_tuple, options, expected_error):
    response = active_subscriber_client.post(
        url_for('audio_processing.upload_and_process_audio'),
        data={'file': file_tuple, 'options': options},
        content_type='multipart/form-data'
    )
    assert response.status_code == 400
    assert response.get_json()['error'] == expected_error

def test_upload_and_process_with_cover_art(active_subscriber_client, dummy_wav_file, mocker, app):
    mock_delay = mocker.patch('app.blueprints.audio.routes.process_audio_file.delay')
    mock_delay.return_value.id = 'mock_celery_id_123'
    
    mock_cover_art = (io.BytesIO(b'dummy_image_data'), 'cover.jpg')
    
    response = active_subscriber_client.post(
        url_for('audio_processing.upload_and_process_audio'),
        data={
            'file': dummy_wav_file,
            'cover_art': mock_cover_art,
            'options': '{"artist": "Test Artist"}'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 202
    mock_delay.assert_called_once()
    
    args, kwargs = mock_delay.call_args
    passed_options = args[4]
    
    assert passed_options['artist'] == 'Test Artist'
    assert 'cover_art_path' in passed_options
    assert passed_options['cover_art_path'].startswith(app.config['UPLOAD_FOLDER'])
    assert passed_options['cover_art_path'].endswith('_cover.jpg')
    assert os.path.exists(passed_options['cover_art_path'])

def test_history_shows_download_link(logged_in_client, processed_audio_file):
    response = logged_in_client.get(url_for('audio_processing.get_processing_history'))
    assert response.status_code == 200
    download_url = url_for('serve_uploads', filename=processed_audio_file.processed_filename)
    assert f'href="{download_url}"' in response.data.decode('utf-8')

def test_get_task_status_not_found(logged_in_client):
    response = logged_in_client.get(url_for('audio_processing.get_task_status', task_id=999))
    assert response.status_code == 404

def test_full_delete_flow_with_files(logged_in_client, db, test_user, app):
    upload_folder = app.config['UPLOAD_FOLDER']
    original_path = os.path.join(upload_folder, 'original.wav')
    processed_path = os.path.join(upload_folder, 'processed.mp3')
    with open(original_path, 'w') as f: f.write('orig')
    with open(processed_path, 'w') as f: f.write('proc')
    audio_file = AudioFile(user_id=test_user.id, original_filename='original.wav', original_file_path=original_path, processed_filename='processed.mp3', processed_file_path=processed_path)
    task = ProcessingTask(user_id=test_user.id, audio_file_id=1)
    db.session.add_all([audio_file, task])
    db.session.commit()
    file_id = audio_file.id
    response = logged_in_client.post(url_for('audio_processing.delete_files'), json={'ids': [file_id]})
    assert response.status_code == 200
    assert db.session.get(AudioFile, file_id) is None
    assert not os.path.exists(original_path)
    assert not os.path.exists(processed_path)

def test_delete_flow_with_os_error(logged_in_client, db, test_user, app, mocker):
    audio_file = AudioFile(user_id=test_user.id, original_filename='file.wav', original_file_path='/tmp/file.wav')
    db.session.add(audio_file)
    db.session.commit()
    file_id = audio_file.id
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.remove', side_effect=OSError("Permission denied"))
    response = logged_in_client.post(url_for('audio_processing.delete_files'), json={'ids': [file_id]})
    assert response.status_code == 207
    assert 'Permission denied' in response.get_json()['errors'][0]
    assert db.session.get(AudioFile, file_id) is not None

def test_delete_files_bad_request(logged_in_client):
    response_no_ids = logged_in_client.post(url_for('audio_processing.delete_files'), json={})
    assert response_no_ids.status_code == 400
    response_not_list = logged_in_client.post(url_for('audio_processing.delete_files'), json={'ids': 'not-a-list'})
    assert response_not_list.status_code == 400

def test_history_with_missing_file_on_disk(logged_in_client, db, test_user):
    AudioFile.query.delete()
    db.session.commit()
    audio_file = AudioFile(user_id=test_user.id, original_filename='test.wav', original_file_path='/tmp/test.wav', processed_filename='nonexistent.mp3')
    task = ProcessingTask(user_id=test_user.id, audio_file_id=1)
    db.session.add_all([audio_file, task])
    db.session.commit()
    response = logged_in_client.get(url_for('audio_processing.get_processing_history'))
    assert response.status_code == 200
    assert b'nonexistent.mp3' not in response.data
