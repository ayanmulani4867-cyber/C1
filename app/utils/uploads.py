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
        clean_path = str(relative_path).replace('\\', '/').lstrip('/')
        if clean_path.startswith('static/'):
            clean_path = clean_path[7:]
        full_path = os.path.join(current_app.root_path, 'static', clean_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception:
        pass


def format_profile_image_url(photo_path, name="", bg_color="1e3a8a"):
    """
    Returns a valid, web-accessible URL for a profile image.
    Handles all stored formats (relative paths, full URLs, raw filenames) and provides a clean fallback.
    """
    if not photo_path or not str(photo_path).strip():
        clean_name = str(name).strip() if name else "User"
        parts = [p for p in clean_name.split() if p]
        if len(parts) >= 2:
            initials = f"{parts[0][0]}{parts[1][0]}".upper()
        elif len(parts) == 1:
            initials = parts[0][:2].upper()
        else:
            initials = "U"
        return f"https://ui-avatars.com/api/?name={initials}&background={bg_color}&color=ffffff&size=128&bold=true"

    path_str = str(photo_path).strip().replace('\\', '/')
    if path_str.startswith('http://') or path_str.startswith('https://'):
        return path_str
    if path_str.startswith('/static/'):
        return path_str
    if path_str.startswith('static/'):
        return f"/{path_str}"
    if path_str.startswith('/uploads/'):
        return f"/static{path_str}"
    if path_str.startswith('uploads/'):
        return f"/static/{path_str}"
    if path_str.startswith('photos/'):
        return f"/static/uploads/{path_str}"
    if path_str.startswith('/'):
        return path_str
    return f"/static/uploads/photos/{path_str}"


def format_document_url(file_path):
    """
    Returns a valid, web-accessible URL for an uploaded document file.
    """
    if not file_path or not str(file_path).strip():
        return None
    path_str = str(file_path).strip().replace('\\', '/')
    if path_str.startswith('http://') or path_str.startswith('https://'):
        return path_str
    if path_str.startswith('/static/'):
        return path_str
    if path_str.startswith('static/'):
        return f"/{path_str}"
    if path_str.startswith('/uploads/'):
        return f"/static{path_str}"
    if path_str.startswith('uploads/'):
        return f"/static/{path_str}"
    if path_str.startswith('documents/'):
        return f"/static/uploads/{path_str}"
    if path_str.startswith('/'):
        return path_str
    return f"/static/uploads/documents/{path_str}"

