import pytest
from pisklak import create_app


@pytest.fixture(scope="session")
def app(tmpdir_factory):
    app = create_app()
    uploads = tmpdir_factory.mktemp('uploads')
    app.config['UPLOAD_FOLDER'] = uploads
    with open(uploads / 'preloaded_file.txt', 'w+') as file:
        file.write('test_line1\ntest_line2')
    return app
