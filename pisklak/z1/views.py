import os
from flask import Blueprint, flash, request, current_app, make_response, Response
from werkzeug.utils import secure_filename
from pathlib import Path

mod = Blueprint('file_handler', __name__)


@mod.route('/', methods=['GET', 'POST'])
def request_file_handler() -> Response:
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            # return redirect(request.url)
            return make_response('No file part', 422)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            # return redirect(request.url)
            return make_response('File not found', 400)
        filename = secure_filename(str(file.filename))
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        # return redirect(url_for('download_file', name=filename))
        return make_response(f'Created {filename}', 201)
    if request.method == 'GET':
        if all(k in request.args for k in ('file', 'line')):
            try:
                requested_path = Path(str(current_app.config['UPLOAD_FOLDER'])) / str(request.args.get('file'))
            except (ValueError, TypeError):
                return make_response('file not found', 404)
            if os.path.commonprefix(
                    (os.path.realpath(requested_path), os.path.realpath(current_app.config['UPLOAD_FOLDER']))) \
                    != os.path.realpath(current_app.config['UPLOAD_FOLDER']):
                return make_response('Filename contains illegal characters', 400)
            try:
                with open(requested_path, 'r') as requested_file:
                    return make_response(requested_file.readlines()[int(str(request.args.get('line'))) - 1], 200)
            except (ValueError, TypeError):
                return make_response('Line must be an integer', 400)
            except IOError:
                return make_response('file not found', 404)
            except IndexError:
                return make_response('line not found', 422)

    return make_response('Request', 200)
