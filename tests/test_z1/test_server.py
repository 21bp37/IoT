import pytest
import json
import io
from flask import request, url_for


@pytest.mark.usefixtures('client_class')
class TestFileHandler:
    def test_post_get_file(self) -> None:
        data = {
            'file': (io.BytesIO(b"test_line1\ntest_line2"), 'test_file.txt')
        }
        assert self.client.post(request.host_url, data=data).status_code == 201
        assert self.client.get(f'{request.host_url}?file=test_file.txt&line=2').data.decode() == 'test_line2'

    def test_post_missing_file(self) -> None:
        assert self.client.post(request.host_url).status_code == 422

    def test_post_missing_filename(self) -> None:
        data = {
            'file': (io.BytesIO(b"test_line1\ntest_line2"), '')
        }
        assert self.client.post(request.host_url, data=data).status_code == 400

    def test_get_path_traversal(self) -> None:
        assert self.client.get(f'{request.host_url}?file=../pisklak/__init__.py&line=2'
                               ).data.decode() == 'Filename contains illegal characters'
        assert self.client.get(f'{request.host_url}?file=../pisklak/__init__.py&line=2').status_code == 400

    def test_get_non_integer_line(self) -> None:
        assert self.client.get(f'{request.host_url}?file=preloaded_file.txt&line=0.1').status_code == 400

    def test_get_line_does_not_exists(self) -> None:
        assert self.client.get(f'{request.host_url}?file=preloaded_file.txt&line=22').status_code == 422

    def test_get_file_does_not_exists(self) -> None:
        assert self.client.get(f'{request.host_url}?file=file_that_not.exists&line=12').status_code == 404


@pytest.mark.usefixtures('client_class')
class TestJsonHandler:
    def test_post_json(self):
        json_data = json.dumps(
            {
                "test1": "0.1",
                "test2": "21.37"
            })
        assert self.client.post(url_for('json_file.request_json_handler'), json=json_data).status_code == 200
