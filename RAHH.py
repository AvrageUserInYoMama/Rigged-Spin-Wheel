import streamlit as st
import random
import time
import matplotlib.pyplot as plt
import numpy as np
import io

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Spin Wheel",
    page_icon="🎡",
    layout="centered"
)

# --- MATPLOTLIB PIE CHART WHEEL ---
def create_wheel(options, winner=None):
    """
    Creates a static Matplotlib pie chart wheel with a pointer.
    """
    plt.figure(figsize=(8, 8))
    # Make slices equal
    sizes = [1] * len(options)
    
    # Generate consistent colors
    # Hashing the option ensures the color is the same every time
    colors = [f"#{abs(hash(opt)) % 0xFFFFFF:06x}" for opt in options]

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=options, colors=colors, startangle=90, counterclock=False,
           wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    ax.set_aspect('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    
    # Draw a pointer
    ax.arrow(0, 0, 0, 1.1, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    plt.title("Spin Wheel", fontsize=24, weight='bold')

    # Save the plot to a buffer
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
    # 1. DETERMINE THE WINNER
    if rigged_winner_index is not None:
        winner = st.session_state.options[rigged_winner_index - 1]
    else:
        winner = random.choice(st.session_state.options)

    # 2. HANDLE FAST SPIN
    if fast_spin:
        placeholder.success(f"## Winner: **{winner}**")
        st.balloons()
    else:
        # 3. PERFORM ANIMATION
        winner_index = st.session_state.options.index(winner)
        slice_angle = 360 / len(st.session_state.options)
        
        # Calculate the target angle to center the winner under the pointer (at 90 degrees)
        target_rotation = - (winner_index * slice_angle + slice_angle / 2)
        
        # Add random extra spins for visual effect
        total_rotation = 360 * 3 + target_rotation # 3 full spins
        
        num_frames = 60 # Number of frames for the animation
        
        for i in range(num_frames + 1):
            # Simple easing out effect
            progress = 1 - (1 - (i / num_frames))**3
            current_rotation = progress * total_rotation
            
            # Create a rotated pie chart
            plt.figure(figsize=(8, 8))
            sizes = [1] * len(st.session_state.options)
            colors = [f"#{abs(hash(opt)) % 0xFFFFFF:06x}" for opt in st.session_state.options]
            
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(sizes, labels=st.session_state.options, colors=colors, 
                   startangle=90 + current_rotation, # This rotates the pie
                   counterclock=False, wedgeprops={'edgecolor': 'white'})
            ax.set_aspect('equal')
            ax.arrow(0, 0, 0, 1.1, head_width=0.1, head_length=0.1, fc='black', ec='black')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', transparent=True)
            buf.seek(0)
            
            # Update the placeholder with the new frame
            placeholder.image(buf, use_column_width=True)
            plt.close(fig)
            time.sleep(0.05) # Control animation speed
        
        # 4. SHOW FINAL RESULT
        placeholder.success(f"## Winner: **{winner}**")
        st.balloons()
else:
    # Show the initial static wheel before the first spin
    static_wheel_img = create_wheel(st.session_state.options)
    placeholder.image(static_wheel_img, use_column_width=True)
