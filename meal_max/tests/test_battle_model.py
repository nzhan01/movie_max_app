import pytest
from unittest.mock import patch
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture
def battle_model():
    """Fixture to provide a BattleModel instance."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Fixture to provide a mock for the update_meal_stats function."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

@pytest.fixture
def sample_meal1():
    """Fixture to provide a sample Meal instance for testing."""
    return Meal(id=1, meal="Lasagna", cuisine="Italian", price=10.99, difficulty="HIGH")

@pytest.fixture
def sample_meal2():
    """Fixture to provide a sample Meal instance for testing."""
    return Meal(id=2, meal="Burger", cuisine="American", price=12.99, difficulty="LOW")

@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    """Fixture to provide a sample BattleModel instance for testing."""
    return [sample_meal1, sample_meal2]


def test_prep_combatant(battle_model, sample_meal1, sample_meal2):
    """Test adding a combatant to the combatants list."""
    battle_model.prep_combatant(sample_meal1)
    assert battle_model.get_combatants() == [sample_meal1], "First combatant should be added"

    battle_model.prep_combatant(sample_meal2)
    assert battle_model.get_combatants() == [sample_meal1, sample_meal2], "Second combatant should be added"

    # Check for exception when trying to add a third combatant
    with pytest.raises(ValueError, match="Combatant list is full"):
        battle_model.prep_combatant(sample_meal1)

def test_get_combatants(battle_model, sample_battle, sample_meal1, sample_meal2):
    """Test retrieving the combatants list."""
    assert battle_model.get_combatants() == [], "Combatants list should be empty initially"

    """Test retrieving the combatants list."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)

    assert battle_model.get_combatants() == sample_battle, "Combatants list should contain both sample meals"

def test_get_battle_score(battle_model, sample_meal1, sample_meal2):
    """Test calculating the battle score for a combatant."""
    score1 = battle_model.get_battle_score(sample_meal1)
    score2 = battle_model.get_battle_score(sample_meal2)
    assert score1 == (sample_meal1.price * len(sample_meal1.cuisine)) - 1, "Score calculation for meal1 is incorrect"
    assert score2 == (sample_meal2.price * len(sample_meal2.cuisine)) - 3, "Score calculation for meal2 is incorrect"

@patch("meal_max.models.battle_model.get_random", return_value=0.5)
@patch("meal_max.models.battle_model.update_meal_stats")

def test_battle(mock_update_meal_stats, mock_random, battle_model, sample_meal1, sample_meal2):
    """Test conducting a battle between two combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)

    mock_random.return_value = 0.5

    # Simulate a battle between the two combatants
    winner = battle_model.battle()

    # Since the delta (20/100 = 0.2) is less than get_random (0.5), meal2 should win
    assert winner == sample_meal2.meal, "meal2 should be the winner based on battle logic"
    mock_update_meal_stats.assert_any_call(sample_meal2.id, 'win')
    mock_update_meal_stats.assert_any_call(sample_meal1.id, 'loss')

    assert sample_meal1 not in battle_model.get_combatants(), "Losing combatant should be removed from combatants list"
    assert sample_meal2 in battle_model.get_combatants(), "Winning combatant should remain in combatants list"

def test_battle_not_enough_combatants(battle_model, sample_meal1):
    """Test conducting a battle with less than two combatants."""
    battle_model.prep_combatant(sample_meal1)

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle"):
        battle_model.battle()

def test_clear_combatants(battle_model, sample_meal1, sample_meal2):
    """Test clearing the combatants list."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)

    assert len(battle_model.get_combatants()) == 2, "Combatants list should contain two meals"
    battle_model.clear_combatants()
    assert len(battle_model.get_combatants()) == 0, "Combatants list should be empty after clearing"
    assert battle_model.get_combatants() == [], "Combatants list should be empty after clearing"
