import os
from flask import Blueprint, flash, request, current_app
from werkzeug.utils import secure_filename
from pathlib import Path

mod = Blueprint('file_handler', __name__)


@mod.route('/', methods=['GET', 'POST'])
def request_file_handler():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            # return redirect(request.url)
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            # return redirect(request.url)
            return 'File not found'
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        # return redirect(url_for('download_file', name=filename))
        return 'OK'
    if request.method == 'GET':
        if all(k in request.args for k in ('file', 'line')):
            requested_path = str(Path(current_app.config['UPLOAD_FOLDER']) / Path(request.args.get('file')))
            if os.path.commonprefix(
                    (os.path.realpath(requested_path), os.path.realpath(current_app.config['UPLOAD_FOLDER']))) \
                    != os.path.realpath(current_app.config['UPLOAD_FOLDER']):
                return 'Permissions denied'
            try:
                with open(requested_path, 'r') as requested_file:
                    return requested_file.readlines()[int(request.args.get('line')) - 1]
            except ValueError:
                return 'Line must be an integer'
            except IOError:
                return 'file not found'
            except IndexError:
                return 'line not found'

    return 'Request'
