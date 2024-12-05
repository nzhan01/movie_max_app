#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

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
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Meal Management
#
##########################################################

# Add meal
create_meal() {
  meal_name=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal_name, Cuisine: $cuisine) to the kitchen..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal_name\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    echo "Response from server: $response"  # Print response for debugging
    exit 1
  fi
}

clear_meals() {
  echo "Clearing all meals from the kitchen..."
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All meals cleared successfully."
  else
    echo "Failed to clear meals."
    echo "Response from server: $response"
    exit 1
  fi
}

# Delete meal by ID
delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    echo "Response from server: $response"
    exit 1
  fi
}

delete_meal_by_name() {
  meal_name=$1
  echo "Deleting meal by name ($meal_name)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by name ($meal_name)."
  else
    echo "Failed to delete meal by name ($meal_name)."
    echo "Response from server: $response"
    exit 1
  fi
}


# Get meal by ID
get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    echo "Response from server: $response"
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1
  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name: $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal_name)."
    echo "Response from server: $response"
    exit 1
  fi
}


############################################################
#
# Combatant Management
#
############################################################

clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Clear Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to clear combatants."
    echo "Response from server: $response"
    exit 1
  fi
}

get_combatants() {
  echo "Getting combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Get Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get combatants."
    echo "Response from server: $response"
    exit 1
  fi
}

prep_combatant() {
  local meal_name="$1"
  echo "Preparing combatant: $meal_name..."
  
  # Ensure meal_name is properly escaped for JSON
  prep_data="{\"meal\": \"$meal_name\"}"
  
  # Make the POST request to prepare the combatant
  response=$(curl -s -X POST -H "Content-Type: application/json" -d "$prep_data" "$BASE_URL/prep-combatant")

  # Check if the response indicates success
  if echo "$response" | grep -q '"status": "combatant prepared"'; then
    echo "Combatant prepared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Prep Combatant JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to prepare combatant."
    echo "Response: $response"  # Output the full response for debugging
    exit 1
  fi
}


############################################################
#
# Battle Management
#
############################################################

battle() {
  echo "Initiating a battle between prepared meals..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle executed successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Result JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initiate battle."
    echo "Response from server: $response"
    exit 1
  fi
}

get_leaderboard() {
  echo "Retrieving leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}


# Health checks
check_health
check_db

# Clear the catalog
clear_meals

# Meal Management Tests
create_meal "Spaghetti" "Italian" 10.99 "MED"
create_meal "Sushi" "Japanese" 12.99 "LOW"
create_meal "Burger" "American" 8.99 "HIGH"

delete_meal_by_id 1

# Retrieve meals by name to confirm they were added correctly
get_meal_by_id 2
get_meal_by_name "Sushi"


prep_combatant "Sushi"
prep_combatant "Burger"

get_combatants



# Battle Management Tests

battle 

clear_combatants

# Leaderboard
get_leaderboard

echo "All tests passed successfully!"
