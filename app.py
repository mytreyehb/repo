import streamlit as st
import string
import os
import random

from game_logic import (
    new_multiplayer_game,
    process_turn,
    new_single_game,
    process_single_turn,
    load_words
)

st.set_page_config(page_title="Hangman", layout="centered")

# ---------- IMAGE SETUP ----------
BASE = os.path.dirname(__file__)
MAX_IMAGES = 10

def show_image(stage=None, state=None):
    if state == "win":
        filename = "win.jpg"
    elif state == "lose":
        filename = "lose.jpg"
    else:
        filename = f"{stage}.jpg"

    path = os.path.join(BASE, "assets", filename)

    if os.path.exists(path):
        st.image(path, use_container_width=True)

# ---------- SETTINGS ----------
st.sidebar.title("⚙️ Settings")
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
mode = st.sidebar.selectbox("Mode", ["Single Player", "Multiplayer"])

# Reset game if mode changes
if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode

if st.session_state.last_mode != mode:
    if "game" in st.session_state:
        del st.session_state.game
    if "players" in st.session_state:
        del st.session_state.players
    if "setter" in st.session_state:
        del st.session_state.setter
    if "word_mode" in st.session_state:
        del st.session_state.word_mode

    st.session_state.last_mode = mode
    st.rerun()

# =========================================================
# 🧍 SINGLE PLAYER MODE
# =========================================================
if mode == "Single Player":

    if "game" not in st.session_state:
        st.session_state.game = new_single_game(difficulty)

    game = st.session_state.game

    st.title("🎯 Hangman (Single Player)")
    st.markdown("### 🎯 Your Turn")

    display = [c if c in game["guesses"] else "_" for c in game["word"]]

    progress = game["wrong"] / game["max_turns"]
    stage = min(int(progress * MAX_IMAGES), MAX_IMAGES)
    remaining = game["max_turns"] - game["wrong"]

    left, right = st.columns([3, 1])

    with left:
        st.markdown("## " + " ".join(display))
        st.progress(progress)
        st.write("❤️" * remaining + "🖤" * game["wrong"])

    with right:
        show_image(stage, game["status"])

    cols = st.columns(9)
    for i, l in enumerate(string.ascii_uppercase):
        with cols[i % 9]:
            if st.button(
                l,
                key=f"single_{l}",
                disabled=(l in game["guesses"] or game["status"] != "playing"),
                use_container_width=True
            ):
                st.session_state.game = process_single_turn(game, l)
                st.rerun()

    st.markdown("### 🏆 Score")
    st.write(game["score"])

    if game["status"] == "win":
        st.success("🎉 You won!")
        st.balloons()

    elif game["status"] == "lose":
        st.error(f"💀 Game Over! Word: {game['word']}")

    if game["status"] != "playing":
        if st.button("🔄 Play Again"):
            del st.session_state.game
            st.rerun()

# =========================================================
# 👥 MULTIPLAYER MODE
# =========================================================
else:

    # ---------- PLAYER SETUP ----------
    if "players" not in st.session_state:

        st.title("👥 Multiplayer Setup")

        num_players = st.number_input("Number of players", 2, 6, 2)

        players = []
        for i in range(num_players):
            name = st.text_input(f"Player {i+1} Name", key=f"p{i}")
            if name:
                players.append(name)

        if st.button("Next") and len(players) == num_players:
            st.session_state.players = players
            st.rerun()

        st.stop()

    # ---------- CHOOSE MODE ----------
    if "word_mode" not in st.session_state:

        st.title("🎮 Choose Game Type")

        word_mode = st.radio(
            "Select word source:",
            ["Player enters word", "Random word"]
        )

        if st.button("Continue"):
            st.session_state.word_mode = word_mode
            st.rerun()

        st.stop()

    # ---------- WORD SETUP ----------
    if "game" not in st.session_state:

        # 🎲 RANDOM WORD MODE
        if st.session_state.word_mode == "Random word":

            words = load_words()
            word = random.choice(words)

            st.session_state.game = new_multiplayer_game(
                word,
                difficulty,
                st.session_state.players,
                setter="System"
            )
            st.rerun()

        # 👤 PLAYER ENTERS WORD
        else:

            if "setter" not in st.session_state:

                st.title("🎭 Choose Word Setter")

                setter = st.selectbox("Who will set the word?", st.session_state.players)

                if st.button("Continue"):
                    st.session_state.setter = setter
                    st.rerun()

                st.stop()

            st.title("🔒 Enter Secret Word")
            st.write(f"{st.session_state.setter}, enter the word")

            word = st.text_input("Word", type="password")

            if st.button("Start Game") and word:
                st.session_state.game = new_multiplayer_game(
                    word.upper(),
                    difficulty,
                    st.session_state.players,
                    st.session_state.setter
                )
                st.rerun()

            st.stop()

    # ---------- GAME ----------
    game = st.session_state.game
    players = game.get("players", [])

    # Handle "System" setter
    if game["setter"] == "System":
        current_player = game["players"][game["turn"] % len(game["players"])]
        st.caption("🎲 Random word mode")
    else:
        current_player = game["guessers"][game["turn"]]
        st.caption(f"Word set by {game['setter']} (not playing)")

    st.title("🎯 Hangman (Multiplayer)")
    st.markdown(f"### 🎯 Turn: **{current_player}**")

    display = [c if c in game["guesses"] else "_" for c in game["word"]]

    progress = game["wrong"] / game["max_turns"]
    stage = min(int(progress * MAX_IMAGES), MAX_IMAGES)
    remaining = game["max_turns"] - game["wrong"]

    left, right = st.columns([3, 1])

    with left:
        st.markdown("## " + " ".join(display))
        st.progress(progress)
        st.write("❤️" * remaining + "🖤" * game["wrong"])

    with right:
        show_image(stage, game["status"])

    cols = st.columns(9)
    for i, l in enumerate(string.ascii_uppercase):
        with cols[i % 9]:
            if st.button(
                l,
                key=f"multi_{l}",
                disabled=(l in game["guesses"] or game["status"] != "playing"),
                use_container_width=True
            ):
                st.session_state.game = process_turn(game, l)
                st.rerun()

    st.markdown("### 🏆 Scores")
    for p in players:
        role = " (Setter)" if p == game["setter"] else ""
        st.write(f"{p}{role}: {game['scores'][p]}")

    if game["status"] == "win":
        st.success(f"🎉 {game['winner']} guessed the word!")
        st.balloons()

    elif game["status"] == "lose":
        st.error(f"💀 No one guessed it. Word: {game['word']}")

    if game["status"] != "playing":
        if st.button("🔄 Next Round"):
            del st.session_state.game
            if "setter" in st.session_state:
                del st.session_state.setter
            if "word_mode" in st.session_state:
                del st.session_state.word_mode
            st.rerun()