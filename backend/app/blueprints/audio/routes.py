import os
import json
from flask import request, jsonify, current_app, url_for, render_template, redirect
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from datetime import datetime, UTC
from app.tasks.audio_tasks import process_audio_file
from app.models import db, AudioFile, ProcessingTask, User
from app.utils.decorators import subscription_required
from . import bp

def _get_user_id_from_request_or_current_user():
    """
    Pomocnicza funkcja do pobierania ID użytkownika, wspierająca tryb testowy.
    """
    if current_app.config.get('TESTING') and request.args.get('user_id_override', type=int) is not None:
        return request.args.get('user_id_override', type=int)
    elif current_user.is_authenticated:
        return int(current_user.get_id())
    else:
        return None

@bp.route('/')
@login_required
def index():
    """
    Dashboard dla zalogowanego użytkownika.
    """
    return redirect(url_for('audio_processing.dashboard'))

@bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard użytkownika z podsumowaniem i statystykami.
    """
    user_id = int(current_user.get_id())
    user_object = db.session.get(User, user_id)
    
    # Statystyki
    total_files = AudioFile.query.filter_by(user_id=user_id).count()
    total_tasks = ProcessingTask.query.filter_by(user_id=user_id).count()
    completed_tasks = ProcessingTask.query.filter_by(user_id=user_id, status='COMPLETED').count()
    failed_tasks = ProcessingTask.query.filter_by(user_id=user_id, status='FAILED').count()
    pending_tasks = ProcessingTask.query.filter_by(user_id=user_id).filter(
        ProcessingTask.status.in_(['PENDING', 'QUEUED', 'PROCESSING'])
    ).count()
    
    # Ostatnie pliki (5 najnowszych)
    recent_files = AudioFile.query.filter_by(user_id=user_id).order_by(
        AudioFile.upload_date.desc()
    ).limit(5).all()
    
    # Statystyki LUFS (średnia głośność)
    files_with_lufs = AudioFile.query.filter_by(user_id=user_id).filter(
        AudioFile.loudness_lufs.isnot(None)
    ).all()
    
    avg_lufs = None
    if files_with_lufs:
        avg_lufs = sum(f.loudness_lufs for f in files_with_lufs) / len(files_with_lufs)
    
    # Total storage used
    total_storage_bytes = db.session.query(
        db.func.sum(AudioFile.file_size_bytes)
    ).filter_by(user_id=user_id).scalar() or 0
    
    recent_data = []
    for af in recent_files:
        task = ProcessingTask.query.filter_by(audio_file_id=af.id).order_by(
            ProcessingTask.created_at.desc()
        ).first()
        
        processed_file_url = None
        if af.processed_filename and os.path.exists(
            os.path.join(current_app.config['UPLOAD_FOLDER'], af.processed_filename)
        ):
            processed_file_url = f"/uploads/{af.processed_filename}"
        
        recent_data.append({
            "id": af.id,
            "filename": af.original_filename,
            "upload_date": af.upload_date,
            "status": task.status if task else "NO_TASK",
            "loudness_lufs": af.loudness_lufs,
            "processed_file_url": processed_file_url
        })
    
    current_year = datetime.now(UTC).year
    return render_template(
        'dashboard.html',
        user_email=user_object.email,
        current_year=current_year,
        stats={
            'total_files': total_files,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'pending_tasks': pending_tasks,
            'avg_lufs': avg_lufs,
            'total_storage_bytes': total_storage_bytes,
        },
        recent_files=recent_data
    )

@bp.route('/upload-and-process', methods=['GET', 'POST'])
@login_required
@subscription_required
def upload_and_process_audio():
    user_id_int = _get_user_id_from_request_or_current_user()
    if user_id_int is None:
        return jsonify({"error": "User ID not found"}), 401
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        options_str = request.form.get('options', '{}')
        try:
            options = json.loads(options_str)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid options format"}), 400
        
        cover_art_file = request.files.get('cover_art')
        cover_art_path = None
        if cover_art_file:
            cover_art_filename = secure_filename(cover_art_file.filename)
            unique_cover_filename = f"cover_{user_id_int}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{cover_art_filename}"
            cover_art_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_cover_filename)
            cover_art_file.save(cover_art_path)
            options['cover_art_path'] = cover_art_path

        filename = secure_filename(file.filename)
        if not filename.lower().endswith('.wav'):
            if cover_art_path and os.path.exists(cover_art_path):
                os.remove(cover_art_path)
            return jsonify({"error": "Only WAV files are supported"}), 400

        unique_filename = f"{user_id_int}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        new_audio_file = AudioFile(
            user_id=user_id_int,
            original_filename=filename,
            original_file_path=filepath,
            file_size_bytes=os.path.getsize(filepath)
        )
        db.session.add(new_audio_file)
        db.session.commit()
        new_processing_task = ProcessingTask(
            user_id=user_id_int,
            audio_file_id=new_audio_file.id,
            status='QUEUED'
        )
        db.session.add(new_processing_task)
        db.session.commit()
        task = process_audio_file.delay(
            new_processing_task.id,
            filepath,
            filename,
            user_id_int,
            options
        )
        new_processing_task.celery_task_id = task.id
        db.session.commit()
        status_url = f"/audio/task-status/{new_processing_task.id}"
        return jsonify({
            "message": "File uploaded and queued for processing",
            "status_url": status_url,
        }), 202
    user_object = db.session.get(User, user_id_int)
    user_email = user_object.email if user_object else "Nieznany"
    current_year = datetime.now(UTC).year
    return render_template('upload_audio.html', user_email=user_email, current_year=current_year)

@bp.route('/history', methods=['GET'])
@login_required
def get_processing_history():
    user_id_to_query = _get_user_id_from_request_or_current_user()
    if user_id_to_query is None:
        return jsonify({"error": "User ID not found or not authenticated."}), 401
    user_object = db.session.get(User, user_id_to_query)
    user_email = user_object.email if user_object else "Nieznany"
    audio_files = AudioFile.query.filter_by(user_id=user_id_to_query).order_by(AudioFile.upload_date.desc()).all()
    results = []
    for af in audio_files:
        processed_file_url = None
        if af.processed_filename and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], af.processed_filename)):
            processed_file_url = f"/uploads/{af.processed_filename}"
        task = ProcessingTask.query.filter_by(audio_file_id=af.id).order_by(ProcessingTask.created_at.desc()).first()
        results.append({
            "audio_file_id": af.id,
            "original_filename": af.original_filename,
            "upload_date": af.upload_date.isoformat(),
            "file_size_bytes": af.file_size_bytes,
            "processed_filename": af.processed_filename,
            "loudness_lufs": af.loudness_lufs,
            "true_peak_db": af.true_peak_db,
            "duration_seconds": af.duration_seconds,
            "current_status": task.status if task else "NO_TASK",
            "task_id": task.id if task else None,
            "task_status_url": f"/audio/task-status/{task.id}" if task else None,
            "processed_file_url": processed_file_url
        })
    current_year = datetime.now(UTC).year 
    return render_template('history.html', history_data=results, user_email=user_email, current_year=current_year)

@bp.route('/task-status/<int:task_id>', methods=['GET'])
@login_required
def get_task_status(task_id):
    user_id_to_query = _get_user_id_from_request_or_current_user()
    if user_id_to_query is None:
        return jsonify({"error": "User ID not found"}), 401
    task_entry = db.session.get(ProcessingTask, task_id)
    if not task_entry or task_entry.user_id != user_id_to_query:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({
        "status": task_entry.status,
        "result": task_entry.result_json,
    }), 200

@bp.route('/file/<int:file_id>')
@login_required
def file_details(file_id):
    """
    Szczegółowa strona pojedynczego pliku audio z analizą i historią.
    """
    user_id = int(current_user.get_id())
    audio_file = db.session.get(AudioFile, file_id)
    
    if not audio_file or audio_file.user_id != user_id:
        return redirect(url_for('audio_processing.get_processing_history'))
    
    # Get processing task
    task = ProcessingTask.query.filter_by(audio_file_id=file_id).order_by(
        ProcessingTask.created_at.desc()
    ).first()
    
    # Get processed file URL
    processed_file_url = None
    if audio_file.processed_filename and os.path.exists(
        os.path.join(current_app.config['UPLOAD_FOLDER'], audio_file.processed_filename)
    ):
        processed_file_url = f"/uploads/{audio_file.processed_filename}"
    
    # Parse result JSON for additional data
    result_data = {}
    if task and task.result_json:
        try:
            result_data = json.loads(task.result_json)
        except:
            pass
    
    current_year = datetime.now(UTC).year
    return render_template(
        'file_details.html',
        file=audio_file,
        task=task,
        processed_file_url=processed_file_url,
        result_data=result_data,
        user_email=current_user.email,
        current_year=current_year
    )

@bp.route('/download-multiple', methods=['POST'])
@login_required
def download_multiple():
    """
    Pobierz wiele plików jako archiwum ZIP.
    """
    from flask import send_file
    import zipfile
    import io
    
    data = request.get_json()
    if not data or 'ids' not in data:
        return jsonify({"error": "Missing file IDs"}), 400
    
    file_ids = data['ids']
    user_id = int(current_user.get_id())
    
    # Create ZIP in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_id in file_ids:
            audio_file = db.session.get(AudioFile, int(file_id))
            if audio_file and audio_file.user_id == user_id and audio_file.processed_filename:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], audio_file.processed_filename)
                if os.path.exists(file_path):
                    zf.write(file_path, audio_file.processed_filename)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'wavebulk_files_{datetime.now(UTC).strftime("%Y%m%d_%H%M%S")}.zip'
    )

@bp.route('/delete-files', methods=['POST'])
@login_required
def delete_files():
    data = request.get_json()
    if not data or 'ids' not in data:
        return jsonify({"error": "Missing file IDs"}), 400
    ids_to_delete = data['ids']
    if not isinstance(ids_to_delete, list):
        return jsonify({"error": "IDs must be a list"}), 400
    current_user_id = int(current_user.get_id())
    deleted_count = 0
    errors = []
    for file_id in ids_to_delete:
        try:
            audio_file = db.session.get(AudioFile, int(file_id))
            if not audio_file:
                continue 
            if audio_file.user_id != current_user_id:
                errors.append(f"File ID {file_id} not owned by user.")
                continue 
            if audio_file.processing_task:
                db.session.delete(audio_file.processing_task)
            if os.path.exists(audio_file.original_file_path):
                os.remove(audio_file.original_file_path)
            if audio_file.processed_file_path and os.path.exists(audio_file.processed_file_path):
                os.remove(audio_file.processed_file_path)
            db.session.delete(audio_file)
            deleted_count += 1
        except Exception as e:
            errors.append(f"Error deleting file ID {file_id}: {str(e)}")
            db.session.rollback()
            continue
    if not errors:
        db.session.commit()
        return jsonify({"message": f"Successfully deleted {deleted_count} files."}), 200
    else:
        db.session.commit()
        return jsonify({"message": f"Completed with errors. Deleted {deleted_count} files.", "errors": errors}), 207

@bp.route('/pricing')
def pricing():
    user_email = current_user.email if current_user.is_authenticated else None
    current_year = datetime.now(UTC).year
    return render_template('pricing.html', user_email=user_email, current_year=current_year)
