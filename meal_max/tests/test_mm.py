import pytest

from models.movie_model import Movie
from models.user_model import Users



def test_search_movie():
    movie = "Inception"
    results = Movie.search_movie(movie)
    assert len(results) > 0


def test_get_movie_providers():
    movie_id = 27205
    results = Movie.get_movie_providers(movie_id)
    
    assert "US" in results["results"]
    
    # Check if "flatrate" exists in the "US" region
    assert "flatrate" in results["results"]["US"]
    
    # Ensure "flatrate" contains at least one provider
    assert len(results["results"]["US"]["flatrate"]) > 0
    
    # Check the first provider in "flatrate"
    first_provider = results["results"]["US"]["flatrate"][0]
    assert first_provider["provider_name"] == "Peacock Premium" 
    assert first_provider["provider_id"] == 386



def test_get_recommendations():
    movie_id = 27205
    results = Movie.get_recommendations(movie_id)
    
    assert len(results) > 0
    # Check that the list has at least one recommendation
    assert results[0]["title"] == "The Dark Knight"
    assert results[0]["vote_average"] == 8.5
    
    


def test_get_movie_details():
    movie_id = 27205
    results = Movie.get_movie_details(movie_id)
    assert len(results) > 0
    assert "title" in results
    assert results["title"] == "Inception"
    assert results["vote_average"] == 8.4
    assert results["id"] == 27205


def test_get_popular_movies():
    results = Movie.get_popular_movies()
    assert "results" in results
    assert len(results["results"]) > 0
    assert "title" in results["results"][0]
    assert results["results"][0]["title"] == "Venom: The Last Dance"