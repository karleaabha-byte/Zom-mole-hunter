"""Utility-based adversarial agent for the mole, Zephyr.

The 50/50 Storage evidence roll is NOT controlled by the agent.
The agent only evaluates strategic choices after that hidden state exists.
"""
import copy
import random


class MoleAI:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.truth_count = 0
        self.lie_count = 0
        self.security_sabotage_count = 0
        self.security_skip_count = 0

    def _state_features(self, state):
        storage = bool(getattr(state, "storage_evidence_found", False))
        cafe = bool(getattr(state, "cafeteria_evidence_found", False))
        security = bool(getattr(state, "security_challenge_active", False))
        wordle_failed = bool(getattr(state, "wordle_failed", False))
        contrad = bool(getattr(state, "contradiction_flagged", False))
        return storage, cafe, security, wordle_failed, contrad

    def _utility(self, state, action):
        """Higher utility means better for Zephyr.

        This is intentionally based on the evidence/security state rather than
        player suspicion, because suspicion was removed from the game design.
        """
        storage, cafe, security, wordle_failed, contrad = self._state_features(state)
        score = 0

        # Zephyr benefits when physical evidence is weak.
        score += 20 if not storage else -35
        score += -5 if cafe else 0
        if storage and cafe:
            score -= 30

        # A live security lock delays interrogation.
        if security:
            score += 20
        if wordle_failed:
            score += 25
        if contrad:
            score -= 30

        if getattr(state, "pin_cracked", False) and not getattr(state, "security_challenge_complete", False):
            score += 15

        if action == "activate_security":
            # Hiding behind a security challenge is useful, but visibly
            # sabotaging access has a cost.
            score += 60 if storage else -20
            score -= 12
        elif action == "skip_security":
            # Avoiding an obvious tamper is good, but giving the detective
            # immediate interrogation access is bad.
            score -= 20
            score += 12

        elif action == "truth":
            # Truth protects credibility but gives information away.
            score += 8
            score -= 5
            if storage:
                score -= 15
            if storage and cafe:
                score -= 30
        elif action == "lie":
            # Lying hides information, but risks contradiction.
            score += 15
            score -= 18
            score -= 8
            if storage:
                score -= 15
                score += 10
            if storage and cafe:
                score += 45
            elif not storage:
                score += 8

        return score

    def decide_security_sabotage(self, game_state):
        """Use the secondary security challenge only when Storage proof exists."""
        if not getattr(game_state, "storage_evidence_found", False):
            self.security_skip_count += 1
            return False

        candidates = []
        for action in ("activate_security", "skip_security"):
            candidate = copy.deepcopy(game_state)
            if action == "activate_security":
                candidate.security_challenge_active = True
                candidate.security_challenge_complete = False
            else:
                candidate.security_challenge_active = False
                candidate.security_challenge_complete = True
            candidates.append((self._utility(candidate, action), action))

        best_score = max(score for score, _ in candidates)
        best_actions = [action for score, action in candidates if score == best_score]
        action = self.rng.choice(best_actions)

        if action == "activate_security":
            self.security_sabotage_count += 1
        else:
            self.security_skip_count += 1
        return action == "activate_security"

    def decide_truth_or_lie(self, game_state):
        """Simulate both responses and select the higher-utility response."""
        candidates = []
        for action in ("truth", "lie"):
            candidate = copy.deepcopy(game_state)
            candidates.append((self._utility(candidate, action), action))

        best_score = max(score for score, _ in candidates)
        best_actions = [action for score, action in candidates if score == best_score]
        action = self.rng.choice(best_actions)

        if action == "truth":
            self.truth_count += 1
        else:
            self.lie_count += 1
        return action == "truth"

    def stats(self):
        return {
            "truth_count": self.truth_count,
            "lie_count": self.lie_count,
            "security_sabotage_count": self.security_sabotage_count,
            "security_skip_count": self.security_skip_count,
        }
