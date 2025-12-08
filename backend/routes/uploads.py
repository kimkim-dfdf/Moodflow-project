# ==============================================
# File Upload Routes
# ==============================================

from flask import Blueprint, request, jsonify, send_from_directory
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
import uuid

uploads_bp = Blueprint('uploads', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """Check if a file extension is allowed for upload."""
    if not filename:
        return False
    
    if '.' not in filename:
        return False
    
    parts = filename.rsplit('.', 1)
    extension = parts[1].lower()
    
    if extension in ALLOWED_EXTENSIONS:
        return True
    
    return False


@uploads_bp.route('/upload/photo', methods=['POST'])
@login_required
def upload_photo():
    """Upload a photo for an emotion diary entry."""
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400
    
    file = request.files['photo']
    
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    unique_filename = uuid.uuid4().hex + '_' + filename
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    
    photo_url = '/api/uploads/' + unique_filename
    
    return jsonify({
        'photo_url': photo_url,
        'filename': unique_filename
    })


@uploads_bp.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve an uploaded file."""
    return send_from_directory(UPLOAD_FOLDER, filename)
