import streamlit as st
import random
import time
import matplotlib.pyplot as plt
import io

# --- The self-contained GIF for the 'spinning' phase ---
WHEEL_GIF_BASE64 = "R0lGODlhfQJ9APcAAAD/AACa/wCaAAAAzP8AzACZ/wCZAMz/AMwAMwD/MwAAmQAzmQAzzDMA/zMAAJkzmZkzzJkAM5kzAJkzAACZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH/C05FVFNDQVBFMi4wAwEAAAAh+QQFAAD/ACwAAAAAfQJ9AAAI/wD/CRxIsKDBgwgTKlzIsKHDhxAjSpxIsaLFixgzatzIsaPHjyBDihxJsqTJkyhTqlzJsqXLlzBjypxJs6bNmzhz6tzJs6fPn0CDCh1KtKjRo0iTKl3KtKnTp1CjSp1KtarVq1izat3KtavXr2DDih1LtqzZs2jTql3Ltq3bt3Djyp1Lt67du3jz6t3Lt6/fv4ADCx5MuLDhw4gTK17MuLHjx5AjS55MubLly5gza97MubPnz6BDix5NurTpxgAAOw=="

# --- Function to draw the pie chart wheel ---
def create_wheel(options, rotation_angle=0):
    """
    Creates a Matplotlib pie chart with visible labels and a specific rotation.
    """
    plt.figure(figsize=(8, 8))
    # Make slices equal
    sizes = [1] * len(options)
    
    # Use a set of high-contrast default colors from Matplotlib
    colors = plt.cm.get_cmap('tab20').colors[:len(options)]

    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Draw the pie chart with specified rotation and text properties
    ax.pie(sizes, labels=options, colors=colors,
           startangle=90 + rotation_angle,  # This rotates the wheel
           counterclock=False,
           wedgeprops={'edgecolor': 'white', 'linewidth': 2},
           textprops={'fontsize': 14, 'weight': 'bold'}) # Ensure labels are visible
    
    ax.set_aspect('equal')
    
    # Draw a static pointer at the top
    ax.arrow(0, 1.1, 0, -0.3, head_width=0.1, head_length=0.1, fc='black', ec='black', lw=2)
    
    # Save the plot to a memory buffer to display in Streamlit
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    buf.seek(0)
    plt.close(fig)
    return buf

# --- SESSION STATE & ADMIN CHECK ---
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = st.query_params.get("mode") == "admin"
if 'options' not in st.session_state:
    st.session_state.options = ["Pizza", "Burger", "Tacos", "Salad", "Sushi", "Pasta"]

# --- UI ELEMENTS ---
st.title("🎡 Spin Wheel")

with st.sidebar:
    st.header("⚙️ Controls")
    options_text = st.text_area("Options (one per line)", value="\n".join(st.session_state.options), height=250)
    
    if st.button("Update Options"):
        st.session_state.options = [opt.strip() for opt in options_text.split("\n") if opt.strip()]
        st.rerun()

    st.markdown("---")
    fast_spin = st.toggle("Fast Spin", help="Skip the spin animation for an instant result.")
    
    rigged_winner_index = None
    if st.session_state.is_admin and fast_spin:
        st.info("🤫 Admin Controls Enabled")
        rigged_winner_index = st.number_input(
            "Winner Number (1, 2, 3...)", min_value=1,
            max_value=len(st.session_state.options) if st.session_state.options else 1,
            step=1, value=None
        )

# --- MAIN PAGE LOGIC ---
placeholder = st.empty()

if st.button("SPIN!", type="primary", use_container_width=True):
    # 1. Determine the winner
    if rigged_winner_index is not None:
        winner = st.session_state.options[rigged_winner_index - 1]
    else:
        winner = random.choice(st.session_state.options)

    # 2. Handle Fast Spin or Full Spin
    if fast_spin:
        placeholder.success(f"## Winner: **{winner}**")
        st.balloons()
    else:
        # Step A: Show the spinning placeholder
        placeholder.markdown(
            f'<div style="text-align: center;"><img src="data:image/gif;base64,{WHEEL_GIF_BASE64}" alt="Spinning..."></div>',
            unsafe_allow_html=True,
        )
        time.sleep(3) # Wait for the animation to "play"

        # Step B: Calculate the final rotation to place the winner at the top
        winner_index = st.session_state.options.index(winner)
        slice_angle = 360 / len(st.session_state.options)
        final_rotation = - (winner_index * slice_angle + slice_angle / 2)
        
        # Step C: Draw the final wheel rotated to the winner
        final_wheel_img = create_wheel(st.session_state.options, rotation_angle=final_rotation)
        
        # FIX: Changed use_column_width to use_container_width
        placeholder.image(final_wheel_img, use_container_width=True)
        st.success(f"## Winner: **{winner}**")
        st.balloons()
else:
    # Show the initial static wheel before the first spin
    if st.session_state.options:
        initial_wheel_img = create_wheel(st.session_state.options)
        # FIX: Changed use_column_width to use_container_width
        placeholder.image(initial_wheel_img, use_container_width=True)
    else:
        placeholder.warning("Please add some options in the sidebar.")
