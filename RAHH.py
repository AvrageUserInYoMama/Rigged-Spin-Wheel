import streamlit as st
import random
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Spin Wheel",
    page_icon="🎡",
    layout="centered"
)

# --- SESSION STATE & ADMIN CHECK ---
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = st.query_params.get("mode") == "admin"
if 'options' not in st.session_state:
    st.session_state.options = ["Pizza", "Burger", "Tacos", "Salad", "Sushi", "Pasta"]
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'fast_spin' not in st.session_state:
    st.session_state.fast_spin = False

# --- UI ELEMENTS ---
st.title("🎡 Spin Wheel")

with st.sidebar:
    st.header("⚙️ Controls")
    options_text = st.text_area("Options (one per line)", value="\n".join(st.session_state.options), height=250)
    
    if st.button("Update Options"):
        st.session_state.options = [opt.strip() for opt in options_text.split("\n") if opt.strip()]
        st.session_state.winner = None # Reset winner when options change
        st.rerun()

    st.markdown("---")
    st.session_state.fast_spin = st.toggle("Fast Spin", help="Skip the spin animation for an instant result.")
    
    rigged_winner_index = None
    if st.session_state.is_admin and st.session_state.fast_spin:
        st.info("🤫 Admin Controls Enabled")
        rigged_winner_index = st.number_input(
            "Winner Number (1, 2, 3...)", min_value=1,
            max_value=len(st.session_state.options) if st.session_state.options else 1,
            step=1, value=None, placeholder="Enter # to force win..."
        )

# --- MAIN PAGE LOGIC ---
placeholder = st.empty() # A container for the wheel or the result

if st.session_state.winner:
    # If a winner has been determined, show it.
    placeholder.success(f"## Winner: **{st.session_state.winner}**")
    st.balloons()
else:
    # Otherwise, show an info message.
    placeholder.info("Click the SPIN! button to start.")

if st.button("SPIN!", type="primary", use_container_width=True):
    # Determine the winner
    if rigged_winner_index is not None:
        st.session_state.winner = st.session_state.options[rigged_winner_index - 1]
    else:
        st.session_state.winner = random.choice(st.session_state.options)

    if st.session_state.fast_spin:
        # If fast spin is on, just rerun to show the winner immediately
        st.rerun()
    else:
        # Show the spinning wheel GIF
        placeholder.image("https://i.gifer.com/origin/d7/d7ac42a5933e38181658421a52108502_w200.gif", use_column_width=True)
        # Wait for 3 seconds while the GIF plays
        time.sleep(3)
        # Rerun the script to show the winner
        st.rerun()
