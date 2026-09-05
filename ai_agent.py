def _utility(self, state, action):
    storage, cafe, security, wordle_failed, contrad = self._state_features(state)

    # Shared environmental context — identical across candidate actions,
    # so it never changes WHICH action wins, only the raw magnitude.
    context = 0
    context += 20 if not storage else -35
    context += -5 if cafe else 0
    if storage and cafe:
        context -= 30
    if security:
        context += 20
    if contrad:
        context -= 30
    if getattr(state, "pin_cracked", False) and not getattr(state, "security_challenge_complete", False):
        context += 15

    if action == "activate_security":
        benefit = 60 if storage else 0
        cost = 12 + (0 if storage else 20)
        return context + benefit - cost

    elif action == "skip_security":
        benefit = 12
        cost = 20
        return context + benefit - cost

    elif action == "truth":
        benefit = 8                      # protects credibility
        cost = 5                         # gives information away
        if storage:
            cost += 15                    # riskier to be caught out
        if storage and cafe:
            cost += 30                    # even riskier with full evidence
        if wordle_failed:
            cost += 10                    # NEW: less to lose by lying now, so truth is relatively less attractive
        return context + benefit - cost

    elif action == "lie":
        benefit = 15                     # hides information
        cost = 18 + 8                    # contradiction / credibility risk
        if storage:
            cost += 15
        if storage and cafe:
            benefit += 45                 # strong incentive with full evidence
        elif not storage:
            benefit += 8
        if wordle_failed:
            benefit += 20                 # NEW: missed vent/supplies clue makes lying safer
        return context + benefit - cost

    return context
