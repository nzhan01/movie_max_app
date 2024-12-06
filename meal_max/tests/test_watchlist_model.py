import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from meal_max.models.watchlist_model import Watchlist
from meal_max.models.user_model import Users
from db import db



@pytest.fixture
def mock_user():
    """Fixture for a mock user."""
    return MagicMock(id=1, username="test_user")


@pytest.fixture
def mock_watchlist_entry():
    """Fixture for a mock watchlist entry."""
    return MagicMock(id=1, movie_title="Inception", added_on=datetime.utcnow(), watched=False)


def test_add_to_watchlist_user_not_found(mocker):
    """Test adding a movie to the watchlist when the user does not exist."""
    mocker.patch("watchlist.Users.query.filter_by", return_value=MagicMock(first=lambda: None))

    with pytest.raises(ValueError, match="User 'test_user' not found."):
        Watchlist.add_to_watchlist("test_user", "Inception")


def test_add_to_watchlist_duplicate_entry(mocker, mock_user):
    """Test adding a movie already in the user's watchlist."""
    mocker.patch("watchlist.Users.query.filter_by", return_value=MagicMock(first=lambda: mock_user))
    mocker.patch("watchlist.Watchlist.query.filter_by", return_value=MagicMock(first=lambda: True))

    with pytest.raises(ValueError, match="Movie 'Inception' already exists in the watchlist."):
        Watchlist.add_to_watchlist("test_user", "Inception")


def test_add_to_watchlist_success(mocker, mock_user):
    """Test successfully adding a movie to the watchlist."""
    mocker.patch("watchlist.Users.query.filter_by", return_value=MagicMock(first=lambda: mock_user))
    mocker.patch("watchlist.Watchlist.query.filter_by", return_value=MagicMock(first=lambda: None))
    mock_db_session = mocker.patch("watchlist.db.session")
    
    result = Watchlist.add_to_watchlist("test_user", "Inception")
    
    assert result == {"message": "Movie added to watchlist", "movie_title": "Inception"}
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_get_watchlist_user_not_found(mocker):
    """Test retrieving a watchlist when the user does not exist."""
    mocker.patch("watchlist.Users.query.filter_by", return_value=MagicMock(first=lambda: None))

    with pytest.raises(ValueError, match="User 'test_user' not found."):
        Watchlist.get_watchlist("test_user")


def test_get_watchlist_success(mocker, mock_user, mock_watchlist_entry):
    """Test successfully retrieving a watchlist."""
    mocker.patch("watchlist.Users.query.filter_by", return_value=MagicMock(first=lambda: mock_user))
    mocker.patch("watchlist.Watchlist.query.filter_by", return_value=MagicMock(all=lambda: [mock_watchlist_entry]))

    result = Watchlist.get_watchlist("test_user")
    
    expected_result = [
        {"id": 1, "movie_title": "Inception", "added_on": mock_watchlist_entry.added_on, "watched": False}
    ]
    assert result == expected_result


def test_remove_from_watchlist_user_not_found(mocker):
    """Test removing a movie from the watchlist when the user does not exist."""
    mocker.patch("watchlist.Users.query.filter_by", return_value=MagicMock(first=lambda: None))

    with pytest.raises(ValueError, match="User 'test_user' not found."):
        Watchlist.remove_from_watchlist("test_user", "Inception")


def test_remove_from_watchlist_entry_not_found(mocker, mock_user):
    """Test removing a movie not in the user's watchlist."""
    mocker.patch("watchlist.Users.query.filter_by", return_value=MagicMock(first=lambda: mock_user))
    mocker.patch("watchlist.Watchlist.query.filter_by", return_value=MagicMock(first=lambda: None))

    with pytest.raises(ValueError, match="Movie 'Inception' not found in the watchlist."):
        Watchlist.remove_from_watchlist("test_user", "Inception")


def test_remove_from_watchlist_success(mocker, mock_user, mock_watchlist_entry):
    """Test successfully removing a movie from the watchlist."""
    mocker.patch("watchlist.Users.query.filter_by", return_value=MagicMock(first=lambda: mock_user))
    mocker.patch("watchlist.Watchlist.query.filter_by", return_value=MagicMock(first=lambda: mock_watchlist_entry))
    mock_db_session = mocker.patch("watchlist.db.session")

    result = Watchlist.remove_from_watchlist("test_user", "Inception")
    
    assert result == {"message": "Movie removed from watchlist", "movie_title": "Inception"}
    mock_db_session.delete.assert_called_once_with(mock_watchlist_entry)
    mock_db_session.commit.assert_called_once()