"""
FastAPI Application Tests using AAA (Arrange-Act-Assert) Pattern

Tests cover:
- GET /activities endpoint
- POST /activities/{activity_name}/signup endpoint
- POST /activities/{activity_name}/unregister endpoint
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture providing a test client for the FastAPI app"""
    return TestClient(app)


# GET /activities Tests

def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities"""
    # Arrange
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Art Studio",
        "Drama Club",
        "Science Club",
        "Debate Team"
    ]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) == len(expected_activities)
    for activity_name in expected_activities:
        assert activity_name in activities


def test_get_activities_contains_required_fields(client):
    """Test that each activity has required fields"""
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    for activity_name, activity_data in activities.items():
        assert set(activity_data.keys()) == required_fields


def test_get_activities_participants_is_list(client):
    """Test that participants field is always a list"""
    # Arrange & Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["participants"], list)


# POST /activities/{activity_name}/signup Tests

def test_signup_success(client):
    """Test successfully signing up a new participant"""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_adds_participant_to_activity(client):
    """Test that signup actually adds participant to the activity list"""
    # Arrange
    activity_name = "Art Studio"
    email = "newartist@mergington.edu"

    # Act
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_email_error(client):
    """Test that duplicate signup returns 400 error"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity_error(client):
    """Test that signup for non-existent activity returns 404 error"""
    # Arrange
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


# POST /activities/{activity_name}/unregister Tests

def test_unregister_success(client):
    """Test successfully unregistering a participant"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_unregister_removes_participant_from_activity(client):
    """Test that unregister actually removes participant from activity"""
    # Arrange
    activity_name = "Drama Club"
    email = "lucas@mergington.edu"  # Already signed up

    # Act
    client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert email not in activities[activity_name]["participants"]


def test_unregister_participant_not_signed_up_error(client):
    """Test that unregistering non-existent participant returns 400 error"""
    # Arrange
    activity_name = "Basketball Team"
    email = "notstudent@mergington.edu"  # Not signed up

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"].lower()


def test_unregister_nonexistent_activity_error(client):
    """Test that unregister from non-existent activity returns 404 error"""
    # Arrange
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


# Workflow Tests (Multiple steps)

def test_signup_then_unregister_workflow(client):
    """Test full workflow of signing up then unregistering"""
    # Arrange
    activity_name = "Tennis Club"
    email = "newplayer@mergington.edu"

    # Act - Sign up
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert signup
    assert signup_response.status_code == 200
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

    # Act - Unregister
    unregister_response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )

    # Assert unregister
    assert unregister_response.status_code == 200
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
