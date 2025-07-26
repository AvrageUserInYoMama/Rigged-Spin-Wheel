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
def create_wheel_component(options, winner_to_land_on, key):
    options_json = json.dumps(options)
    winner_json = json.dumps(winner_to_land_on)

    component_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Winwheel.js Simple Wheel</title>
        <style>
            body, html {{ margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; background-color: transparent; }}
            #canvasContainer {{ position: relative; width: 400px; height: 400px; }}
            #spin_button_in_canvas {{
                position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                background: #fff; color: #333; border: 3px solid #333; border-radius: 50%;
                width: 80px; height: 80px; font-size: 1.2em; font-weight: bold; cursor: default; z-index: 10;
            }}
        </style>
    </head>
    <body>
        <div id="canvasContainer">
            <canvas id='canvas' width='400' height='400'></canvas>
            <button id="spin_button_in_canvas">SPIN!</button>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/winwheeljs@2.8.0/dist/Winwheel.min.js"></script>
        <script>
            (function() {{
                const options = {options_json};
                const winner = {winner_json};
                const segments = options.map(opt => ({{'text': opt.text, 'fillStyle': opt.fillStyle}}));
                let theWheel = new Winwheel({{
                    'numSegments'  : segments.length, 'outerRadius'  : 180, 'innerRadius'  : 40,
                    'textFontSize' : 16, 'segments' : segments,
                    'animation'    : {{ 'type': 'spinToStop', 'duration': 6, 'spins': 8, 'callbackFinished': () => {{}} }}
                }});
                const winningSegment = theWheel.segments.find(s => s && s.text === winner);
                if (winningSegment) {{
                    let stopAt = theWheel.getRandomForSegment(winningSegment.segmentNumber);
                    theWheel.animation.stopAngle = stopAt;
                }}
                theWheel.startAnimation();
            }})();
        </script>
    </body>
    </html>
    """
    return components.html(component_html, height=410, width=410, key=key)


# --- MAIN APP LOGIC ---
st.title("🎡 Spin Wheel")

# --- SESSION STATE INITIALIZATION ---
if 'options' not in st.session_state:
    st.session_state.options = ["Pizza", "Burger", "Tacos", "Salad", "Sushi", "Pasta"]
if 'winner' not in st.session_state:
    st.session_state.winner = None
if 'spin_key' not in st.session_state:
    st.session_state.spin_key = 0

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Controls")
    options_text = st.text_area("Options (one per line)", value="\n".join(st.session_state.options), height=150)
    
    if st.button("Update Wheel"):
        st.session_state.options = [opt.strip() for opt in options_text.split("\n") if opt.strip()]
        st.session_state.winner = None
        st.rerun()

    # --- UPDATED: HIDDEN RIGGING MECHANISM ---
    # The rigging input only appears if the URL has "?mode=admin"
    if st.query_params.get("mode") == "admin":
        st.markdown("---")
        st.info("🤫 Admin Mode Activated")
        rigged_winner_input = st.text_input(
            "Winner Override",
            placeholder="Enter option to force win..."
        ).strip()
    else:
        # If not in admin mode, this variable must still exist but be empty
        rigged_winner_input = ""

# --- MAIN PAGE ---
if not st.session_state.options:
    st.warning("Please add some options in the sidebar to create the wheel.")
else:
    if st.button("SPIN!", type="primary", use_container_width=True):
        st.session_state.spin_key += 1
        if rigged_winner_input and rigged_winner_input in st.session_state.options:
            st.session_state.winner = rigged_winner_input
        else:
            st.session_state.winner = random.choice(st.session_state.options)

    if st.session_state.winner:
        if 'option_colors' not in st.session_state or len(st.session_state.option_colors) != len(st.session_state.options):
            st.session_state.option_colors = {opt: f'hsl({random.randint(0, 360)}, 70%, 80%)' for opt in st.session_state.options}
        
        options_with_colors = [{'text': opt, 'fillStyle': st.session_state.option_colors.get(opt)} for opt in st.session_state.options]
        
        with st.container():
            create_wheel_component(options_with_colors, st.session_state.winner, key=f"spin_{st.session_state.spin_key}")
            st.success(f"## Winner: **{st.session_state.winner}**")
            st.balloons()
    else:
        st.info("Click the SPIN! button to see the wheel.")
