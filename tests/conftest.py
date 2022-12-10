import pytest
from pisklak.manager import run_manager
import os


@pytest.fixture(scope="session")
def app(tmpdir_factory):
    app = run_manager()
    uploads = tmpdir_factory.mktemp('uploads')
    os.mkdir(uploads / 'z2')
    os.mkdir(uploads / 'z3')
    app.config['UPLOAD_FOLDER'] = uploads
    with open(uploads / 'preloaded_file.txt', 'w+') as file:
        file.write('test_line1\ntest_line2')
    return app
