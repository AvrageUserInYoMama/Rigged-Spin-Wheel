import streamlit as st
import streamlit.components.v1 as components
import json
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Spin Wheel",
    page_icon="🎡",
    layout="centered"
)

# --- JAVASCRIPT & HTML COMPONENT ---
def create_wheel_component(options, is_spinning=False, winner_to_land_on=None):
    """
    Generates the HTML for the wheel. Can be static or spinning.
    - is_spinning=False: Renders a static, non-interactive wheel.
    - is_spinning=True: Renders a wheel that immediately spins and lands on the winner.
    """
    options_json = json.dumps(options)
    winner_json = json.dumps(winner_to_land_on)

    # Conditionally generate the JavaScript for spinning or static display
    if is_spinning:
        animation_script = f"""
            const winner = {winner_json};
            const winningSegment = theWheel.segments.find(s => s && s.text === winner);
            if (winningSegment) {{
                let stopAt = theWheel.getRandomForSegment(winningSegment.segmentNumber);
                theWheel.animation.stopAngle = stopAt;
            }}
            theWheel.startAnimation();
        """
    else:
        animation_script = "theWheel.draw(); // Draw static wheel"

    component_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Winwheel.js Wheel</title>
        <style>
            body, html {{ margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; background-color: transparent; }}
        </style>
    </head>
    <body>
        <canvas id='canvas' width='400' height='400'></canvas>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/winwheeljs@2.8.0/dist/Winwheel.min.js"></script>
        <script>
            (function() {{
                const options = {options_json};
                const segments = options.map(opt => ({{'text': opt.text, 'fillStyle': opt.fillStyle}}));
                let theWheel = new Winwheel({{
                    'numSegments'  : segments.length, 'outerRadius'  : 180, 'innerRadius'  : 40,
                    'textFontSize' : 16, 'segments' : segments, 'pointerAngle' : 90,
                    'animation'    : {{ 'type': 'spinToStop', 'duration': 6, 'spins': 8, 'callbackFinished': () => {{}} }}
                }});
                {animation_script}
            }})();
        </script>
    </body>
    </html>
    """
    return components.html(component_html, height=410, width=410)

# --- MAIN APP LOGIC ---
# Set admin status based on URL query parameter
if st.query_params.get("mode") == "admin":
    st.session_state.is_admin = True

st.title("🎡 Spin Wheel")

# --- SESSION STATE INITIALIZATION ---
if 'options' not in st.session_state:
    st.session_state.options = ["Pizza", "Burger", "Tacos", "Salad", "Sushi", "Pasta"]
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'fast_spin' not in st.session_state:
    st.session_state.fast_spin = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Controls")
    options_text = st.text_area("Options (one per line)", value="\n".join(st.session_state.options), height=250)
    
    if st.button("Update Wheel"):
        st.session_state.options = [opt.strip() for opt in options_text.split("\n") if opt.strip()]
        st.session_state.winner = None
        st.rerun()

    st.markdown("---")
    
    # Fast Spin toggle is visible to everyone
    st.session_state.fast_spin = st.toggle(
        "Fast Spin",
        key='fast_spin_toggle',
        help="Skip the spin animation for an instant result."
    )
    
    # The Winner Override controls ONLY appear if admin AND fast spin are enabled
    rigged_winner_index = None
    if st.session_state.is_admin and st.session_state.fast_spin:
        st.info("🤫 Admin Controls Enabled")
        rigged_winner_index = st.number_input(
            "Winner Number (1, 2, 3...)",
            min_value=1,
            max_value=len(st.session_state.options) if st.session_state.options else 1,
            step=1, value=None, placeholder="Enter # to force win..."
        )

# --- MAIN PAGE ---
if not st.session_state.options:
    st.warning("Please add some options in the sidebar to create the wheel.")
else:
    # Always prepare colors for the wheel display
    if 'option_colors' not in st.session_state or len(st.session_state.option_colors) != len(st.session_state.options):
        st.session_state.option_colors = {opt: f'hsl({random.randint(0, 360)}, 70%, 80%)' for opt in st.session_state.options}
    options_with_colors = [{'text': opt, 'fillStyle': st.session_state.option_colors.get(opt)} for opt in st.session_state.options]
    
    # Determine the winner when the spin button is clicked
    if st.button("SPIN!", type="primary", use_container_width=True):
        st.session_state.winner = None # Clear previous winner to ensure rerun shows animation
        winner_determined = False
        if rigged_winner_index is not None and 0 < rigged_winner_index <= len(st.session_state.options):
            st.session_state.winner = st.session_state.options[rigged_winner_index - 1]
            winner_determined = True
        
        if not winner_determined:
            st.session_state.winner = random.choice(st.session_state.options)

    # Display logic: Show wheel, animation, or result based on state
    if st.session_state.winner is None:
        # Before any spin, show the static wheel
        st.info("Click the SPIN! button to start.")
        create_wheel_component(options_with_colors, is_spinning=False)
    elif st.session_state.fast_spin:
        # If fast spin is on, just show the result text
        st.success(f"## Winner: **{st.session_state.winner}**")
        st.balloons()
    else:
        # Otherwise, show the spinning wheel animation
        with st.container():
            create_wheel_component(options_with_colors, is_spinning=True, winner_to_land_on=st.session_state.winner)
            st.success(f"## Winner: **{st.session_state.winner}**")
            st.balloons()
