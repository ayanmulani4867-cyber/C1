import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'zip', 'txt'}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file_storage, subfolder='documents', prefix='', is_image=False):
    """
    Saves an uploaded file to the configured upload folder with a sanitized, unique filename.
    Validates extension and returns relative path under static/ (e.g. 'uploads/photos/xyz.jpg') or None if invalid.
    """
    if not file_storage or not hasattr(file_storage, 'filename') or file_storage.filename == '':
        return None

    filename = secure_filename(file_storage.filename)
    if not filename:
        return None

    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    allowed_exts = ALLOWED_IMAGE_EXTENSIONS if is_image or subfolder == 'photos' else ALLOWED_DOCUMENT_EXTENSIONS
    
    if ext not in allowed_exts:
        return None

    # Generate unique filename
    unique_name = f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}" if prefix else f"{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, unique_name)
    file_storage.seek(0)
    file_storage.save(file_path)

    # Return relative URL/path for template rendering (relative to static)
    return f"uploads/{subfolder}/{unique_name}"


def save_profile_photo(file_storage, prefix='user'):
    """Helper specifically for saving avatar / profile photos"""
    return save_uploaded_file(file_storage, subfolder='photos', prefix=prefix, is_image=True)


def delete_uploaded_file(relative_path):
    """Safely delete a file from the uploads directory if it exists"""
    if not relative_path:
        return
    try:
        full_path = os.path.join(current_app.root_path, 'static', relative_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception:
        pass
