import pytest
import json
from flask import url_for


@pytest.mark.usefixtures('client_class')
class TestFileHandler:
    def test_post_empty_file(self):
        assert self.client.post(url_for('json_file_z2.request_json_handler')).status_code == 400
        assert self.client.post(url_for('json_file_z3.request_json_handler')).status_code == 400


@pytest.mark.usefixtures('client_class')
class TestJsonHandler:
    def test_post_json(self):
        json_data = json.dumps(
            {
                "test1": "0.1",
                "test2": "21.37"
            })
        assert self.client.post(url_for('json_file_z3.request_json_handler'), json=json_data).status_code == 200
        assert self.client.post(url_for('json_file_z2.request_json_handler'), json=json_data).status_code == 200
