import json
from optimal_time_slot_lambda.src.optimal_time_slot_lambda import lambda_handler

def test_single_optimal_time_slot():
    """Should return 200 and give the best time slot"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": "Alice", "preferredSlots": ["2024-06-10T09:00", "2024-06-10T10:00"]},
                {"name": "Bob", "preferredSlots": ["2024-06-10T10:00", "2024-06-10T13:00"]},
                {"name": "Carol", "preferredSlots": ["2024-06-10T10:00"]}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["meetingName"] == "Design Sync"
    assert body["maxParticipants"] == 3
    assert body["optimalSlots"][0]["slot"] == "2024-06-10T10:00"


def test_multiple_optimal_slots():
    """Should return 200 and give multiple optimal time slots"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": "Alice", "preferredSlots": ["2024-06-10T09:00", "2024-06-10T10:00"]},
                {"name": "Bob", "preferredSlots": ["2024-06-10T10:00", "2024-06-10T09:00"]},
                {"name": "Carol", "preferredSlots": ["2024-06-10T11:00"]}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["meetingName"] == "Design Sync"
    assert body["maxParticipants"] == 2
    assert len(body["optimalSlots"]) == 2


def test_no_overlapping_time_slots():
    """Should return 200 and give a message when there are no overlapping time slots"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": "Alice", "preferredSlots": ["2024-06-10T09:00"]},
                {"name": "Bob", "preferredSlots": ["2024-06-10T10:00"]},
                {"name": "Carol", "preferredSlots": ["2024-06-10T11:00"]}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert "No overlapping time slots" in body["message"]
    assert body["maxParticipants"] == 1
    assert body["optimalSlots"] == []


def test_invalid_json():
    """Should return 400 if JSON body is invalid"""

    event = {"body": "{invalid json}"}
    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Invalid JSON in request body"


def test_missing_meeting_name():
    """Should return 400 if meetingName is missing"""

    event = {
        "body": json.dumps({
            "participants": [
                {"name": "Alice", "preferredSlots": ["2024-06-10T09:00"]}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: meetingName (must be a non-empty string)"


def test_empty_meeting_name():
    """Should return 400 if meetingName is empty"""
    
    event = {
        "body": json.dumps({
            "meetingName": "",
            "participants": [
                {"name": "Alice"}
            ]
        })
    }
    
    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: meetingName (must be a non-empty string)"


def test_nonstring_meeting_name():
    """Should return 400 if meetingName is not a string"""

    event = {
        "body": json.dumps({
            "meetingName": 123,
            "participants": [
                {"name": "Alice"}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: meetingName (must be a non-empty string)"


def test_whitespace_meeting_name():
    """Should return 400 if meetingName is only whitespace"""

    event = {
        "body": json.dumps({
            "meetingName": "   ",
            "participants": [
                {"name": "Alice"}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: meetingName (must be a non-empty string)"


def test_missing_participants():
    """Should return 400 if participants is missing"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync"
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: participants (must be a non-empty list)"


def test_empty_participants():
    """Should return 400 if participants is empty"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": []
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: participants (must be a non-empty list)"


def test_nonlist_participants():
    """Should return 400 if participants is not a list"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": "not a list"
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: participants (must be a non-empty list)"


def test_missing_participant_name():
    """Should return 400 if a participant is missing the name field"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"preferredSlots": ["2024-06-10T09:00"]}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: name (must be a non-empty string)"


def test_empty_participant_name():
    """Should return 400 if a participant has an empty name"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": "", "preferredSlots": ["2024-06-10T09:00"]}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: name (must be a non-empty string)"


def test_nonstring_particiant_name():
    """Should return 400 if a participant has a non-string name"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": 123, "preferredSlots": ["2024-06-10T09:00"]}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: name (must be a non-empty string)"


def test_whitespace_participant_name():
    """Should return 400 if a participant has a name with only whitespace"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": " ", "preferredSlots": ["2024-06-10T09:00"]}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Missing or invalid required field: name (must be a non-empty string)"


def test_missing_preferred_slots():
    """Should return 400 if a participant is missing the preferredSlots field"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": "Alice"}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Participant 'Alice' has a missing or invalid required field: preferredSlots (must be a non-empty list)"


def test_empty_preferred_slots():
    """Should return 400 if a participant has empty preferredSlots"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": "Alice", "preferredSlots": []}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Participant 'Alice' has a missing or invalid required field: preferredSlots (must be a non-empty list)"


def test_nonlist_preferred_slots():
    """Should return 400 if a participant has non-list preferredSlots"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": "Alice", "preferredSlots": "2024-06-10T09:00"}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Participant 'Alice' has a missing or invalid required field: preferredSlots (must be a non-empty list)"


def test_nonstring_preferred_slot():
    """Should return 400 if a participant has a non-string preferred slot"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": "Alice", "preferredSlots": [202406100900]}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Preferred slot '202406100900' for participant 'Alice' must be a string in format YYYY-MM-DDTHH:MM"


def test_invalid_preferred_slot_format():
    """Should return 400 if a participant has a preferred slot in invalid format"""

    event = {
        "body": json.dumps({
            "meetingName": "Design Sync",
            "participants": [
                {"name": "Alice", "preferredSlots": ["06-10-2024 09:00"]}
            ]
        })
    }

    response = lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 400
    assert body["error"] == "Preferred slot '06-10-2024 09:00' for participant 'Alice' must be a string in format YYYY-MM-DDTHH:MM"
