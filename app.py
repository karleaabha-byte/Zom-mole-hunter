from __future__ import annotations

import secrets
import threading
from pathlib import Path

from flask import Flask, jsonify, make_response, request

from case import (
    BACKGROUND,
    CASE_INTRO,
    CHARACTERS,
    PROFILES,
    QUESTION_BANK,
    ROOMS,
    STORAGE_CLUE,
)
from game import GameState

ROOT = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=None)

_sessions: dict[str, GameState] = {}
_sessions_lock = threading.Lock()


def snapshot(state: GameState) -> dict:
    data = state.get_stats()
    data.update(
        {
            "visited_rooms": list(state.visited_rooms),
            "asked": list(state.asked),
            "log": list(state.log),
            "clues": sorted(state.evidence.clues_found),
            "evidence_notes": list(state.evidence.notes),
            "storage_riddle_solved": state.storage_riddle_solved,
            "security_challenge_active": state.security_challenge_active,
            "security_challenge_complete": state.security_challenge_complete,
            "wordle_attempts": list(state.wordle_attempts),
            "wordle_results": list(state.wordle_results),
            "statements": dict(state.evidence.suspect_statements),
            "notes": list(state.evidence.notes),
            "game_over": state.game_over,
        }
    )
    return data


def get_session() -> tuple[str, GameState]:
    sid = request.cookies.get("sid")

    with _sessions_lock:
        if not sid or sid not in _sessions:
            sid = secrets.token_urlsafe(18)

            state = GameState()

            # First game in this browser session:
            # NO Storage evidence.
            state.demo_run_number = 1
            state.storage_roll = False

            _sessions[sid] = state

        return sid, _sessions[sid]


def json_response(payload: dict, sid: str, status: int = 200):
    response = make_response(jsonify(payload), status)

    response.set_cookie(
        "sid",
        sid,
        max_age=60 * 60 * 24 * 30,
        samesite="Lax",
    )

    response.headers["Cache-Control"] = "no-store"

    return response


@app.get("/")
def index():
    response = make_response(
        (ROOT / "index.html").read_text(encoding="utf-8")
    )

    response.headers["Content-Type"] = "text/html; charset=utf-8"
    response.headers["Cache-Control"] = "no-store"

    return response


@app.get("/frontend.js")
def frontend():
    response = make_response(
        (ROOT / "frontend.js").read_text(encoding="utf-8")
    )

    response.headers["Content-Type"] = "application/javascript"
    response.headers["Cache-Control"] = "no-store"

    return response


@app.get("/api/state")
def state_api():
    sid, state = get_session()
    return json_response(snapshot(state), sid)


@app.get("/api/case")
def case_api():
    sid, _ = get_session()

    return json_response(
        {
            "intro": CASE_INTRO,
            "background": BACKGROUND,
            "characters": CHARACTERS,
            "profiles": PROFILES,
            "question": QUESTION_BANK["alibi"],
            "rooms": ROOMS,
            "storage_riddle": STORAGE_CLUE["riddle"],
        },
        sid,
    )


@app.post("/api/new")
def new_game():
    sid, old_state = get_session()

    with _sessions_lock:
        previous_run = getattr(
            old_state,
            "demo_run_number",
            1,
        )

        next_run = previous_run + 1

        state = GameState()

        state.demo_run_number = next_run

        # Alternate Storage outcome:
        # Game 1 -> NOT_FOUND
        # Game 2 -> FOUND
        # Game 3 -> NOT_FOUND
        # Game 4 -> FOUND
        state.storage_roll = (next_run % 2 == 0)

        _sessions[sid] = state

    return json_response(
        {
            "ok": True,
            "state": snapshot(state),
        },
        sid,
    )


@app.post("/api/<action>")
def game_action(action: str):
    sid, state = get_session()
    payload = request.get_json(silent=True) or {}

    try:
        if action == "room":
            ok, result = state.visit_room(
                str(payload.get("room", ""))
            )

        elif action == "storage":
            ok, result = state.solve_storage_riddle(
                str(payload.get("answer", ""))
            )

        elif action == "pin":
            ok, result = state.attempt_pin(
                str(payload.get("guess", ""))
            )

        elif action == "wordle":
            ok, result = state.submit_wordle(
                str(payload.get("guess", ""))
            )

        elif action == "question":
            ok, result = state.ask_question(
                str(payload.get("character", ""))
            )

        elif action == "accuse":
            ok, result = state.make_accusation(
                str(payload.get("character", "")),
                str(payload.get("reasoning", "")),
            )

        else:
            return json_response(
                {
                    "ok": False,
                    "result": "Unknown endpoint",
                },
                sid,
                404,
            )

    except Exception as error:
        return json_response(
            {
                "ok": False,
                "result": f"Server error: {error}",
            },
            sid,
            500,
        )

    return json_response(
        {
            "ok": ok,
            "result": result,
            "state": snapshot(state),
        },
        sid,
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True,
    )

