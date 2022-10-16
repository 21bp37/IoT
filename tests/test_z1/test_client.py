from pisklak_client.z1.app1 import post_file, get_line
import pytest


@pytest.mark.usefixtures('client_class')
def test_server_connection(tmp_path):
    file_path = tmp_path / 'test_file.txt'
    with open(file_path, 'w+') as test_post:
        test_post.write('line1\nline2')
    assert post_file(file_path).status_code == 200
    assert get_line('test_file.txt', 2) == 'line2'

