import pytest
from flask import url_for, request


@pytest.mark.usefixtures('client_class')
class TestSuite:

    def test_server_status(self):
        assert self.client.get(request.host_url).status_code == 200

    def test_index(self):
        assert self.client.get(url_for('index')).status_code == 200
