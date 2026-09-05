"""Hybrid adversarial agent for the mole, Zephyr.

Zephyr combines:
1. Simple Reflex behavior for the initial Storage decision.
2. Utility-based reasoning for security sabotage when Storage evidence exists.
3. Utility-based reasoning for the final truth-or-lie interrogation.

The 50/50 Storage evidence roll is NOT controlled by the agent.
The agent only evaluates strategic choices after that hidden state exists.
"""

import random


class MoleAI:

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.truth_count = 0
        self.lie_count = 0
        self.security_sabotage_count = 0
        self.security_skip_count = 0

    def _state_features(self, state):
        storage = bool(
            getattr(state, "storage_evidence_found", False)
        )
        cafe = bool(
            getattr(state, "cafeteria_evidence_found", False)
        )
        security = bool(
            getattr(state, "security_challenge_active", False)
        )
        wordle_failed = bool(
            getattr(state, "wordle_failed", False)
        )
        contrad = bool(
            getattr(state, "contradiction_flagged", False)
        )

        return storage, cafe, security, wordle_failed, contrad

    def _utility(self, state, action):
        """Higher utility means better for Zephyr.

        Utility is based on the current evidence and security state.
        Player suspicion is not used in the utility calculation.

        NOTE: `state` is always the real, unmutated game_state here.
        The context block below must stay identical across candidate
        actions being compared — it should never be evaluated against
        an action-specific hypothetical copy, or it silently favors
        whichever action happens to flip those same flags.
        """

        storage, cafe, security, wordle_failed, contrad = (
            self._state_features(state)
        )

        score = 0

        # Zephyr benefits when physical evidence is weak.
        score += 20 if not storage else -35
        score += -5 if cafe else 0

        if storage and cafe:
            score -= 30

        # A live security lock delays interrogation.
        if security:
            score += 20

        # A failed Wordle/security challenge affects later decisions.
        if wordle_failed:
            score += 25

        # Contradictions are harmful to Zephyr.
        if contrad:
            score -= 30

        if (
            getattr(state, "pin_cracked", False)
            and not getattr(state, "security_challenge_complete", False)
        ):
            score += 15

        # ---------------------------------------------------------
        # SECURITY DECISION
        # ---------------------------------------------------------

        if action == "activate_security":
            # Hiding behind a security challenge is useful,
            # but activating it has a sabotage cost.
            score += 60 if storage else -20
            score -= 12

        elif action == "skip_security":
            # Skipping avoids obvious tampering,
            # but gives the detective faster access to interrogation.
            score -= 20
            score += 12

        # ---------------------------------------------------------
        # INTERROGATION DECISION
        # ---------------------------------------------------------

        elif action == "truth":
            # Truth protects credibility but gives information away.
            score += 8
            score -= 5

            if storage:
                score -= 15

            if storage and cafe:
                score -= 30

            if wordle_failed:
                score -= 10

        elif action == "lie":
            # Lying hides information but carries contradiction risk.
            score += 15
            score -= 18
            score -= 8

            if storage:
                score -= 15

            if storage and cafe:
                # More evidence = riskier to be caught contradicting,
                # same escalation shape as the `truth` branch above,
                # instead of a benefit spike that flips the outcome
                # in one discontinuous jump.
                score -= 20
            elif not storage:
                score += 8

            if wordle_failed:
                score += 20

        return score

    def decide_security_sabotage(self, game_state):
        """Decide whether to activate the secondary security challenge.

        Simple Reflex:
            If no Storage evidence exists, immediately skip the challenge.

        Utility-Based:
            If Storage evidence exists, evaluate both activating and
            skipping the challenge and choose the action with the
            highest utility.
        """

        # ---------------------------------------------------------
        # SIMPLE REFLEX RULE
        # ---------------------------------------------------------

        if not getattr(game_state, "storage_evidence_found", False):
            self.security_skip_count += 1
            return False

        # ---------------------------------------------------------
        # UTILITY-BASED DECISION
        # ---------------------------------------------------------

        candidates = [
            (self._utility(game_state, action), action)
            for action in ("activate_security", "skip_security")
        ]

        best_score = max(
            score for score, _ in candidates
        )

        best_actions = [
            action
            for score, action in candidates
            if score == best_score
        ]

        action = self.rng.choice(best_actions)

        if action == "activate_security":
            self.security_sabotage_count += 1
        else:
            self.security_skip_count += 1

        return action == "activate_security"

    def decide_truth_or_lie(self, game_state):
        """Use utility to choose between truth and lying."""

        candidates = [
            (self._utility(game_state, action), action)
            for action in ("truth", "lie")
        ]

        best_score = max(
            score for score, _ in candidates
        )

        best_actions = [
            action
            for score, action in candidates
            if score == best_score
        ]

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
