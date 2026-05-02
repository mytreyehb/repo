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

# ---------- MOBILE / DESKTOP TOGGLE ----------
screen_mode = st.sidebar.radio("View Mode", ["Auto", "Mobile", "Desktop"])

if screen_mode == "Mobile":
    is_mobile = True
elif screen_mode == "Desktop":
    is_mobile = False
else:
    is_mobile = False  # fallback

# ---------- BUTTON STYLE ----------
st.markdown("""
<style>
button {
    height: 3rem !important;
    font-size: 18px !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

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

# ---------- RESET ON MODE CHANGE ----------
if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode

if st.session_state.last_mode != mode:
    for key in ["game", "players", "setter", "word_mode"]:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.last_mode = mode
    st.rerun()

# =========================================================
# 🧍 SINGLE PLAYER
# =========================================================
if mode == "Single Player":

    if "game" not in st.session_state:
        st.session_state.game = new_single_game(difficulty)

    game = st.session_state.game

    st.title("🎯 Hangman")
    st.markdown("### 🎯 Your Turn")

    display = [c if c in game["guesses"] else "_" for c in game["word"]]

    progress = game["wrong"] / game["max_turns"]
    stage = min(int(progress * MAX_IMAGES), MAX_IMAGES)
    remaining = game["max_turns"] - game["wrong"]

    # ---------- RESPONSIVE LAYOUT ----------
    if is_mobile:
        show_image(stage, game["status"])

        st.markdown(
            f"<div style='text-align:center; font-size:28px; letter-spacing:6px;'>"
            f"{' '.join(display)}</div>",
            unsafe_allow_html=True
        )

        st.progress(progress)
        st.write("❤️" * remaining + "🖤" * game["wrong"])

    else:
        left, right = st.columns([3, 1])

        with left:
            st.markdown("## " + " ".join(display))
            st.progress(progress)
            st.write("❤️" * remaining + "🖤" * game["wrong"])

        with right:
            show_image(stage, game["status"])

    # ---------- LETTERS ----------
    cols_per_row = 6 if is_mobile else 9
    cols = st.columns(cols_per_row)

    for i, l in enumerate(string.ascii_uppercase):
        with cols[i % cols_per_row]:
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
# 👥 MULTIPLAYER
# =========================================================
else:

    if "players" not in st.session_state:
        st.title("👥 Multiplayer Setup")

        num_players = st.number_input("Number of players", 2, 6, 2)

        players = []
        for i in range(num_players):
            name = st.text_input(f"Player {i+1}", key=f"p{i}")
            if name:
                players.append(name)

        if st.button("Next") and len(players) == num_players:
            st.session_state.players = players
            st.rerun()

        st.stop()

    if "word_mode" not in st.session_state:
        st.title("🎮 Game Type")

        mode_choice = st.radio(
            "Word source:",
            ["Player enters word", "Random word"]
        )

        if st.button("Continue"):
            st.session_state.word_mode = mode_choice
            st.rerun()

        st.stop()

    if "game" not in st.session_state:

        if st.session_state.word_mode == "Random word":
            word = random.choice(load_words())

            st.session_state.game = new_multiplayer_game(
                word, difficulty, st.session_state.players, "System"
            )
            st.rerun()

        else:
            if "setter" not in st.session_state:
                st.title("🎭 Choose Setter")

                setter = st.selectbox("Who sets the word?", st.session_state.players)

                if st.button("Continue"):
                    st.session_state.setter = setter
                    st.rerun()

                st.stop()

            st.title("🔒 Enter Word")
            st.write(f"{st.session_state.setter}, enter the word")

            word = st.text_input("Word", type="password")

            if st.button("Start") and word:
                st.session_state.game = new_multiplayer_game(
                    word.upper(),
                    difficulty,
                    st.session_state.players,
                    st.session_state.setter
                )
                st.rerun()

            st.stop()

    game = st.session_state.game
    players = game.get("players", [])

    if game["setter"] == "System":
        current_player = players[game["turn"] % len(players)]
    else:
        current_player = game["guessers"][game["turn"]]

    st.title("🎯 Hangman")
    st.markdown(f"### 🎯 Turn: **{current_player}**")

    display = [c if c in game["guesses"] else "_" for c in game["word"]]

    progress = game["wrong"] / game["max_turns"]
    stage = min(int(progress * MAX_IMAGES), MAX_IMAGES)
    remaining = game["max_turns"] - game["wrong"]

    if is_mobile:
        show_image(stage, game["status"])
        st.markdown("## " + " ".join(display))
        st.progress(progress)
        st.write("❤️" * remaining + "🖤" * game["wrong"])
    else:
        left, right = st.columns([3, 1])

        with left:
            st.markdown("## " + " ".join(display))
            st.progress(progress)
            st.write("❤️" * remaining + "🖤" * game["wrong"])

        with right:
            show_image(stage, game["status"])

    cols_per_row = 6 if is_mobile else 9
    cols = st.columns(cols_per_row)

    for i, l in enumerate(string.ascii_uppercase):
        with cols[i % cols_per_row]:
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
        st.write(f"{p}: {game['scores'][p]}")

    if game["status"] == "win":
        st.success(f"🎉 {game['winner']} wins!")
        st.balloons()
    elif game["status"] == "lose":
        st.error(f"💀 Word: {game['word']}")

    if game["status"] != "playing":
        if st.button("🔄 Next Round"):
            for key in ["game", "setter", "word_mode"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()