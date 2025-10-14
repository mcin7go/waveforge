import os
import json
import pytest
import array
import mutagen
import subprocess
import numpy as np
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from app.tasks.audio_tasks import process_audio_file
from app.models import ProcessingTask, AudioFile

def test_task_handles_nonexistent_task_id(app):
    result = process_audio_file.s(999, '/tmp/file', 'file.wav', 1, {}).apply()
    assert result.state == 'FAILURE'

def test_task_handles_processing_exception(db, test_user, dummy_wav_file, mocker, app):
    task_entry = ProcessingTask(user_id=test_user.id, audio_file_id=1)
    db.session.add(task_entry)
    db.session.commit()
    mocker.patch('soundfile.read', side_effect=Exception("Corrupted file"))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'test.wav')
    with open(filepath, 'wb') as f: f.write(dummy_wav_file[0].read())
    process_audio_file.s(task_entry.id, filepath, 'test.wav', test_user.id, {}).apply()
    db.session.refresh(task_entry)
    assert task_entry.status == 'FAILED'
    result_dict = json.loads(task_entry.result_json)
    assert 'Corrupted file' in result_dict['error']

def test_task_success_path_no_normalization(db, test_user, dummy_wav_file, app):
    audio_file = AudioFile(user_id=test_user.id, original_filename='test.wav', original_file_path='dummy')
    db.session.add(audio_file)
    db.session.commit()
    task_entry = ProcessingTask(user_id=test_user.id, audio_file_id=audio_file.id)
    db.session.add(task_entry)
    db.session.commit()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'original.wav')
    with open(filepath, 'wb') as f: f.write(dummy_wav_file[0].read())
    
    options = {'normalize': False, 'format': 'mp3'}
    process_audio_file.s(task_entry.id, filepath, 'original.wav', test_user.id, options).apply()

    db.session.refresh(task_entry)
    assert task_entry.status == 'COMPLETED'
    assert 'processed_filename' in json.loads(task_entry.result_json)

@pytest.mark.parametrize("sample_width", [2, 4])
def test_task_normalization_by_sample_width(db, test_user, app, mocker, sample_width):
    mock_audio_segment = mocker.patch('app.tasks.audio_tasks.AudioSegment.from_wav').return_value
    mock_audio_segment.sample_width = sample_width
    mock_audio_segment.get_array_of_samples.return_value = array.array('h', [0, 1, -1])
    mock_audio_segment.apply_gain.return_value = mock_audio_segment
    mock_audio_segment.frame_rate = 44100

    mocker.patch('soundfile.read', return_value=(np.array([0, 0]), 44100))
    mock_meter_instance = mocker.patch('pyloudnorm.Meter').return_value
    mock_meter_instance.integrated_loudness.return_value = -23.0

    audio_file = AudioFile(user_id=test_user.id, original_filename='test.wav', original_file_path='dummy')
    db.session.add(audio_file)
    db.session.commit()
    task_entry = ProcessingTask(user_id=test_user.id, audio_file_id=audio_file.id)
    db.session.add(task_entry)
    db.session.commit()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'sample.wav')
    with open(filepath, 'wb') as f: f.write(b'dummy')
    
    options = {'normalize': True, 'target_lufs': -14.0, 'lufs_preset': 'custom'}
    process_audio_file.s(task_entry.id, filepath, 'sample.wav', test_user.id, options).apply()
    
    db.session.refresh(task_entry)
    assert task_entry.status == 'COMPLETED'

@pytest.mark.parametrize("options, should_normalize, expected_export_params", [
    ({'lufs_preset': 'spotify', 'format': 'wav', 'bit_depth': '16'}, True, {'format': 'wav', 'parameters': ['-ar', '44100', '-acodec', 'pcm_s16le']}),
    ({'lufs_preset': 'apple_music', 'format': 'flac', 'bit_depth': '24'}, True, {'format': 'flac', 'parameters': ['-ar', '44100', '-acodec', 'pcm_s24le']}),
    ({'lufs_preset': 'none', 'format': 'mp3', 'bitrate': '320k', 'bit_depth': '16'}, False, {'format': 'mp3', 'parameters': ['-ar', '44100'], 'bitrate': '320k'}),
    ({'lufs_preset': 'custom', 'normalize': True, 'target_lufs': -10.0, 'format': 'wav', 'bit_depth': '32f'}, True, {'format': 'wav', 'parameters': ['-ar', '44100', '-acodec', 'pcm_f32le']}),
    ({'lufs_preset': 'custom', 'normalize': False, 'format': 'wav'}, False, {'format': 'wav', 'parameters': ['-ar', '44100']}),
    ({'lufs_preset': 'youtube', 'format': 'mp3', 'bitrate': '192k', 'bit_depth': '24'}, True, {'format': 'mp3', 'parameters': ['-ar', '44100'], 'bitrate': '192k'}),
])
def test_task_presets_and_bit_depth_logic(db, test_user, app, mocker, options, should_normalize, expected_export_params):
    INITIAL_LUFS = -25.0
    
    mock_audio_segment = mocker.MagicMock()
    mock_audio_segment.apply_gain.return_value = mock_audio_segment
    mock_audio_segment.get_array_of_samples.return_value = array.array('h', [1000, -1000])
    mock_audio_segment.sample_width = 2
    mock_audio_segment.frame_rate = 44100
    mocker.patch('app.tasks.audio_tasks.AudioSegment.from_wav', return_value=mock_audio_segment)

    mocker.patch('soundfile.read', return_value=(np.array([0, 0]), 44100))
    mock_meter = mocker.patch('pyloudnorm.Meter').return_value
    mock_meter.integrated_loudness.return_value = INITIAL_LUFS
    
    audio_file = AudioFile(user_id=test_user.id, original_filename='test.wav', original_file_path='dummy_path')
    db.session.add(audio_file)
    db.session.commit()
    task_entry = ProcessingTask(user_id=test_user.id, audio_file_id=audio_file.id)
    db.session.add(task_entry)
    db.session.commit()
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'test_logic.wav')
    with open(filepath, 'w') as f:
        f.write('dummy_content')
        
    process_audio_file.s(task_entry.id, filepath, 'test_logic.wav', test_user.id, options).apply()
    
    db.session.refresh(task_entry)
    assert task_entry.status == 'COMPLETED'
    
    if should_normalize:
        assert mock_audio_segment.apply_gain.called
    else:
        assert not mock_audio_segment.apply_gain.called
        
    mock_audio_segment.export.assert_called_once_with(mocker.ANY, **expected_export_params)

@pytest.mark.parametrize("options, audio_format, expected_easy_tags, expect_cover_art", [
    (
        {'artist': 'Test Artist', 'album': 'Test Album', 'title': 'Test Title', 'track_number': '1', 'isrc': 'US1234567890', 'cover_art_path': '/tmp/cover.jpg', 'format': 'mp3'},
        'mp3',
        {'artist': 'Test Artist', 'album': 'Test Album', 'title': 'Test Title', 'tracknumber': '1'},
        True
    ),
    (
        {'artist': 'Another Artist', 'album': '', 'title': '', 'track_number': '', 'isrc': '', 'cover_art_path': None, 'format': 'flac'},
        'flac',
        {'artist': 'Another Artist'},
        False
    ),
])
def test_task_metadata_application(db, test_user, app, mocker, options, audio_format, expected_easy_tags, expect_cover_art):
    mocker.patch('app.tasks.audio_tasks.AudioSegment.from_wav').return_value.export.return_value = None
    mocker.patch('soundfile.read', return_value=(np.array([0, 0]), 44100))
    mocker.patch('pyloudnorm.Meter').return_value.integrated_loudness.return_value = -20.0
    mock_os_remove = mocker.patch('os.remove')
    
    easy_tags_storage = {}
    def set_easy_tag(key, value):
        easy_tags_storage[key] = value
    def get_easy_tag(key):
        return easy_tags_storage.get(key)

    mock_mutagen_easy = mocker.MagicMock()
    mock_mutagen_easy.__setitem__.side_effect = set_easy_tag
    mock_mutagen_easy.__getitem__.side_effect = get_easy_tag
    
    if audio_format == 'mp3':
        mock_mutagen_file = mocker.MagicMock(spec=MP3)
        mock_mutagen_file.tags = mocker.MagicMock()
    else:
        mock_mutagen_file = mocker.MagicMock(spec=FLAC)

    def mutagen_file_side_effect(path, easy=False):
        if easy:
            return mock_mutagen_easy
        return mock_mutagen_file

    mocker.patch('mutagen.File', side_effect=mutagen_file_side_effect)

    if options.get('cover_art_path'):
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('builtins.open', mocker.mock_open(read_data=b'imagedata'))

    audio_file = AudioFile(user_id=test_user.id, original_filename='meta.wav', original_file_path='dummy')
    db.session.add(audio_file)
    db.session.commit()
    task_entry = ProcessingTask(user_id=test_user.id, audio_file_id=audio_file.id)
    db.session.add(task_entry)
    db.session.commit()
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'meta.wav')
    with open(filepath, 'w') as f: f.write('dummy')
    
    process_audio_file.s(task_entry.id, filepath, 'meta.wav', test_user.id, options).apply()

    db.session.refresh(task_entry)
    assert task_entry.status == 'COMPLETED'
    
    mock_mutagen_easy.save.assert_called_once()
    mock_mutagen_file.save.assert_called_once()
    
    for key, value in expected_easy_tags.items():
        assert easy_tags_storage[key] == value

    if expect_cover_art:
        assert mock_mutagen_file.tags.add.called or mock_mutagen_file.add_picture.called
        mock_os_remove.assert_any_call(options['cover_art_path'])
    
    mock_os_remove.assert_any_call(filepath)

@pytest.mark.parametrize("limit_peak, preset, use_ffmpeg", [
    (True, 'spotify', True),
    (True, 'custom', True),
    (False, 'spotify', False),
    (False, 'none', False),
])
def test_task_true_peak_limiter_logic(db, test_user, app, mocker, limit_peak, preset, use_ffmpeg):
    mock_run_ffmpeg = mocker.patch('app.tasks.audio_tasks._run_ffmpeg_loudnorm', return_value=True)
    mocker.patch('app.tasks.audio_tasks._apply_metadata')
    mocker.patch('soundfile.read', return_value=(np.array([0.1, -0.1]), 44100))
    mocker.patch('pyloudnorm.Meter').return_value.integrated_loudness.return_value = -20.0
    
    mock_audio_segment = mocker.MagicMock()
    mock_audio_segment.frame_rate = 44100
    mock_audio_segment.get_array_of_samples.return_value = array.array('h', [100, -100])
    mock_audio_segment.apply_gain.return_value = mock_audio_segment
    mocker.patch('app.tasks.audio_tasks.AudioSegment.from_wav', return_value=mock_audio_segment)

    options = {
        'lufs_preset': preset,
        'normalize': True,
        'target_lufs': -14.0,
        'limit_true_peak': limit_peak,
        'format': 'wav',
        'bit_depth': '16'
    }

    audio_file = AudioFile(user_id=test_user.id, original_filename='peak.wav', original_file_path='dummy')
    db.session.add(audio_file)
    db.session.commit()
    task_entry = ProcessingTask(user_id=test_user.id, audio_file_id=audio_file.id)
    db.session.add(task_entry)
    db.session.commit()
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'peak.wav')
    with open(filepath, 'w') as f: f.write('dummy')

    process_audio_file.s(task_entry.id, filepath, 'peak.wav', test_user.id, options).apply()

    db.session.refresh(task_entry)
    assert task_entry.status == 'COMPLETED'

    if use_ffmpeg:
        mock_run_ffmpeg.assert_called_once()
        mock_audio_segment.export.assert_not_called()
    else:
        mock_run_ffmpeg.assert_not_called()
        mock_audio_segment.export.assert_called_once()

def test_task_dithering_and_resampling_real_ffmpeg(db, test_user, app, dummy_wav_file):
    options = {
        'format': 'wav',
        'limit_true_peak': True,
        'lufs_preset': 'spotify',
        'bit_depth': '16',
        'dither_method': 'shibata',
        'resampler': 'soxr'
    }
    
    audio_file = AudioFile(user_id=test_user.id, original_filename='pro_real.wav', original_file_path='dummy')
    db.session.add(audio_file)
    db.session.commit()
    task_entry = ProcessingTask(user_id=test_user.id, audio_file_id=audio_file.id)
    db.session.add(task_entry)
    db.session.commit()
    
    input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'pro_real.wav')
    with open(input_filepath, 'wb') as f:
        f.write(dummy_wav_file[0].getbuffer())

    process_audio_file.s(task_entry.id, input_filepath, 'pro_real.wav', test_user.id, options).apply()
    
    db.session.refresh(task_entry)
    assert task_entry.status == 'COMPLETED'
