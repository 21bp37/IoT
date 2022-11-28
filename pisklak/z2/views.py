import json
from flask import Blueprint, request, current_app, make_response, Response
from pathlib import Path
import logging

mod = Blueprint('json_file_z2', __name__)


@mod.route('/z2', methods=['GET', 'POST'])
def request_json_handler() -> Response:
    if request.method == 'POST':
        content = request.json
        if not content:
            return make_response('No json part', 422)
        if content == '':
            return make_response('Json  not found', 400)
        with open(Path(current_app.config['UPLOAD_FOLDER']) / 'z2' / 'file.json', 'a+') as file_json:
            try:
                file_json.seek(0)
                data = json.load(file_json)
                data.append(json.loads(content))
                file_json.seek(0)
                file_json.truncate()
                json.dump(data, file_json, indent=4)
                return make_response(f'{content}', 200)
            except Exception as e:
                file_json.seek(0)
                json.dump([json.loads(content)], file_json, indent=4)
                logging.warning(e)
                return make_response(f'{content}', 200)

    if request.method == 'GET':
        with open(Path(current_app.config['UPLOAD_FOLDER']) / 'z2' / 'file.json', 'r') as file_json:
            try:
                return make_response(file_json.read(), 200)
            except Exception as e:
                logging.warning(e)
                return make_response('an error occurred', 414)
    return make_response('default', 200)
