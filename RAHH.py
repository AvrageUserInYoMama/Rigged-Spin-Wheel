import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
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
    """Generates the HTML for the wheel. Can be static or spinning."""
    options_json = json.dumps(options)
    
    if is_spinning:
        winner_json = json.dumps(winner_to_land_on)
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

# --- SESSION STATE & ADMIN CHECK ---
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = st.query_params.get("mode") == "admin"
if 'options' not in st.session_state:
    st.session_state.options = ["Pizza", "Burger", "Tacos", "Salad", "Sushi", "Pasta"]
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'fast_spin' not in st.session_state:
    st.session_state.fast_spin = False
if 'is_spinning' not in st.session_state:
    st.session_state.is_spinning = False

# --- UI ELEMENTS ---
st.title("🎡 Spin Wheel")

with st.sidebar:
    st.header("⚙️ Controls")
    options_text = st.text_area("Options (one per line)", value="\n".join(st.session_state.options), height=250)
    
    if st.button("Update Wheel"):
        st.session_state.options = [opt.strip() for opt in options_text.split("\n") if opt.strip()]
        st.session_state.winner = None
        st.session_state.is_spinning = False
        st.rerun()

    st.markdown("---")
    st.session_state.fast_spin = st.toggle("Fast Spin", key='fast_spin_toggle', help="Skip the spin animation for an instant result.")
    
    rigged_winner_index = None
    if st.session_state.is_admin and st.session_state.fast_spin:
        st.info("🤫 Admin Controls Enabled")
        rigged_winner_index = st.number_input(
            "Winner Number (1, 2, 3...)", min_value=1,
            max_value=len(st.session_state.options) if st.session_state.options else 1,
            step=1, value=None, placeholder="Enter # to force win..."
        )

# --- MAIN PAGE LOGIC ---
if not st.session_state.options:
    st.warning("Please add some options in the sidebar.")
else:
    # Prepare colors for wheel display
    if 'option_colors' not in st.session_state or len(st.session_state.option_colors) != len(st.session_state.options):
        st.session_state.option_colors = {opt: f'hsl({random.randint(0, 360)}, 70%, 80%)' for opt in st.session_state.options}
    options_with_colors = [{'text': opt, 'fillStyle': st.session_state.option_colors.get(opt)} for opt in st.session_state.options]

    # This container will hold the wheel or the final result
    placeholder = st.empty()

    if st.session_state.is_spinning:
        # STATE 2: We are in the middle of a spin animation
        with placeholder.container():
            create_wheel_component(options_with_colors, is_spinning=True, winner_to_land_on=st.session_state.winner)
            # This will automatically refresh the page after 6.5 seconds
            st_autorefresh(interval=6500, limit=1, key="spin_refresher")
        st.session_state.is_spinning = False # Set to false so the next run shows the winner
    elif st.session_state.winner is not None:
        # STATE 3: The spin is complete, show the final winner
        with placeholder.container():
            st.success(f"## Winner: **{st.session_state.winner}**")
            st.balloons()
    else:
        # STATE 1: Default state, waiting for a spin
        with placeholder.container():
            st.info("Click the SPIN! button to start.")
            create_wheel_component(options_with_colors, is_spinning=False)

    # The SPIN button logic that transitions between states
    if st.button("SPIN!", type="primary", use_container_width=True):
        # Determine the winner
        if rigged_winner_index is not None:
            st.session_state.winner = st.session_state.options[rigged_winner_index - 1]
        else:
            st.session_state.winner = random.choice(st.session_state.options)

        if st.session_state.fast_spin:
            # Fast spin is on, skip animation and go straight to showing the winner
            st.session_state.is_spinning = False
        else:
            # Fast spin is off, trigger the animation state
            st.session_state.is_spinning = True
        
        st.rerun()
