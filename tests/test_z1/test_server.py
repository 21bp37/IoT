import pytest
import io
from flask import request


@pytest.mark.usefixtures('client_class')
class TestFileHandler:
    def test_post_get_file(self):
        data = {
            'file': (io.BytesIO(b"test_line1\ntest_line2"), 'test_file.txt')
        }
        assert self.client.post(request.host_url, data=data).status_code == 201
        assert self.client.get(f'{request.host_url}?file=test_file.txt&line=2').data.decode() == 'test_line2'

    def test_post_missing_file(self):
        assert self.client.post(request.host_url).status_code == 422

    def test_post_missing_filename(self):
        data = {
            'file': (io.BytesIO(b"test_line1\ntest_line2"), '')
        }
        assert self.client.post(request.host_url, data=data).status_code == 400

    def test_get_path_traversal(self):
        assert self.client.get(f'{request.host_url}?file=../pisklak/__init__.py&line=2'
                               ).data.decode() == 'Filename contains illegal characters'
        assert self.client.get(f'{request.host_url}?file=../pisklak/__init__.py&line=2').status_code == 400

    def test_get_non_integer_line(self):
        assert self.client.get(f'{request.host_url}?file=test_file.txt&line=0.1').status_code == 400

    def test_get_line_does_not_exists(self):
        assert self.client.get(f'{request.host_url}?file=test_file.txt&line=22').status_code == 422

    def test_get_file_does_not_exists(self):
        assert self.client.get(f'{request.host_url}?file=file_that_not.exists&line=12').status_code == 404
