import os
from flask import Blueprint, flash, request, current_app, make_response
from werkzeug.utils import secure_filename
from pathlib import Path

mod = Blueprint('file_handler', __name__)


@mod.route('/', methods=['GET', 'POST'])
def request_file_handler():
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
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        # return redirect(url_for('download_file', name=filename))
        return make_response(f'Created {filename}', 201)
    if request.method == 'GET':
        if all(k in request.args for k in ('file', 'line')):
            requested_path = str(Path(current_app.config['UPLOAD_FOLDER']) / Path(request.args.get('file')))
            if os.path.commonprefix(
                    (os.path.realpath(requested_path), os.path.realpath(current_app.config['UPLOAD_FOLDER']))) \
                    != os.path.realpath(current_app.config['UPLOAD_FOLDER']):
                return make_response('Filename contains illegal characters', 400)
            try:
                with open(requested_path, 'r') as requested_file:
                    return requested_file.readlines()[int(request.args.get('line')) - 1]
            except ValueError:
                return make_response('Line must be an integer', 400)
            except IOError:
                return make_response('file not found', 404)
            except IndexError:
                return make_response('line not found', 422)

    return make_response('Request', 200)
