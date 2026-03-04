"""
Tests for the Mergington High School Activities API
"""

import pytest
import copy
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test."""
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_chess_club(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert "Chess Club" in response.json()

    def test_get_activities_has_required_fields(self, client):
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity in data.values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity


class TestSignupForActivity:
    def test_signup_returns_200(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200

    def test_signup_adds_participant(self, client):
        # Arrange
        email = "teststudent@mergington.edu"
        activity = "Chess Club"

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        assert email in response.json()[activity]["participants"]

    def test_signup_returns_message(self, client):
        # Arrange
        email = "another@mergington.edu"
        activity = "Programming Class"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert "message" in response.json()

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_returns_400(self, client):
        # Arrange
        email = "michael@mergington.edu"  # already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400

    def test_signup_duplicate_does_not_add_twice(self, client):
        # Arrange
        email = "michael@mergington.edu"  # already in Chess Club
        activity = "Chess Club"
        initial_count = len(activities[activity]["participants"])

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert len(activities[activity]["participants"]) == initial_count


class TestUnregisterFromActivity:
    def test_unregister_returns_200(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200

    def test_unregister_removes_participant(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        client.delete(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        assert email not in response.json()[activity]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_unregister_not_signed_up_returns_404(self, client):
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
