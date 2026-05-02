import random
import os
def load_words():
    path = os.path.join(os.path.dirname(__file__), "words.txt")

    if not os.path.exists(path):
        return ["PYTHON", "STREAMLIT", "HANGMAN"]  # fallback

    with open(path, "r") as f:
        words = [w.strip().upper() for w in f.readlines() if w.strip()]

    return words
WORDS = load_words()
import random
def new_single_game(difficulty):
    extra = {"Easy": 4, "Medium": 2, "Hard": 0}[difficulty]
    word = random.choice(WORDS)

    return {
        "word": word,
        "guesses": [],
        "wrong": 0,
        "max_turns": len(word) + extra,
        "status": "playing",
        "score": 0
    }


def process_single_turn(state, letter):
    if state["status"] != "playing":
        return state

    if letter in state["guesses"]:
        return state

    state["guesses"].append(letter)

    if letter in state["word"]:
        state["score"] += 10

        if all(c in state["guesses"] for c in state["word"]):
            state["status"] = "win"
            state["score"] += 50
    else:
        state["wrong"] += 1

        if state["wrong"] >= state["max_turns"]:
            state["status"] = "lose"

    return state
def new_multiplayer_game(word, difficulty, players, setter):
    extra = {"Easy": 4, "Medium": 2, "Hard": 0}[difficulty]

    guessers = [p for p in players if p != setter]

    return {
        "word": word,
        "guesses": [],
        "wrong": 0,
        "max_turns": len(word) + extra,
        "status": "playing",
        "players": players,
        "guessers": guessers,
        "setter": setter,
        "turn": 0,
        "scores": {p: 0 for p in players}
    }

def process_turn(state, letter):
    if state["status"] != "playing":
        return state

    current_player = state["guessers"][state["turn"]]

    if letter in state["guesses"]:
        return state

    state["guesses"].append(letter)

    if letter in state["word"]:
        state["scores"][current_player] += 10

        if all(c in state["guesses"] for c in state["word"]):
            state["status"] = "win"
            state["winner"] = current_player
            state["scores"][current_player] += 50

    else:
        state["wrong"] += 1
        state["turn"] = (state["turn"] + 1) % len(state["guessers"])

        if state["wrong"] >= state["max_turns"]:
            state["status"] = "lose"

    return state