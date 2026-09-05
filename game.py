import random
from ai_agent import MoleAI
from evidence import EvidenceBoard
import case

ROOMS = list(case.ROOMS)
WORDLE_ANSWER = case.WORDLE_ANSWER
WORDLE_MAX_ATTEMPTS = 6


class GameState:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.mole_ai = MoleAI(seed)
        self.evidence = EvidenceBoard()

        self.actions_used = 0
        self.visited_rooms = {}
        self.room_decisions = {}
        self.asked = {}
        self.log = []
        self.game_over = False
        self.result = None
        self.accused = None
        self.contradiction_flagged = False

        self.pin_cracked = False
        self.pin_attempts = 0

        self.security_challenge_active = False
        self.security_challenge_complete = False
        self.wordle_answer = WORDLE_ANSWER
        self.wordle_attempts = []
        self.wordle_failed = False
        self.wordle_results = []

        self.storage_riddle_solved = False
        self.storage_evidence_found = False
        # The Storage search is the game's only randomized event.
        self.storage_roll = self.rng.random() < 0.5
        self.cafeteria_evidence_found = False

    def can_act(self):
        return not self.game_over

    def _log(self, text):
        self.log.append(text)

    def visit_room(self, room):
        if not self.can_act():
            return False, "The case is already closed."
        if room in self.visited_rooms:
            return False, f"You've already investigated the {room}."
        if room not in ROOMS:
            return False, "Unknown room."

        if room == "Laboratory":
            clue = case.LAB_CLUE
            self.evidence.add_clue("lab_acrostic")
            self.room_decisions[room] = "neutral"
        elif room == "Storage":
            clue = case.STORAGE_CLUE
            self.room_decisions[room] = "awaiting_riddle"
        else:
            clue = case.CAFETERIA_CLUE
            self.cafeteria_evidence_found = True
            self.evidence.add_clue("cafeteria_pin")
            self.room_decisions[room] = "neutral"

        self.visited_rooms[room] = clue
        self.actions_used += 1
        self._log(f"Investigated the {room}.")
        return True, clue

    def solve_storage_riddle(self, answer):
        if "Storage" not in self.visited_rooms:
            return False, "Investigate Storage first."
        if self.storage_riddle_solved:
            return True, "FOUND" if self.storage_evidence_found else "NOT_FOUND"

        if str(answer).strip().upper() != case.STORAGE_ANSWER:
            self.actions_used += 1
            self._log("Incorrect Storage riddle answer.")
            return False, "Incorrect answer. Try again."

        self.storage_riddle_solved = True
        self.actions_used += 1
        self.storage_evidence_found = self.storage_roll
        if self.storage_evidence_found:
            self.evidence.add_clue("storage_ventilation")
            self.room_decisions["Storage"] = "evidence_found"
            self._log("Ventilation override found in Storage.")
            return True, "FOUND"

        self.room_decisions["Storage"] = "evidence_not_found"
        return True, "NOT_FOUND"

    def attempt_pin(self, guess):
        if self.pin_cracked:
            return True, "ALREADY_CRACKED"
        if not self.can_act():
            return False, "The case is already closed."

        self.actions_used += 1
        self.pin_attempts += 1
        digits = "".join(ch for ch in str(guess) if ch.isdigit())
        if digits != case.CORRECT_PIN:
            self._log(f"Incorrect PIN attempt #{self.pin_attempts}.")
            return False, "Incorrect PIN."

        self.pin_cracked = True
        self.evidence.set_pin_cracked()
        self._log("PIN cracked. Restricted employee access unlocked.")

        self.security_challenge_active = self.mole_ai.decide_security_sabotage(self)
        self.security_challenge_complete = not self.security_challenge_active
        if self.security_challenge_active:
            self._log("Zephyr deployed the secondary security verification.")
        else:
            self._log("Interrogation system unlocked.")
        return True, "CORRECT"

    def submit_wordle(self, guess):
        if not self.security_challenge_active:
            return False, "No security challenge is active."
        guess = str(guess).strip().upper()
        if len(guess) != 5 or not guess.isalpha():
            return False, "Enter a 5-letter word."
        if len(self.wordle_attempts) >= WORDLE_MAX_ATTEMPTS:
            self.security_challenge_active = False
            self.wordle_failed = True
            return False, "ATTEMPTS_EXHAUSTED"

        self.wordle_attempts.append(guess)
        answer = self.wordle_answer
        result = ["black"] * 5
        remaining = {}
        for ch in answer:
            remaining[ch] = remaining.get(ch, 0) + 1
        for i, ch in enumerate(guess):
            if ch == answer[i]:
                result[i] = "green"
                remaining[ch] -= 1
        for i, ch in enumerate(guess):
            if result[i] == "green":
                continue
            if remaining.get(ch, 0) > 0:
                result[i] = "yellow"
                remaining[ch] -= 1

        self.wordle_results.append({"guess": guess, "result": list(result)})

        if guess == answer:
            self.security_challenge_complete = True
            self.security_challenge_active = False
            self._log("Secondary security lock defeated.")
            return True, {"status": "CORRECT", "result": result, "attempts_remaining": WORDLE_MAX_ATTEMPTS - len(self.wordle_attempts)}

        if len(self.wordle_attempts) >= WORDLE_MAX_ATTEMPTS:
            self.security_challenge_active = False
            self.wordle_failed = True
            self._log("Security challenge failed; interrogation access remains blocked.")
            return False, {"status": "FAILED", "result": result, "attempts_remaining": 0}

        return True, {"status": "CONTINUE", "result": result, "attempts_remaining": WORDLE_MAX_ATTEMPTS - len(self.wordle_attempts)}

    def ask_question(self, character, question_key="alibi"):
        # Interrogation is intentionally available from the hub without
        # requiring the Cafeteria PIN or the secondary security challenge.
        if not self.can_act():
            return False, "The case is already closed."
        if character in self.asked:
            return False, f"You've already questioned {character}."
        if character not in case.CHARACTERS:
            return False, "Unknown character."

        if character == case.MOLE:
            tell_truth = self.mole_ai.decide_truth_or_lie(self)
            data = case.ANSWERS[character][question_key]
            answer = data.get("truth_answer") if tell_truth else data.get("lie_answer")
            lied = not tell_truth
        else:
            answer = case.ANSWERS[character][question_key]["answer"]
            lied = False

        self.asked[character] = {"question": question_key, "answer": answer, "lied": lied}
        self.evidence.log_answer(character, question_key, answer, not lied)
        self.evidence.add_note(f"{character}: \"{answer}\"")
        self.actions_used += 1
        self._log(f"Questioned {character}.")
        return True, answer

    def make_accusation(self, character, reasoning=""):
        if self.game_over:
            return False, "The case is already closed."
        if character not in case.CHARACTERS:
            return False, "Unknown character."
        self.accused = character
        self.game_over = True
        self.result = "win" if character == case.MOLE else "lose"
        self._log(f"Final accusation: {character}.")
        return True, self.result

    def get_stats(self):
        return {
            "actions_used": self.actions_used,
            "result": self.result,
            "accused": self.accused,
            "pin_cracked": self.pin_cracked,
            "pin_attempts": self.pin_attempts,
            "storage_evidence_found": self.storage_evidence_found,
            "cafeteria_evidence_found": self.cafeteria_evidence_found,
            "security_challenge_complete": self.security_challenge_complete,
            "wordle_failed": self.wordle_failed,
            "wordle_attempts": list(self.wordle_attempts),
            "wordle_results": list(self.wordle_results),
            "mole_ai": self.mole_ai.stats(),
            "statements": self.evidence.suspect_statements,
            "notes": list(self.evidence.notes),
        }
