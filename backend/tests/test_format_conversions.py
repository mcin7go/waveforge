"""
Real format conversion tests using FFmpeg-generated audio files.
Tests end-to-end conversion for critical format combinations.
"""
import os
import json
import pytest
from app.models import AudioFile, ProcessingTask
from app.tasks.audio_tasks import process_audio_file
from tests.helpers.audio_generator import generate_test_audio, verify_audio_format, cleanup_test_audio


def test_flac_to_mp3_conversion(db, test_user, app):
    """
    Test FLAC → MP3 conversion (lossless → lossy).
    Most popular lossless source format to universal lossy format.
    """
    # Generate real FLAC file
    input_file = generate_test_audio('flac', duration=2)
    
    try:
        # Verify input is valid FLAC
        input_info = verify_audio_format(input_file, 'flac')
        assert input_info['codec'] == 'flac'
        assert input_info['duration'] > 1.5  # ~2 seconds
        
        # Create DB entries
        audio_file = AudioFile(
            user_id=test_user.id,
            original_filename='test.flac',
            original_file_path=input_file,
            file_size_bytes=os.path.getsize(input_file)
        )
        db.session.add(audio_file)
        db.session.commit()
        
        task = ProcessingTask(
            user_id=test_user.id,
            audio_file_id=audio_file.id,
            status='QUEUED'
        )
        db.session.add(task)
        db.session.commit()
        
        # Process: FLAC → MP3
        options = {
            'format': 'mp3',
            'bitrate': '320k',
            'limit_true_peak': False
        }
        
        process_audio_file(task.id, input_file, 'test.flac', test_user.id, options)
        
        # Verify results
        db.session.refresh(task)
        assert task.status == 'COMPLETED', f"Task failed: {task.result_json}"
        
        # Parse result
        result = json.loads(task.result_json)
        assert 'loudness_lufs' in result
        assert 'true_peak_db' in result
        assert 'processed_filename' in result
        assert result['processed_filename'].endswith('.mp3')
        
        # Verify LUFS is in sensible range
        assert -60 < result['loudness_lufs'] < 0
        
        # Quality warning should be None (lossless → lossy is OK)
        # quality_warning = result.get('quality_warning')
        # Note: Current implementation may not set warning for lossless→lossy
        
        # Verify output file exists and is valid MP3
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], result['processed_filename'])
        assert os.path.exists(output_path)
        
        output_info = verify_audio_format(output_path, 'mp3')
        assert output_info['codec'] == 'mp3'
        
        # Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)
            
    finally:
        cleanup_test_audio(input_file)


def test_mp3_to_wav_conversion(db, test_user, app):
    """
    Test MP3 → WAV conversion (lossy → lossless).
    Reverse conversion - tests MP3 decoding.
    """
    input_file = generate_test_audio('mp3', duration=2)
    
    try:
        input_info = verify_audio_format(input_file, 'mp3')
        assert input_info['codec'] == 'mp3'
        
        audio_file = AudioFile(
            user_id=test_user.id,
            original_filename='test.mp3',
            original_file_path=input_file,
            file_size_bytes=os.path.getsize(input_file)
        )
        db.session.add(audio_file)
        db.session.commit()
        
        task = ProcessingTask(
            user_id=test_user.id,
            audio_file_id=audio_file.id,
            status='QUEUED'
        )
        db.session.add(task)
        db.session.commit()
        
        options = {
            'format': 'wav',
            'limit_true_peak': False
        }
        
        process_audio_file(task.id, input_file, 'test.mp3', test_user.id, options)
        
        db.session.refresh(task)
        assert task.status == 'COMPLETED', f"Task failed: {task.result_json}"
        
        result = json.loads(task.result_json)
        assert 'loudness_lufs' in result
        assert 'processed_filename' in result
        assert result['processed_filename'].endswith('.wav')
        
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], result['processed_filename'])
        assert os.path.exists(output_path)
        
        output_info = verify_audio_format(output_path, 'wav')
        assert output_info['codec'] == 'pcm_s16le'
        assert output_info['sample_rate'] == 44100
        
        if os.path.exists(output_path):
            os.remove(output_path)
            
    finally:
        cleanup_test_audio(input_file)


def test_wav_to_aac_m4a_conversion(db, test_user, app):
    """
    Test WAV → AAC (M4A container) conversion (lossless → lossy streaming).
    Tests AAC encoding for Apple Music / YouTube standard.
    """
    input_file = generate_test_audio('wav', duration=2)
    
    try:
        input_info = verify_audio_format(input_file, 'wav')
        assert input_info['codec'] == 'pcm_s16le'
        
        audio_file = AudioFile(
            user_id=test_user.id,
            original_filename='test.wav',
            original_file_path=input_file,
            file_size_bytes=os.path.getsize(input_file)
        )
        db.session.add(audio_file)
        db.session.commit()
        
        task = ProcessingTask(
            user_id=test_user.id,
            audio_file_id=audio_file.id,
            status='QUEUED'
        )
        db.session.add(task)
        db.session.commit()
        
        # Convert to AAC with Spotify LUFS normalization
        options = {
            'format': 'aac',
            'bitrate': '256k',
            'lufs_preset': 'spotify',
            'limit_true_peak': True
        }
        
        process_audio_file(task.id, input_file, 'test.wav', test_user.id, options)
        
        db.session.refresh(task)
        assert task.status == 'COMPLETED', f"Task failed: {task.result_json}"
        
        result = json.loads(task.result_json)
        assert 'loudness_lufs' in result
        
        # Output should be M4A (AAC uses M4A container by convention)
        assert result['processed_filename'].endswith('.m4a')
        
        # LUFS should be normalized to ~-14.0 (Spotify standard)
        assert -15.0 < result['loudness_lufs'] < -13.0
        
        # True Peak should be limited
        assert result['true_peak_db'] < -0.5
        
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], result['processed_filename'])
        assert os.path.exists(output_path)
        
        # Verify M4A file (AAC codec in M4A container)
        output_info = verify_audio_format(output_path, 'm4a')
        assert output_info['codec'] == 'aac'
        
        if os.path.exists(output_path):
            os.remove(output_path)
            
    finally:
        cleanup_test_audio(input_file)


def test_m4a_to_mp3_lossy_warning(db, test_user, app):
    """
    Test M4A → MP3 conversion (lossy → lossy).
    Should generate quality warning about double lossy compression.
    """
    input_file = generate_test_audio('m4a', duration=2)
    
    try:
        input_info = verify_audio_format(input_file, 'm4a')
        assert input_info['codec'] == 'aac'
        
        audio_file = AudioFile(
            user_id=test_user.id,
            original_filename='test.m4a',
            original_file_path=input_file,
            file_size_bytes=os.path.getsize(input_file)
        )
        db.session.add(audio_file)
        db.session.commit()
        
        task = ProcessingTask(
            user_id=test_user.id,
            audio_file_id=audio_file.id,
            status='QUEUED'
        )
        db.session.add(task)
        db.session.commit()
        
        options = {
            'format': 'mp3',
            'bitrate': '320k',
            'limit_true_peak': False
        }
        
        process_audio_file(task.id, input_file, 'test.m4a', test_user.id, options)
        
        db.session.refresh(task)
        assert task.status == 'COMPLETED', f"Task failed: {task.result_json}"
        
        result = json.loads(task.result_json)
        assert 'loudness_lufs' in result
        assert result['processed_filename'].endswith('.mp3')
        
        # CRITICAL: Quality warning should be present for lossy → lossy
        assert 'quality_warning' in result
        quality_warning = result['quality_warning']
        assert quality_warning is not None
        # quality_warning can be dict or string
        if isinstance(quality_warning, dict):
            warning_text = str(quality_warning.get('message', '')).lower()
        else:
            warning_text = str(quality_warning).lower()
        assert 'lossy' in warning_text or 'quality' in warning_text
        
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], result['processed_filename'])
        assert os.path.exists(output_path)
        
        output_info = verify_audio_format(output_path, 'mp3')
        assert output_info['codec'] == 'mp3'
        
        if os.path.exists(output_path):
            os.remove(output_path)
            
    finally:
        cleanup_test_audio(input_file)


def test_aac_to_flac_archiving(db, test_user, app):
    """
    Test AAC → FLAC conversion (lossy → lossless archiving).
    Tests lossy source to lossless archive format.
    """
    input_file = generate_test_audio('aac', duration=2)
    
    try:
        # Note: Pure AAC file (not in M4A container) - FFmpeg creates ADTS AAC
        input_info = verify_audio_format(input_file, 'aac')
        assert input_info['codec'] == 'aac'
        
        audio_file = AudioFile(
            user_id=test_user.id,
            original_filename='test.aac',
            original_file_path=input_file,
            file_size_bytes=os.path.getsize(input_file)
        )
        db.session.add(audio_file)
        db.session.commit()
        
        task = ProcessingTask(
            user_id=test_user.id,
            audio_file_id=audio_file.id,
            status='QUEUED'
        )
        db.session.add(task)
        db.session.commit()
        
        options = {
            'format': 'flac',
            'limit_true_peak': False
        }
        
        process_audio_file(task.id, input_file, 'test.aac', test_user.id, options)
        
        db.session.refresh(task)
        assert task.status == 'COMPLETED', f"Task failed: {task.result_json}"
        
        result = json.loads(task.result_json)
        assert 'loudness_lufs' in result
        assert result['processed_filename'].endswith('.flac')
        
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], result['processed_filename'])
        assert os.path.exists(output_path)
        
        # Verify FLAC output
        output_info = verify_audio_format(output_path, 'flac')
        assert output_info['codec'] == 'flac'
        
        # FLAC should be smaller than WAV (lossless compression)
        # But larger than AAC (lossy → lossless doesn't add quality, just size)
        
        if os.path.exists(output_path):
            os.remove(output_path)
            
    finally:
        cleanup_test_audio(input_file)

