import os
import json
import numpy as np
import soundfile as sf
import mutagen
import subprocess
from mutagen.mp3 import MP3
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, TSRC
from pydub import AudioSegment
import pyloudnorm as pyln
from datetime import datetime, UTC
from app import celery, db
from app.models import AudioFile, ProcessingTask
from flask import current_app
import tempfile

PRESET_LUFS = {
    'spotify': -14.0,
    'apple_music': -16.0,
    'youtube': -14.0,
}
BIT_DEPTH_PARAMS = {
    '16': ['-acodec', 'pcm_s16le'],
    '24': ['-acodec', 'pcm_s24le'],
    '32f': ['-acodec', 'pcm_f32le'],
}
BITRATE_PARAMS = {
    'v0': ['-q:a', '0'],  # VBR V0 (245 kbps avg)
    'v2': ['-q:a', '2'],  # VBR V2 (190 kbps avg)
}
LOSSLESS_FORMATS = ['wav', 'flac', 'aiff', 'alac']
LOSSY_FORMATS = ['mp3', 'aac', 'm4a', 'ogg', 'wma', 'opus']

def _detect_audio_format(filepath):
    """Detect audio format using ffprobe and return detailed info"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        format_info = data.get('format', {})
        stream_info = data.get('streams', [{}])[0]
        
        # Determine if lossy or lossless
        codec_name = stream_info.get('codec_name', '').lower()
        format_name = format_info.get('format_name', '').lower()
        
        is_lossless = any(fmt in codec_name or fmt in format_name 
                         for fmt in LOSSLESS_FORMATS)
        
        return {
            'codec': stream_info.get('codec_name', 'unknown'),
            'codec_long_name': stream_info.get('codec_long_name', 'Unknown'),
            'format_name': format_info.get('format_name', 'unknown'),
            'bitrate': int(stream_info.get('bit_rate', 0)) if stream_info.get('bit_rate') else None,
            'sample_rate': int(stream_info.get('sample_rate', 0)) if stream_info.get('sample_rate') else None,
            'channels': stream_info.get('channels', 0),
            'duration': float(format_info.get('duration', 0)),
            'is_lossless': is_lossless,
            'file_extension': os.path.splitext(filepath)[1].lower()
        }
    except Exception as e:
        current_app.logger.error(f"Format detection failed: {e}")
        return None

def _convert_to_wav(input_path, output_path):
    """Convert any audio format to WAV using ffmpeg"""
    try:
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-acodec', 'pcm_s16le',  # 16-bit PCM
            '-ar', '44100',  # 44.1kHz
            '-ac', '2',  # Stereo
            output_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except Exception as e:
        current_app.logger.error(f"Conversion to WAV failed: {e}")
        return False

def _get_quality_warning(input_format_info, output_format):
    """Generate quality warning message based on conversion"""
    if not input_format_info:
        return None
    
    input_lossless = input_format_info.get('is_lossless', False)
    output_lossless = output_format in LOSSLESS_FORMATS
    
    if not input_lossless and not output_lossless:
        return {
            'level': 'warning',
            'message': 'Converting lossy to lossy format - quality may degrade'
        }
    elif not input_lossless and output_lossless:
        return {
            'level': 'info',
            'message': 'Converting lossy to lossless - no quality improvement'
        }
    elif input_lossless and not output_lossless:
        return {
            'level': 'caution',
            'message': 'Converting lossless to lossy - quality will be reduced'
        }
    else:
        return {
            'level': 'ok',
            'message': 'Lossless to lossless conversion - quality preserved'
        }

def _get_bitrate_param(format_type, bitrate):
    """Get bitrate parameters for given format and bitrate setting"""
    if format_type == 'mp3':
        if bitrate in BITRATE_PARAMS:
            return BITRATE_PARAMS[bitrate]
        return ['-b:a', bitrate]
    elif format_type == 'aac':
        if bitrate in ['v0', 'v2']:
            # AAC VBR: v0=~256k, v2=~192k
            vbr_map = {'v0': '5', 'v2': '3'}
            return ['-q:a', vbr_map.get(bitrate, '4')]
        # AAC CBR
        return ['-b:a', bitrate]
    return None

def _run_ffmpeg_loudnorm(input_path, output_path, target_lufs, bit_depth_params, bitrate_param, options):
    try:
        pass1_filter = f"loudnorm=I={target_lufs}:TP=-1.0:LRA=7:print_format=json"
        
        pass1_cmd = ['ffmpeg', '-y', '-i', input_path, '-af', pass1_filter, '-f', 'null', '-']
        
        result = subprocess.run(pass1_cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, pass1_cmd, output=result.stdout, stderr=result.stderr)

        stderr_output = result.stderr.strip()
        start_index = stderr_output.rfind('{')
        end_index = stderr_output.rfind('}')
        if start_index == -1 or end_index == -1:
            raise ValueError("Could not find JSON object in ffmpeg output.")
        json_output = stderr_output[start_index:end_index+1]
        loudnorm_stats = json.loads(json_output)
        
        measured_i = loudnorm_stats['input_i']
        measured_tp = loudnorm_stats['input_tp']
        target_offset = loudnorm_stats['target_offset']

        if float(measured_i) == -float('inf'): measured_i = "-99.0"
        if float(measured_tp) == -float('inf'): measured_tp = "-99.0"
        if target_offset == 'inf': target_offset = "0.0"

        pass2_filter = (f"loudnorm=I={target_lufs}:TP=-1.0:LRA=7:"
                        f"measured_I={measured_i}:"
                        f"measured_LRA={loudnorm_stats['input_lra']}:"
                        f"measured_tp={measured_tp}:"
                        f"measured_thresh={loudnorm_stats['input_thresh']}:"
                        f"offset={target_offset}")
        
        pass2_cmd = ['ffmpeg', '-y', '-i', input_path, '-af', pass2_filter]
        
        if options.get('resampler') == 'soxr':
            pass2_cmd.extend(['-swr_engine', 'soxr'])
        if options.get('dither_method') and options['dither_method'] != 'none' and options.get('bit_depth') == '16':
            pass2_cmd.extend(['-dither_method', options['dither_method']])
        
        if bit_depth_params: pass2_cmd.extend(bit_depth_params)
        if bitrate_param: pass2_cmd.extend(bitrate_param)
        
        pass2_cmd.extend(['-ar', '44100'])
        pass2_cmd.append(output_path)
        
        result = subprocess.run(pass2_cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, pass2_cmd, output=result.stdout, stderr=result.stderr)
            
        return True
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, ValueError) as e:
        current_app.logger.error(f"FFmpeg loudnorm failed for {input_path}: {e}")
        if hasattr(e, 'stderr'):
            current_app.logger.error(f"FFmpeg stderr: {e.stderr}")
        return False

def _apply_metadata(filepath, options):
    cover_art_path = options.get('cover_art_path')
    try:
        audio = mutagen.File(filepath, easy=True)
        if audio is None: return
        
        if options.get('artist'): audio['artist'] = options['artist']
        if options.get('album'): audio['album'] = options['album']
        if options.get('title'): audio['title'] = options['title']
        if options.get('track_number'): audio['tracknumber'] = options['track_number']
        audio.save()

        audio_low_level = mutagen.File(filepath)
        if options.get('isrc'):
            if isinstance(audio_low_level, MP3):
                audio_low_level.tags.add(TSRC(encoding=3, text=options['isrc']))
            else:
                 audio_low_level['isrc'] = options['isrc']
        
        if cover_art_path and os.path.exists(cover_art_path):
            with open(cover_art_path, 'rb') as art:
                image_data = art.read()
                mime = 'image/jpeg' if cover_art_path.lower().endswith(('.jpg', '.jpeg')) else 'image/png'
                if isinstance(audio_low_level, MP3):
                    audio_low_level.tags.add(APIC(encoding=3, mime=mime, type=3, desc='Cover', data=image_data))
                elif isinstance(audio_low_level, FLAC):
                    pic = Picture()
                    pic.data = image_data; pic.mime = mime; pic.type = 3
                    audio_low_level.add_picture(pic)
        audio_low_level.save()
    except Exception as e:
        current_app.logger.error(f"Error applying metadata to {filepath}: {e}")
    finally:
        if cover_art_path and os.path.exists(cover_art_path):
            os.remove(cover_art_path)

@celery.task(bind=True, throws=(Exception,))
def process_audio_file(self, processing_task_id, filepath, original_filename, user_id, options):
    with current_app.app_context():
        task_entry = db.session.get(ProcessingTask, processing_task_id)
        if not task_entry:
            raise ValueError(f"Processing task with ID {processing_task_id} not found in database.")

        task_entry.status = 'PROCESSING'; task_entry.celery_task_id = self.request.id
        db.session.commit()

        try:
            # Detect input format
            input_format_info = _detect_audio_format(filepath)
            current_app.logger.info(f"Input format detected: {input_format_info}")
            
            # Convert to WAV if not already WAV
            if not original_filename.lower().endswith('.wav'):
                current_app.logger.info(f"Converting {original_filename} to WAV...")
                temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                temp_wav_path = temp_wav.name
                temp_wav.close()
                
                if not _convert_to_wav(filepath, temp_wav_path):
                    raise ValueError(f"Failed to convert {original_filename} to WAV format")
                
                # Replace filepath with converted WAV
                os.remove(filepath)
                filepath = temp_wav_path
                current_app.logger.info(f"Conversion successful: {temp_wav_path}")
            
            output_format = options.get('format', 'mp3').lower()
            # Handle AAC -> m4a extension
            file_extension = 'm4a' if output_format == 'aac' else output_format
            output_filename = f"{os.path.splitext(original_filename)[0]}.{file_extension}"
            output_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
            
            target_lufs = None
            lufs_preset = options.get('lufs_preset')
            if lufs_preset in PRESET_LUFS:
                target_lufs = PRESET_LUFS[lufs_preset]
            elif lufs_preset == 'custom' and options.get('normalize'):
                target_lufs = float(options.get('target_lufs', -23.0))

            limit_true_peak = options.get('limit_true_peak', False)
            
            if limit_true_peak and target_lufs is not None:
                bit_depth_params = BIT_DEPTH_PARAMS.get(options.get('bit_depth')) if output_format not in ['mp3', 'aac'] else None
                bitrate_param = _get_bitrate_param(output_format, options.get('bitrate', '320k')) if output_format in ['mp3', 'aac'] else None
                success = _run_ffmpeg_loudnorm(filepath, output_filepath, target_lufs, bit_depth_params, bitrate_param, options)
                if not success: raise Exception("FFmpeg loudnorm processing failed.")
            else:
                audio = AudioSegment.from_wav(filepath)
                if target_lufs is not None:
                    initial_lufs = pyln.Meter(audio.frame_rate).integrated_loudness(audio.get_array_of_samples())
                    loudness_difference = target_lufs - initial_lufs
                    audio = audio.apply_gain(loudness_difference)
                
                # Sample rate
                sample_rate = options.get('sample_rate', '44100')
                if sample_rate == 'original':
                    sample_rate = str(audio.frame_rate)
                
                export_params = {'format': output_format, 'parameters': ['-ar', sample_rate]}
                if options.get('resampler') == 'soxr':
                    export_params['parameters'].extend(['-swr_engine', 'soxr'])
                if options.get('dither_method') and options['dither_method'] != 'none' and options.get('bit_depth') == '16':
                    export_params['parameters'].extend(['-dither_method', options['dither_method']])
                
                # Trim silence
                if options.get('trim_silence'):
                    audio = audio.strip_silence(silence_thresh=-50, padding=100)
                
                # Fade in/out
                fade_in = options.get('fade_in')
                fade_out = options.get('fade_out')
                if fade_in:
                    audio = audio.fade_in(int(float(fade_in) * 1000))
                if fade_out:
                    audio = audio.fade_out(int(float(fade_out) * 1000))
                
                if output_format in ['mp3', 'aac']:
                    bitrate = options.get('bitrate', '320k')
                    if bitrate not in ['v0', 'v2']:
                        export_params['bitrate'] = bitrate
                    # For VBR, pydub doesn't support -q:a, use ffmpeg directly
                else:
                    bit_depth = options.get('bit_depth')
                    if bit_depth in BIT_DEPTH_PARAMS:
                        export_params['parameters'].extend(BIT_DEPTH_PARAMS[bit_depth])
                audio.export(output_filepath, **export_params)

            _apply_metadata(output_filepath, options)
            
            final_data, final_rate = sf.read(output_filepath)
            final_meter = pyln.Meter(final_rate)
            final_lufs = final_meter.integrated_loudness(final_data)
            final_peak_linear = np.max(np.abs(final_data))
            final_peak_dbfs = 20 * np.log10(final_peak_linear) if final_peak_linear > 0 else -np.inf
            duration_seconds = len(final_data) / final_rate

            audio_file_entry = db.session.get(AudioFile, task_entry.audio_file_id)
            if audio_file_entry:
                audio_file_entry.processed_filename = output_filename
                audio_file_entry.processed_file_path = output_filepath
                audio_file_entry.loudness_lufs = round(float(final_lufs), 2)
                audio_file_entry.duration_seconds = round(duration_seconds, 2)
                audio_file_entry.true_peak_db = round(float(final_peak_dbfs), 2)

            # Generate quality warning
            quality_warning = _get_quality_warning(input_format_info, output_format)
            
            task_entry.status = 'COMPLETED'
            result_data = {
                "loudness_lufs": round(float(final_lufs), 2),
                "true_peak_db": round(float(final_peak_dbfs), 2),
                "processed_filename": output_filename,
                "duration_seconds": round(duration_seconds, 2),
                "processed_file_url": f"/uploads/{output_filename}",
                "input_format": input_format_info,
                "quality_warning": quality_warning
            }
            task_entry.result_json = json.dumps(result_data)
            task_entry.completed_at = datetime.now(UTC)
            db.session.commit()

            if os.path.exists(filepath): os.remove(filepath)
            return {"message": "File processed successfully"}
        except Exception as e:
            current_app.logger.error(f"Task failed with exception: {e}")
            if isinstance(e, subprocess.CalledProcessError):
                current_app.logger.error(f"FFMPEG STDERR:\n{e.stderr}")

            db.session.rollback()
            task_entry_on_error = db.session.get(ProcessingTask, processing_task_id)
            task_entry_on_error.status = 'FAILED'
            task_entry_on_error.result_json = json.dumps({"error": str(e)})
            task_entry_on_error.completed_at = datetime.now(UTC)
            db.session.commit()
            if os.path.exists(filepath): os.remove(filepath)
            cover_art_path_on_error = options.get('cover_art_path')
            if cover_art_path_on_error and os.path.exists(cover_art_path_on_error):
                os.remove(cover_art_path_on_error)
            raise e
