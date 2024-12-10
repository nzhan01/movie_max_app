#!/bin/bash

# Define the base URL for the Flask API
BASE_URL1="http://localhost:5000/api"
#Define the base URL for the TMDB API
BASE_URL="https://api.themoviedb.org/3"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL1/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

##############################################
#
# User management
#
##############################################

# Function to create a user
create_user() {
  echo "Creating a new user..."
  curl -s -X POST "$BASE_URL1/create-user" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}' | grep -q '"status": "user added"'
  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    exit 1
  fi
}

# Function to log in a user
login_user() {
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL1/login" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')
  if echo "$response" | grep -q '"message": "User testuser logged in successfully."'; then
    echo "User logged in successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log in user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to log out a user
logout_user() {
  echo "Logging out user..."
  response=$(curl -s -X POST "$BASE_URL1/logout" -H "Content-Type: application/json" \
    -d '{"username":"testuser"}')
  if echo "$response" | grep -q '"message": "User testuser logged out successfully."'; then
    echo "User logged out successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Logout Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log out user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}



# Function to initialize the database
init_db() {
  echo "Initializing the database..."
  response=$(curl -s -X POST "$BASE_URL1/init-db")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Database initialized successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Initialization Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initialize the database."
    exit 1
  fi
}


# Function to search a movie 
search_movie(){
  local movie_title="$1"
  echo "Searching for movie: $movie_title..."

  # Perform the API call
  response=$(curl -s -X GET "$BASE_URL/search?title=$movie_title")

  # Check if the response contains valid data
  if echo "$response" | grep -q '"title":'; then
    echo "Search successful for movie: $movie_title."
    if [ "$ECHO_JSON" = true ]; then
      echo "Search Results JSON:"
      echo "$response" | jq .
    fi
  elif echo "$response" | grep -q '"error":'; then
    echo "Search failed: $(echo "$response" | jq -r '.error')"
    exit 1
  else
    echo "Unexpected response format."
    exit 1
  fi

}

# Function to get where movie is available for viewing
get_movie_providers(){
  local movie_id=27205  # Movie ID for Inception
  echo "Testing /movie/${movie_id}/providers..."

  response=$(curl -s -X GET "$BASE_URL/$movie_id/providers")
  
  if echo "$response" | grep -q '"US"'; then
    echo "Movie providers fetched successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi

    flatrate=$(echo "$response" | jq -r '.results.US.flatrate[0].provider_name')
    if [ "$flatrate" = "Peacock Premium" ]; then
      echo "Provider validation passed."
    else
      echo "Provider validation failed: Expected 'Peacock Premium', got '$flatrate'."
      exit 1
    fi
  else
    echo "Failed to fetch movie providers."
    exit 1
  fi
}

#Function to fetch movie details by ID
get_movie_details(){
  local movie_id=27205  # Movie ID for Inception
  echo "Testing /movie/${movie_id}..."

  response=$(curl -s -X GET "$BASE_URL/$movie_id")
  
  if echo "$response" | grep -q '"title": "Inception"'; then
    echo "Movie details fetched successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch movie details."
    exit 1
  fi
}
#Function to get recommended movies based on the given movie ID.
get_recommendations(){
  local movie_id=27205  # Movie ID for Inception
  echo "Testing /movie/${movie_id}/recommendations..."

  response=$(curl -s -X GET "$BASE_URL/$movie_id/recommendations")
  
  if echo "$response" | grep -q '"title": "The Dark Knight"'; then
    echo "Recommendations fetched successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch recommendations."
    exit 1
  fi
}
#Function to get the most popular movies
get_movie_popularity(){
  echo "Testing /movie/popular..."

  response=$(curl -s -X GET "$BASE_URL/popular")
  
  if echo "$response" | grep -q '"title": "Venom: The Last Dance"'; then
    echo "Popular movies fetched successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch popular movies."
    exit 1
  fi
}
#Retrieves the watchlist for a given user.
get_watchlist(){
  echo "Testing retrieving watchlist for user '$USERNAME'..."

  response=$(curl -s -X GET "$BASE_URL/$USERNAME")

  if echo "$response" | grep -q '"movie_title"'; then
    echo "Watchlist retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve watchlist."
    exit 1
  fi
}
#Add a movie from the user's watchlist.
add_to_watchlist(){
  local movie_title="$1"
  echo "Testing adding '$movie_title' to $USERNAME's watchlist..."

  response=$(curl -s -X POST "$BASE_URL/add" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$USERNAME\", \"movie_title\": \"$movie_title\"}")

  if echo "$response" | grep -q '"message"'; then
    echo "Movie '$movie_title' added to watchlist successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  elif echo "$response" | grep -q '"error"'; then
    echo "Failed to add movie: $(echo "$response" | jq -r '.error')"
    exit 1
  else
    echo "Unexpected response format."
    exit 1
  fi
}
#Remove a movie from the user's watchlist.
remove_from_watchlist(){
  local movie_title="$1"
  echo "Testing removing '$movie_title' from $USERNAME's watchlist..."

  response=$(curl -s -X DELETE "$BASE_URL/remove" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$USERNAME\", \"movie_title\": \"$movie_title\"}")

  if echo "$response" | grep -q '"message"'; then
    echo "Movie '$movie_title' removed from watchlist successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  elif echo "$response" | grep -q '"error"'; then
    echo "Failed to remove movie: $(echo "$response" | jq -r '.error')"
    exit 1
  else
    echo "Unexpected response format."
    exit 1
  fi
}
# Run all the steps in order
check_health
init_db
create_user
login_user
search_movie "Inception"
get_movie_details
get_watchlist
add_to_watchlist "Inception"
get_movie_providers
get_recommendations
get_movie_popularity
remove_from_watchlist "Inception"

echo "All tests passed successfully!"