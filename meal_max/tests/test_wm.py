import pytest
from meal_max.models.user_model import Users
from meal_max.models.watchlist_model import Watchlist
from meal_max.db.models import db

@pytest.fixture
def setup_user():
    """
    This fixture creates a test user anpy d yields their username. 
    After the test, it rolls back any changes.
    """
    username = "watchlist_tester"
    password = "testpass"
    Users.create_user(username, password)
    yield username
    # Cleanup after tests if needed (users are deleted when db is dropped anyway)

def test_add_to_watchlist(test_client, setup_user):
    """
    Test the add_to_watchlist functionality by adding a movie to the watchlist
    and verifying the database updates.
    """
    username = setup_user

    # Query the user object from the database
    user = Users.query.filter_by(username=username).first()
    assert user is not None, f"User '{username}' not found in the database"

    # Initially, the watchlist should be empty
    initial_watchlist = Watchlist.query.filter_by(user_id=user.id).all()
    assert len(initial_watchlist) == 0

    # Add the movie "Inception" to the watchlist
    response_data, status_code = Watchlist.add_to_watchlist(username, "Inception")  # Unpack tuple

    # Verify the success message and response structure
    assert status_code == 200
    assert response_data["message"] == "'Inception' has been added to the watchlist"

    # Verify the database reflects the addition
    updated_watchlist = Watchlist.query.filter_by(user_id=user.id).all()
    assert len(updated_watchlist) == 1

    # Check the details of the added movie
    added_movie = updated_watchlist[0]
    assert added_movie.movie_title == "Inception"
    assert added_movie.movie_id == 27205  # TMDB ID for "Inception"

'''
def test_add_duplicate_movie(test_client, setup_user):
    username = setup_user
    # Add a movie once
    Watchlist.add_to_watchlist(username, "Inception")
    # Adding it again should raise a ValueError
    with pytest.raises(ValueError) as excinfo:
        Watchlist.add_to_watchlist(username, "Inception")
    assert "already exists in the watchlist" in str(excinfo.value)

def test_remove_from_watchlist(test_client, setup_user):
    username = setup_user
    # Add a movie
    Watchlist.add_to_watchlist(username, "Matrix")
    watchlist = Watchlist.get_watchlist(username)
    assert len(watchlist) == 1

    # Remove the movie
    result = Watchlist.remove_from_watchlist(username, "Matrix")
    assert result["message"] == "Movie removed from watchlist"
    assert result["movie_title"] == "Matrix"

    # Verify watchlist is empty again
    final_watchlist = Watchlist.get_watchlist(username)
    assert len(final_watchlist) == 0

def test_remove_non_existent_movie(test_client, setup_user):
    username = setup_user
    # Attempt to remove a movie that doesn't exist in the watchlist
    with pytest.raises(ValueError) as excinfo:
        Watchlist.remove_from_watchlist(username, "Avatar")
    assert "not found in the watchlist" in str(excinfo.value)

def test_add_watchlist_invalid_user():
    # Add to watchlist for a user that doesn't exist
    with pytest.raises(ValueError) as excinfo:
        Watchlist.add_to_watchlist("no_such_user", "Inception")
    assert "User 'no_such_user' not found." in str(excinfo.value)
'''