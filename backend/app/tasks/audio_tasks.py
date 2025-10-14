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
            if not original_filename.lower().endswith('.wav'):
                raise ValueError("Only WAV files are supported.")
            
            output_format = options.get('format', 'mp3').lower()
            output_filename = f"{os.path.splitext(original_filename)[0]}.{output_format}"
            output_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], output_filename)
            
            target_lufs = None
            lufs_preset = options.get('lufs_preset')
            if lufs_preset in PRESET_LUFS:
                target_lufs = PRESET_LUFS[lufs_preset]
            elif lufs_preset == 'custom' and options.get('normalize'):
                target_lufs = float(options.get('target_lufs', -23.0))

            limit_true_peak = options.get('limit_true_peak', False)
            
            if limit_true_peak and target_lufs is not None:
                bit_depth_params = BIT_DEPTH_PARAMS.get(options.get('bit_depth')) if output_format != 'mp3' else None
                bitrate_param = ['-b:a', options.get('bitrate', '320k')] if output_format == 'mp3' else None
                success = _run_ffmpeg_loudnorm(filepath, output_filepath, target_lufs, bit_depth_params, bitrate_param, options)
                if not success: raise Exception("FFmpeg loudnorm processing failed.")
            else:
                audio = AudioSegment.from_wav(filepath)
                if target_lufs is not None:
                    initial_lufs = pyln.Meter(audio.frame_rate).integrated_loudness(audio.get_array_of_samples())
                    loudness_difference = target_lufs - initial_lufs
                    audio = audio.apply_gain(loudness_difference)
                
                export_params = {'format': output_format, 'parameters': ['-ar', '44100']}
                if options.get('resampler') == 'soxr':
                    export_params['parameters'].extend(['-swr_engine', 'soxr'])
                if options.get('dither_method') and options['dither_method'] != 'none' and options.get('bit_depth') == '16':
                    export_params['parameters'].extend(['-dither_method', options['dither_method']])
                
                if output_format == 'mp3':
                    export_params['bitrate'] = options.get('bitrate', '320k')
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

            task_entry.status = 'COMPLETED'
            task_entry.result_json = json.dumps({
                "loudness_lufs": round(float(final_lufs), 2),
                "true_peak_db": round(float(final_peak_dbfs), 2),
                "processed_filename": output_filename,
                "duration_seconds": round(duration_seconds, 2),
                "processed_file_url": f"/uploads/{output_filename}"
            })
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
