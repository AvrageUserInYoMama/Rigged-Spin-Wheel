import streamlit as st
import random
import time
import matplotlib.pyplot as plt
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Spin Wheel",
    page_icon="🎡",
    layout="centered"
)

# --- Function to draw the pie chart wheel ---
def create_wheel(options, rotation_angle=0):
    """
    Creates a Matplotlib pie chart with visible labels and a specific rotation.
    """
    plt.figure(figsize=(8, 8))
    sizes = [1] * len(options)
    colors = [f"#{abs(hash(opt)) % 0xFFFFFF:06x}" for opt in options]

    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Draw the pie chart with specified rotation and text properties for visibility
    ax.pie(sizes, labels=options, colors=colors,
           startangle=90 + rotation_angle,
           counterclock=False,
           wedgeprops={'edgecolor': 'white', 'linewidth': 2},
           textprops={'fontsize': 14, 'weight': 'bold'})
    
    ax.set_aspect('equal')
    ax.arrow(0, 1.1, 0, -0.3, head_width=0.1, head_length=0.1, fc='black', ec='black', lw=2)
    
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
        # 3. PERFORM FRAME-BY-FRAME ANIMATION
        winner_index = st.session_state.options.index(winner)
        slice_angle = 360 / len(st.session_state.options)
        target_rotation = - (winner_index * slice_angle + slice_angle / 2)
        total_rotation = 360 * 3 + target_rotation
        num_frames = 60
        
        for i in range(num_frames + 1):
            # Calculate current rotation with an easing effect
            progress = 1 - (1 - (i / num_frames))**3
            current_rotation = progress * total_rotation
            
            # Create and display the current frame of the wheel
            wheel_frame = create_wheel(st.session_state.options, rotation_angle=current_rotation)
            placeholder.image(wheel_frame, use_container_width=True)
            time.sleep(0.02) # A short delay between frames
        
        # 4. SHOW FINAL RESULT
        # Redraw the final wheel perfectly positioned
        final_wheel = create_wheel(st.session_state.options, rotation_angle=target_rotation)
        placeholder.image(final_wheel, use_container_width=True)
        st.success(f"## Winner: **{winner}**")
        st.balloons()
else:
    # Show the initial static wheel before the first spin
    if st.session_state.options:
        initial_wheel_img = create_wheel(st.session_state.options)
        placeholder.image(initial_wheel_img, use_container_width=True)
    else:
        placeholder.warning("Please add some options in the sidebar.")
