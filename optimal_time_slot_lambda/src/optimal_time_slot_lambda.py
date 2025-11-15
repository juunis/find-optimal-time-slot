from datetime import datetime
import json

def lambda_handler(event, context):
    try:
        # Parse body and handle invalid JSON error
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }

    # Validate meetingName exists, is string and is not just whitespace
    meeting_name = body.get("meetingName")
    if not meeting_name or not isinstance(meeting_name, str) or meeting_name.strip() == "":
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing or invalid required field: meetingName (must be a non-empty string)"})
        }

    # Validate participants exists and is a list
    participants = body.get("participants")
    if not participants or not isinstance(participants, list):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing or invalid required field: participants (must be a non-empty list)"})
        }

    # Validate participants fields
    for participant in participants:
        # Validate that name exists, is string and is not just whitespace
        name = participant.get("name")
        if not name or not isinstance(name, str) or name.strip() == "":
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing or invalid required field: name (must be a non-empty string)"})
            }
        # Validate preferredSlots
        # Validate that preferredSlots exists and is a list
        preferred_slots = participant.get("preferredSlots")
        if not preferred_slots or not isinstance(preferred_slots, list):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Participant '{name}' has a missing or invalid required field: preferredSlots (must be a non-empty list)"})
            }
        # Validate that each slot in preferredSlots is string and in correct format "YYYY-MM-DDTHH:MM"
        for slot in preferred_slots:
            try:
                datetime.strptime(slot, "%Y-%m-%dT%H:%M")
            except (ValueError, TypeError):
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": f"Preferred slot '{slot}' for participant '{name}' must be a string in format YYYY-MM-DDTHH:MM"})
                }

    try:
        # Map each slot to the participants who are available
        # {slot: [list of participant names]}
        # e.g. {"2024-06-10T09:00": ["Alice", "Bob"], "2024-06-10T10:00": ["Bob", "Charlie"]}
        slots_and_participants = {}

        for participant in participants:
            name = participant.get("name")
            preferred_slots = participant.get("preferredSlots", [])
            for slot in preferred_slots:
                if slot not in slots_and_participants:
                    slots_and_participants[slot] = []
                slots_and_participants[slot].append(name)

        # Determine the maximum number of participants that can attend
        max_participants = max((len(names) for names in slots_and_participants.values()), default=0)

        # Find all slots with the maximum participants
        optimal_slots = [
            {"slot": slot, "participants": names}
            for slot, names in slots_and_participants.items()
            if len(names) == max_participants and max_participants > 1
        ]

        response_body = {
            "meetingName": meeting_name,
            "optimalSlots": optimal_slots,
            "maxParticipants": max_participants
        }

        # If no slots have more than 1 participant
        if not optimal_slots:
            response_body["message"] = "No overlapping time slots found between participants"

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body)
        }

    except Exception as e:
        # For unexpected errors
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }
