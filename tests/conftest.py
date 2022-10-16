import pytest
from pisklak import create_app


@pytest.fixture(scope="session")
def app(tmpdir_factory):
    app = create_app()
    app.config['UPLOAD_FOLDER'] = tmpdir_factory.mktemp('uploads')
    return app
