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
st.markdown("""
<style>

/* Correct container targeting */
.block-container {
    max-width: 650px;
    padding-top: 2rem;
    padding-left: 1rem;
    padding-right: 1rem;
    margin: auto;
}

/* Mobile override */
@media (max-width: 768px) {
    .block-container {
        max-width: 100%;
        padding-left: 10px;
        padding-right: 10px;
    }
}

</style>
""", unsafe_allow_html=True)
# ---------- VIEW MODE ----------
screen_mode = st.sidebar.radio("View Mode", ["Mobile", "Desktop"])
is_mobile = (screen_mode == "Mobile")

# ---------- BUTTON STYLE ----------
st.markdown("""
<style>
button {
    height: 60px !important;
    font-size: 20px !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- IMAGE ----------
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
        st.markdown(f"""
        <div style="margin-top:-40px;">
        """, unsafe_allow_html=True)

        if is_mobile:
            st.image(path, use_container_width=True)
        else:
            st.image(path, width=220)

        st.markdown("</div>", unsafe_allow_html=True)

# ---------- KEYBOARD ----------
def draw_keyboard(letters, guessed, disabled, key_prefix, cols_per_row):
    for i in range(0, len(letters), cols_per_row):
        row = st.columns(cols_per_row)
        for j, l in enumerate(letters[i:i+cols_per_row]):
            with row[j]:
                if st.button(
                    l,
                    key=f"{key_prefix}_{l}",
                    disabled=(l in guessed or disabled),
                    use_container_width=True
                ):
                    return l
    return None

# ---------- SETTINGS ----------
st.sidebar.title("⚙️ Settings")
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
mode = st.sidebar.selectbox("Mode", ["Single Player", "Multiplayer"])

# ---------- RESET ----------
if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode

if st.session_state.last_mode != mode:
    for key in ["game", "players", "setter", "word_mode"]:
        st.session_state.pop(key, None)

    st.session_state.last_mode = mode
    st.rerun()

# =========================================================
# 🧍 SINGLE PLAYER
# =========================================================
if mode == "Single Player":

    if "game" not in st.session_state:
        st.session_state.game = new_single_game(difficulty)

    game = st.session_state.game

    display = [c if c in game["guesses"] else "_" for c in game["word"]]

    progress = game["wrong"] / game["max_turns"]
    stage = min(int(progress * MAX_IMAGES), MAX_IMAGES)
    remaining = game["max_turns"] - game["wrong"]

    st.title("🎯 Hangman")

    # ---------- MOBILE ----------
    if is_mobile:
        show_image(stage, game["status"])

        st.markdown(
            f"<div style='text-align:center; font-size:32px; letter-spacing:8px;'>"
            f"{' '.join(display)}</div>",
            unsafe_allow_html=True
        )

        st.progress(progress)

        st.markdown(
            f"<div style='text-align:center; font-size:20px;'>"
            f"{'❤️'*remaining} {'🖤'*game['wrong']}</div>",
            unsafe_allow_html=True
        )

    # ---------- DESKTOP ----------
    else:
        left, right = st.columns([3, 1])

        with left:
            st.markdown(
                "<div style='text-align:center; font-size:26px;'>"
                + " ".join(display) +
                "</div>",
                unsafe_allow_html=True
            )
            st.progress(progress)
            st.write("❤️" * remaining + "🖤" * game["wrong"])

        with right:
            show_image(stage, game["status"])

    # ---------- KEYBOARD ----------
    clicked = draw_keyboard(
        string.ascii_uppercase,
        game["guesses"],
        game["status"] != "playing",
        "single",
        cols_per_row=5 if is_mobile else 7
    )

    if clicked:
        st.session_state.game = process_single_turn(game, clicked)
        st.rerun()

    st.markdown("### 🏆 Score")
    st.write(game["score"])

    if game["status"] == "win":
        st.success("🎉 You won!")
        st.balloons()
    elif game["status"] == "lose":
        st.error(f"💀 Word: {game['word']}")

    if game["status"] != "playing":
        if st.button("🔄 Play Again"):
            st.session_state.pop("game", None)
            st.rerun()

# =========================================================
# 👥 MULTIPLAYER
# =========================================================
else:

    if "players" not in st.session_state:
        st.title("👥 Setup")

        num_players = st.number_input("Players", 2, 6, 2)

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

        choice = st.radio("Word source", ["Player enters word", "Random word"])

        if st.button("Continue"):
            st.session_state.word_mode = choice
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
                setter = st.selectbox("Setter", st.session_state.players)

                if st.button("Continue"):
                    st.session_state.setter = setter
                    st.rerun()

                st.stop()

            word = st.text_input("Secret word", type="password")

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
    st.markdown(f"### 🎯 Turn: {current_player}")

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

    clicked = draw_keyboard(
        string.ascii_uppercase,
        game["guesses"],
        game["status"] != "playing",
        "multi",
        cols_per_row=4 if is_mobile else 6
    )

    if clicked:
        st.session_state.game = process_turn(game, clicked)
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
                st.session_state.pop(key, None)
            st.rerun()