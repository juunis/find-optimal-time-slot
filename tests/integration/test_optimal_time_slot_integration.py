import os
import requests
import pytest

API_URL = os.getenv("API_URL")  # Set in GitHub Actions or locally

@pytest.fixture
def post_event():
    def _post(event):
        if not API_URL:
            pytest.skip("API_URL not set, skipping integration test")
        headers = {"Content-Type": "application/json"}
        return requests.post(f"{API_URL}", json=event, headers=headers)
    return _post


def test_single_optimal_time_slot(post_event):
    event = {
        "meetingName": "Design Sync",
        "participants": [
            {"name": "Alice", "preferredSlots": ["2024-06-10T09:00", "2024-06-10T10:00"]},
            {"name": "Bob", "preferredSlots": ["2024-06-10T10:00", "2024-06-10T13:00"]},
            {"name": "Carol", "preferredSlots": ["2024-06-10T10:00"]}
        ]
    }
    response = post_event(event)
    data = response.json()
    assert response.status_code == 200
    assert data["meetingName"] == "Design Sync"
    assert data["maxParticipants"] == 3
    assert data["optimalSlots"][0]["slot"] == "2024-06-10T10:00"


def test_multiple_optimal_slots(post_event):
    event = {
        "meetingName": "Design Sync",
        "participants": [
            {"name": "Alice", "preferredSlots": ["2024-06-10T09:00", "2024-06-10T10:00"]},
            {"name": "Bob", "preferredSlots": ["2024-06-10T10:00", "2024-06-10T09:00"]},
            {"name": "Carol", "preferredSlots": ["2024-06-10T11:00"]}
        ]
    }
    response = post_event(event)
    data = response.json()
    assert response.status_code == 200
    assert data["meetingName"] == "Design Sync"
    assert data["maxParticipants"] == 2
    assert len(data["optimalSlots"]) == 2


def test_no_overlapping_time_slots(post_event):
    event = {
        "meetingName": "Design Sync",
        "participants": [
            {"name": "Alice", "preferredSlots": ["2024-06-10T09:00"]},
            {"name": "Bob", "preferredSlots": ["2024-06-10T10:00"]},
            {"name": "Carol", "preferredSlots": ["2024-06-10T11:00"]}
        ]
    }
    response = post_event(event)
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == "No overlapping time slots found between participants"
    assert data["maxParticipants"] == 1
    assert data["optimalSlots"] == []


def test_invalid_json(post_event):
    if not API_URL:
        pytest.skip("API_URL not set, skipping integration test")
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{API_URL}", data="{invalid json}", headers=headers)
    data = response.json()
    assert response.status_code == 400
    assert data["error"] == "Invalid JSON in request body"


@pytest.mark.parametrize("meeting_name", [None, "", 123, " "])
def test_invalid_meeting_name(post_event, meeting_name):
    event = {
        "meetingName": meeting_name,
        "participants": [{"name": "Alice", "preferredSlots": ["2024-06-10T09:00"]}]
    }
    response = post_event(event)
    data = response.json()
    assert response.status_code == 400
    assert data["error"] == "Missing or invalid required field: meetingName (must be a non-empty string)"


@pytest.mark.parametrize("participants", [None, [], "not a list"])
def test_invalid_participants(post_event, participants):
    event = {
        "meetingName": "Design Sync",
        "participants": participants
    }
    response = post_event(event)
    data = response.json()
    assert response.status_code == 400
    assert data["error"] == "Missing or invalid required field: participants (must be a non-empty list)"


@pytest.mark.parametrize("participant", [
    {"preferredSlots": ["2024-06-10T09:00"]},
    {"name": "", "preferredSlots": ["2024-06-10T09:00"]},
    {"name": 123, "preferredSlots": ["2024-06-10T09:00"]},
    {"name": " ", "preferredSlots": ["2024-06-10T09:00"]},
])
def test_invalid_participant_name(post_event, participant):
    event = {"meetingName": "Design Sync", "participants": [participant]}
    response = post_event(event)
    data = response.json()
    assert response.status_code == 400
    assert data["error"] == "Missing or invalid required field: name (must be a non-empty string)"


@pytest.mark.parametrize("participant", [
    {"name": "Alice"},
    {"name": "Alice", "preferredSlots": []},
    {"name": "Alice", "preferredSlots": "2024-06-10T09:00"}
])
def test_invalid_preferred_slots(post_event, participant):
    event = {"meetingName": "Design Sync", "participants": [participant]}
    response = post_event(event)
    data = response.json()
    assert response.status_code == 400
    assert data["error"] == f"Participant 'Alice' has a missing or invalid required field: preferredSlots (must be a non-empty list)"


@pytest.mark.parametrize("preferred_slot", [
    202406100900,
    ["06-10-2024 09:00"]
])
def test_invalid_slot_format(post_event, preferred_slot):
    participant = {"name": "Alice", "preferredSlots": [preferred_slot]}
    event = {"meetingName": "Design Sync", "participants": [participant]}
    response = post_event(event)
    data = response.json()
    assert response.status_code == 400
    assert data["error"] == f"Preferred slot '{preferred_slot}' for participant 'Alice' must be a string in format YYYY-MM-DDTHH:MM"
