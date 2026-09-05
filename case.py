CHARACTERS = ["Raven", "Zephyr", "Luca", "Marinette", "Adrien"]
MOLE = "Zephyr"
ROOMS = ["Laboratory", "Storage", "Cafeteria"]
LAB_NUMBER = 4
STORAGE_ANSWER = "BREEZE"
STORAGE_NUMBER = len(STORAGE_ANSWER)
CORRECT_PIN = f"{LAB_NUMBER}{STORAGE_NUMBER}19"
QUESTION_BANK = {"alibi": "Where were you at 11:50 PM?"}

CASE_INTRO = """12:18 AM.\n\nThe research facility should have been asleep. Instead, the emergency lights are flashing, a laboratory alarm is screaming through the corridors, and six experimental filter cartridges have disappeared from Storage.\n\nA centrifuge stopped unexpectedly. A vial was found broken. And three minutes of corridor camera footage are missing.\n\nFive employees were still inside the facility. Someone is lying.\n\nYour job is to find out whose lie matters."""

BACKGROUND = {
    "THE CASE": [
        ("12:10 AM", "The emergency alarm sounded after the Laboratory centrifuge stopped unexpectedly."),
        ("12:14 AM", "Six filter cartridges were found missing from Storage."),
        ("12:18 AM", "Three minutes of corridor camera footage were missing."),
    ],
    "THE TIMELINE": [
        ("11:49 PM", "Corridor cameras went offline."),
        ("11:50 PM", "The Cafeteria vending machine began an unscheduled restock."),
        ("11:52 PM", "The Laboratory centrifuge was manually interrupted."),
    ],
    "THE PEOPLE": [
        ("RAVEN", "Head Chemist — responsible for the Laboratory."),
        ("ZEPHYR", "Supply Coordinator — responsible for Storage and supplies."),
        ("LUCA", "Security Officer — responsible for cameras and patrols."),
        ("MARINETTE", "Medic — responsible for the Medical Bay."),
        ("ADRIEN", "Engineer — responsible for facility power systems."),
    ],
    "ONE IMPORTANT DETAIL": [
        ("VENT", "The Storage ventilation override can only be used by Supply and Maintenance. Maintenance is out right now."),
    ],
}

PROFILES = {
    "Raven": {"role": "Head Chemist", "location": "Laboratory", "description": "Brilliant, impatient and visibly annoyed that anyone would question her work.", "personality": "Defensive but confident."},
    "Zephyr": {"role": "Supply Coordinator", "location": "Storage", "description": "Quiet, organized and almost painfully calm. He knows where everything in the facility is kept.", "personality": "Helpful, controlled and evasive."},
    "Luca": {"role": "Security Officer", "location": "Corridor Patrol", "description": "Takes security seriously, but is clearly embarrassed that the camera outage happened on his watch.", "personality": "Professional and guarded."},
    "Marinette": {"role": "Medic", "location": "Medical Bay", "description": "Friendly and observant. She notices more than she initially admits.", "personality": "Kind but cautious."},
    "Adrien": {"role": "Engineer", "location": "Generator Room", "description": "Usually relaxed, but was dealing with a brief power fluctuation that night.", "personality": "Casual and slightly nervous."},
}

ANSWERS = {
    "Raven": {"alibi": {"answer": "In the Laboratory. I was working with the centrifuge. It stopped a couple of minutes later.", "truth": True}},
    "Zephyr": {"alibi": {
        "answer": "In Storage. I was checking the filter inventory. I didn't think anything was wrong.",
        "truth_answer": "In Storage. I was checking the filter inventory. I didn't think anything was wrong.",
        "lie_answer": "I was in the Cafeteria during the restocking cycle. I never went near Storage.",
        "truth": True,
    }},
    "Luca": {"alibi": {"answer": "Near the west corridor. The cameras had just gone down, so I was checking the security panel.", "truth": True}},
    "Marinette": {"alibi": {"answer": "In the Medical Bay, preparing the emergency kit. I heard the alarm a little later.", "truth": True}},
    "Adrien": {"alibi": {"answer": "In the Generator Room. I was handling a brief power fluctuation.", "truth": True}},
}

LAB_CLUE = {
    "title": "LABORATORY INCIDENT NOTE",
    "lines": [
        "Filter pressure was stable before midnight.",
        "One centrifuge cycle was interrupted manually.",
        "Up and active Raven's workstation.",
        "Recorded interruption at 11:52 PM.",
    ],
    "answer": "FOUR",
    "note": "The first letters spell FOUR. That gives you the first PIN digit: 4.",
}

STORAGE_CLUE = {
    "riddle": [
        "I cannot be seen, but I shake every leaf.",
        "I fill the sails of ships, yet I weigh nothing at all.",
        "I can carry a whisper farther than the person who spoke it.",
        "Sailors welcome me when I am gentle, but fear what I become when I grow wild.",
    ],
    "question": "What am I?",
}

CAFETERIA_CLUE = {
    "title": "RESTOCKING RECEIPT",
    "job": "ZEPHYR — SUPPLY",
    "pin_fragment": "??19",
    "note": "The final two PIN digits are 19. Combine them with 4 and the six-letter Storage answer.",
}

WORDLE_ANSWER = "VENTS"
