import streamlit as st
import random

st.set_page_config(page_title="🎰 Fun Slot Machine", layout="centered")

# --- Constants ---
EMOJIS = ["🍒", "🍋", "🍉", "🍇", "⭐", "💎", "🥝", "🍍", "🍎", "🍓"]
WEIGHTS =  [5,    5,    4,    4,    3,    2,     2,     2,     1,     1]
SLOT_COUNT = 5

SPIN_COST = 50
REWARDS = {
    2: 50,
    3: 150,
    4: 400,
    5: 1000
}
STARTING_COINS = 1000
JACKPOT_EVERY_X_SPINS = 7

# --- Initialize Session State ---
if 'balance' not in st.session_state:
    st.session_state.balance = STARTING_COINS
if 'slots' not in st.session_state:
    st.session_state.slots = ["❓"] * SLOT_COUNT
if 'message' not in st.session_state:
    st.session_state.message = ""
if 'spin_count' not in st.session_state:
    st.session_state.spin_count = 0

# --- Game Logic ---
def spin_slots():
    if st.session_state.balance < SPIN_COST:
        st.session_state.message = "🚫 Not enough coins! Click Reset to start over."
        return

    st.session_state.balance -= SPIN_COST
    st.session_state.spin_count += 1

    # Force a jackpot every X spins
    if st.session_state.spin_count % JACKPOT_EVERY_X_SPINS == 0:
        emoji = random.choices(EMOJIS, weights=WEIGHTS)[0]
        result = [emoji] * SLOT_COUNT
        match_count = SLOT_COUNT
    else:
        result = random.choices(EMOJIS, weights=WEIGHTS, k=SLOT_COUNT)
        # Count most frequent emoji
        counts = {emoji: result.count(emoji) for emoji in set(result)}
        match_count = max(counts.values())

    st.session_state.slots = result

    # Determine reward
    if match_count >= 2:
        reward = REWARDS.get(match_count, 0)
        st.session_state.balance += reward
        if match_count == SLOT_COUNT:
            st.session_state.message = f"🌟 JACKPOT! All {SLOT_COUNT} match → +{reward} coins!"
        else:
            st.session_state.message = f"🎉 {match_count} match! You won +{reward} coins."
    else:
        st.session_state.message = "😢 No match. Better luck next time!"

def reset_game():
    st.session_state.balance = STARTING_COINS
    st.session_state.slots = ["❓"] * SLOT_COUNT
    st.session_state.message = "🔄 Game reset. Good luck!"
    st.session_state.spin_count = 0

# --- UI ---
st.title("🎰 Fun Slot Machine (5 Slots)")
st.caption("Now with more emojis & harder odds! Still no real money.")

st.markdown(f"### 💰 Coins: `{st.session_state.balance}`")
st.markdown(f"### 🎲 {' | '.join(st.session_state.slots)}")

# --- Buttons ---
col1, col2 = st.columns(2)
col1.button("🎰 Spin!", use_container_width=True, on_click=spin_slots)
col2.button("🔄 Reset", use_container_width=True, on_click=reset_game)

# --- Message ---
if st.session_state.message:
    st.info(st.session_state.message)

st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Just for fun – no real gambling involved.")
