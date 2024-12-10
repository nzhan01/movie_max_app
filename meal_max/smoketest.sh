#!/bin/bash

# Define the base URL for the Flask API
BASE_URL1="http://localhost:5001/api"
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
  local movie_title="$1"  # Movie title as a parameter
  echo "Searching for movie: $movie_title using TMDB API..."

  # Perform the API call
  response=$(curl -s -X GET "$BASE_URL/search/movie" \
    --get \
    --data-urlencode "api_key=$TMDB_API_KEY" \
    --data-urlencode "query=$movie_title")

  # Check if the response is valid JSON
  if ! echo "$response" | jq empty 2>/dev/null; then
    echo "Unexpected response format: Not valid JSON."
    echo "Response: $response"
    exit 1
  fi

  # Check if the response contains results
  if echo "$response" | jq -e '.results | length > 0' > /dev/null; then
    echo "Search successful for movie: $movie_title."
    if [ "$ECHO_JSON" = true ]; then
      echo "Search Results JSON:"
      echo "$response" | jq '.results'
    else
      # Print the first result
      echo "Top result:"
      echo "$response" | jq '.results[0]'
    fi
  else
    echo "No results found for movie: $movie_title."
    exit 1
  fi
}

# Function to get where movie is available for viewing
get_movie_providers(){
  local movie_id="$1"
  echo "Fetching providers for movie ID: $movie_id..."

  response=$(curl -s -X GET "$BASE_URL/movie/$movie_id/watch/providers?api_key=$TMDB_API_KEY")

  if ! echo "$response" | jq empty 2>/dev/null; then
    echo "Unexpected response format: Not valid JSON."
    echo "Response: $response"
    exit 1
  fi

  echo "Movie Providers:"
  echo "$response" | jq .
}

#Function to fetch movie details by ID
get_movie_details(){
  local movie_id="$1"
  echo "Fetching details for movie ID: $movie_id..."

  response=$(curl -s -X GET "$BASE_URL/movie/$movie_id?api_key=$TMDB_API_KEY")

  if ! echo "$response" | jq empty 2>/dev/null; then
    echo "Unexpected response format: Not valid JSON."
    echo "Response: $response"
    exit 1
  fi

  echo "Movie Details:"
  echo "$response" | jq .
}
#Function to get recommended movies based on the given movie ID.
get_recommendations(){
  local movie_id="$1"
  echo "Fetching recommendations for movie ID: $movie_id..."

  response=$(curl -s -X GET "$BASE_URL/movie/$movie_id/recommendations?api_key=$TMDB_API_KEY")

  if ! echo "$response" | jq empty 2>/dev/null; then
    echo "Unexpected response format: Not valid JSON."
    echo "Response: $response"
    exit 1
  fi

  echo "Movie Recommendations:"
  echo "$response" | jq .
}
#Function to get the most popular movies
get_movie_popularity(){
  local movie_id="$1"
  echo "Fetching popularity for movie ID: $movie_id..."

  response=$(curl -s -X GET "$BASE_URL/movie/$movie_id?api_key=$TMDB_API_KEY")

  if ! echo "$response" | jq empty 2>/dev/null; then
    echo "Unexpected response format: Not valid JSON."
    echo "Response: $response"
    exit 1
  fi

  popularity=$(echo "$response" | jq '.popularity')
  echo "Movie Popularity: $popularity"
}
#Retrieves the watchlist for a given user.
get_watchlist(){
  local username="$1"
  echo "Fetching watchlist for user: $username..."

  response=$(curl -s -X GET "$BASE_URL1/watchlist/$username")

  # Validate response JSON format
  if ! echo "$response" | jq empty 2>/dev/null; then
    echo "Unexpected response format: Not valid JSON."
    echo "Response: $response"
    exit 1
  fi

  # Display the watchlist
  echo "User Watchlist:"
  echo "$response" | jq .
}
#Add a movie from the user's watchlist.
add_to_watchlist(){
  local username="$1"
  local movie_id="$2"
  local movie_title="$3"
  echo "Adding movie: $movie_title to $username's watchlist..."

  response=$(curl -s -X POST "$BASE_URL1/watchlist/add" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\", \"movie_id\": $movie_id, \"movie_title\": \"$movie_title\"}")

  # Validate response JSON format
  if ! echo "$response" | jq empty 2>/dev/null; then
    echo "Unexpected response format: Not valid JSON."
    echo "Response: $response"
    exit 1
  fi

  # Display the response
  echo "Add to Watchlist Response:"
  echo "$response" | jq .
}
#Remove a movie from the user's watchlist.
remove_from_watchlist(){
  local username="$1"
  local movie_id="$2"
  echo "Removing movie with ID: $movie_id from $username's watchlist..."

  response=$(curl -s -X DELETE "$BASE_URL1/watchlist/remove" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$username\", \"movie_id\": $movie_id}")

  # Validate response JSON format
  if ! echo "$response" | jq empty 2>/dev/null; then
    echo "Unexpected response format: Not valid JSON."
    echo "Response: $response"
    exit 1
  fi

  # Display the response
  echo "Remove from Watchlist Response:"
  echo "$response" | jq .
}
# Run all the steps in order
check_health
init_db
create_user
login_user
search_movie "Inception"
get_movie_details 550  # Movie ID for "Fight Club"
get_watchlist "test_user"
add_to_watchlist "test_user" 550 "Fight Club"
get_movie_providers 550  # Movie ID for "Fight Club"
get_recommendations 550  # Movie ID for "Fight Club"
get_movie_popularity 550  # Movie ID for "Fight Club"
remove_from_watchlist "test_user" 550 

echo "All tests passed successfully!"