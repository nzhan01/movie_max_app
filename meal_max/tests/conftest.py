import pytest
from meal_max.app import app, db

@pytest.fixture
def setup_user(test_client):
    # Now this fixture runs inside the app context provided by test_client
    username = "watchlist_test"
    password = "testpass"
    Users.create_user(username, password)  # This now works because test_client ensures app context
    yield username




@pytest.fixture(scope="session")
def test_client():
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        client = app.test_client()
        yield client
        db.drop_all()