import pytest
from app import app, db

@pytest.fixture(scope="module")
def test_client():
    # Set up the test client
    testing_app = app
    testing_app.config['TESTING'] = True
    with testing_app.test_client() as client:
        with testing_app.app_context():
            # Ensure a clean database for tests
            db.drop_all()
            db.create_all()
        yield client
