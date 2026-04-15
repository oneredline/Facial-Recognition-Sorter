"""
app.py — FaceSorter Dashboard
Topaz-themed Streamlit UI for event photo face sorting.
Run with: streamlit run app.py
"""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="FaceSorter",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

TOPAZ_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background-color: #0C1822 !important;
    color: #DFF0F6 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.4rem !important; padding-bottom: 2rem !important; }

[data-testid="stSidebar"] {
    background-color: #081017 !important;
    border-right: 1px solid #172D3E !important;
}

.sidebar-brand {
    display: flex; align-items: center; gap: 10px;
    padding-bottom: 14px; margin-bottom: 14px;
    border-bottom: 1px solid #172D3E;
}
.sidebar-brand-icon {
    width: 32px; height: 32px;
    background: rgba(0,196,218,.15);
    border: 1px solid rgba(0,196,218,.3);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
}
.sidebar-brand-title { font-size: 15px; font-weight: 700; color: #00C4DA; letter-spacing: -.3px; }
.sidebar-brand-sub   { font-size: 10px; color: #4A7888; margin-top: 1px; }

.section-label {
    font-size: 10px; font-weight: 600;
    letter-spacing: .1em; text-transform: uppercase;
    color: #4A7888; margin: 14px 0 6px 0;
    padding-bottom: 6px; border-bottom: 1px solid #172D3E;
}

.stTextInput > label { color: #7AAABB !important; font-size: 12px !important; }
.stTextInput > div > div > input {
    background: #0F2030 !important; border: 1px solid #173040 !important;
    border-radius: 6px !important; color: #DFF0F6 !important; font-size: 13px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00C4DA !important;
    box-shadow: 0 0 0 2px rgba(0,196,218,.14) !important;
}

.stSlider > label { color: #7AAABB !important; font-size: 12px !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: #00C4DA !important; border-color: #00C4DA !important;
}

.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg,#00C4DA,#0094AB) !important;
    color: #fff !important; border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 14px !important;
    padding: .65rem 1rem !important; letter-spacing: .02em !important;
    margin-top: 4px !important;
    box-shadow: 0 4px 16px rgba(0,196,218,.22) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg,#1AD6EC,#00AECA) !important;
    box-shadow: 0 6px 22px rgba(0,196,218,.38) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:disabled {
    background: #172D3E !important; color: #365060 !important;
    box-shadow: none !important; transform: none !important;
}

.main-header {
    background: #0F2030; border: 1px solid #172D3E;
    border-radius: 12px; padding: 18px 24px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 16px;
}
.main-header-title { font-size: 22px; font-weight: 700; color: #DFF0F6; letter-spacing: -.5px; margin: 0; }
.main-header-title span { color: #00C4DA; }
.main-header-sub { margin: 4px 0 0 0; color: #4A7888; font-size: 13px; }
.main-header-badge {
    background: rgba(0,196,218,.12); border: 1px solid rgba(0,196,218,.25);
    color: #00C4DA; border-radius: 6px; padding: 4px 10px;
    font-size: 11px; font-weight: 600;
}

.stat-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 16px; }
.stat-card {
    background: #0F2030; border: 1px solid #172D3E;
    border-radius: 10px; padding: 14px; text-align: center;
}
.stat-card.hl { border-color: rgba(0,196,218,.4); background: rgba(0,196,218,.07); }
.stat-icon  { font-size: 18px; margin-bottom: 5px; }
.stat-value { font-size: 26px; font-weight: 700; color: #DFF0F6; line-height: 1; margin-bottom: 4px; }
.stat-value.teal { color: #00C4DA; }
.stat-label { font-size: 11px; color: #4A7888; font-weight: 500; }

.section-card {
    background: #0F2030; border: 1px solid #172D3E;
    border-radius: 10px; padding: 16px 18px; margin-bottom: 14px;
}
.section-card-title {
    font-size: 11px; font-weight: 600; letter-spacing: .08em;
    text-transform: uppercase; color: #4A7888;
    margin: 0 0 12px 0; padding-bottom: 8px; border-bottom: 1px solid #172D3E;
}

.folder-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(170px,1fr)); gap: 7px; margin-top: 4px; }
.folder-item {
    background: #0C1822; border: 1px solid #172D3E;
    border-radius: 7px; padding: 8px 10px;
    display: flex; align-items: center; gap: 7px;
}
.folder-name { font-size: 12px; color: #BCDCE8; font-weight: 500; flex: 1; }
.folder-badge {
    font-size: 10px; color: #00C4DA; font-weight: 600;
    background: rgba(0,196,218,.1); padding: 1px 6px; border-radius: 4px;
}

.idle-box {
    text-align: center; padding: 48px 24px;
    background: #0F2030; border: 1px dashed #172D3E; border-radius: 12px;
    margin-bottom: 14px;
}
.idle-box-icon { font-size: 42px; margin-bottom: 12px; }
.idle-box-title { font-size: 16px; color: #7AAABB; font-weight: 500; margin: 0 0 6px 0; }
.idle-box-sub   { font-size: 13px; color: #365060; margin: 0; }

.tip-box {
    background: rgba(0,196,218,.06); border: 1px solid rgba(0,196,218,.2);
    border-radius: 8px; padding: 12px 16px; margin-top: 14px;
}
.tip-box-title { font-size: 10px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: #00C4DA; margin: 0 0 7px 0; }
.tip-box-body  { font-size: 12px; color: #7AAABB; line-height: 1.75; margin: 0; }
.tip-box-body code { background: rgba(0,196,218,.12); padding: 1px 5px; border-radius: 3px; font-size: 11px; color: #00C4DA; }

.stProgress > div > div > div > div {
    background: linear-gradient(90deg,#00C4DA,#0094AB) !important; border-radius: 4px !important;
}
.stProgress > div > div > div {
    background: #172D3E !important; border-radius: 4px !important;
}
</style>
"""


def render_sidebar() -> dict:
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">📸</div>
                <div>
                    <div class="sidebar-brand-title">FaceSorter</div>
                    <div class="sidebar-brand-sub">Powered by InsightFace</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">📁 Folders</div>', unsafe_allow_html=True)
        input_folder  = st.text_input("Input folder",  value="./input",  label_visibility="visible")
        output_folder = st.text_input("Output folder", value="./output", label_visibility="visible")

        st.markdown('<div class="section-label">🔍 Face Detection</div>', unsafe_allow_html=True)
        min_face_size  = st.slider("Min face size",   0.01, 0.15, 0.04, 0.01, format="%.2f",
                                   help="Fraction of image width. Raise to exclude background people.")
        min_confidence = st.slider("Min confidence",  0.30, 0.95, 0.55, 0.05, format="%.2f",
                                   help="InsightFace score. Lower catches more faces.")
        min_sharpness  = st.slider("Min sharpness",   10,   150,  45,
                                   help="Lower = blur-tolerant (good for candids).")

        st.markdown('<div class="section-label">🎭 Pose / Candid Angles</div>', unsafe_allow_html=True)
        max_yaw   = st.slider("Max yaw (°)",   15, 90, 60, help="Left/right head turn. 60°+ is candid-friendly.")
        max_pitch = st.slider("Max pitch (°)", 15, 80, 45, help="Up/down tilt.")

        st.markdown('<div class="section-label">🧩 Clustering</div>', unsafe_allow_html=True)
        dbscan_eps   = st.slider("Matching strictness", 0.25, 0.70, 0.45, 0.05, format="%.2f",
                                 help="Lower = stricter. Raise if same person splits into two folders.")
        min_samples  = st.slider("Min photos for folder", 1, 10, 2,
                                 help="A person must appear in this many photos to get their own folder.")

        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("▶  Sort Photos", disabled=st.session_state.get('running', False), use_container_width=True)

    return {
        'run': run,
        'config': {
            'input_folder':        input_folder,
            'output_folder':       output_folder,
            'min_face_size_ratio': min_face_size,
            'min_confidence':      min_confidence,
            'min_sharpness':       float(min_sharpness),
            'max_yaw_angle':       float(max_yaw),
            'max_pitch_angle':     float(max_pitch),
            'dbscan_eps':          dbscan_eps,
            'dbscan_min_samples':  min_samples,
        }
    }


def render_results(r: dict):
    st.success(f"✅  Sort complete — {r['people_found']} people found across {r['total_photos']} photos.")

    st.markdown(f"""
        <div class="stat-row">
            <div class="stat-card">
                <div class="stat-icon">🖼️</div>
                <div class="stat-value">{r['total_photos']}</div>
                <div class="stat-label">Photos scanned</div>
            </div>
            <div class="stat-card hl">
                <div class="stat-icon">👥</div>
                <div class="stat-value teal">{r['people_found']}</div>
                <div class="stat-label">People found</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-value">{r['photos_sorted']}</div>
                <div class="stat-label">Photos sorted</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">❓</div>
                <div class="stat-value">{r['unmatched']}</div>
                <div class="stat-label">Unmatched</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-card"><div class="section-card-title">📂 Output Folders</div>', unsafe_allow_html=True)
    items_html = '<div class="folder-grid">'
    for f in r['person_folders'][:40]:
        items_html += f'<div class="folder-item"><span style="font-size:14px;">👤</span><span class="folder-name">{f["name"]}</span><span class="folder-badge">{f["count"]}</span></div>'
    if len(r['person_folders']) > 40:
        items_html += f'<div class="folder-item"><span class="folder-name" style="color:#365060;">+{len(r["person_folders"])-40} more...</span></div>'
    items_html += '</div>'
    st.markdown(items_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    sk = r['skip_counts']
    st.markdown(f"""
        <div class="tip-box">
            <p class="tip-box-title">💡 Summary &amp; next steps</p>
            <p class="tip-box-body">
                Output saved to <code>{r['output_folder']}</code><br>
                Skipped {sk.get('size',0)} background faces &nbsp;·&nbsp;
                {sk.get('blur',0)} blurry &nbsp;·&nbsp;
                {sk.get('angle',0)} extreme angles &nbsp;·&nbsp;
                {sk.get('confidence',0)} low confidence<br>
                If the same person appears in two folders, merge them before uploading.<br>
                Upload each <code>person-XXX</code> folder as a <strong>Set</strong> inside your Pixieset Collection.
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_idle():
    st.markdown("""
        <div class="idle-box">
            <div class="idle-box-icon">📷</div>
            <p class="idle-box-title">Ready to sort your event photos</p>
            <p class="idle-box-sub">Set your input folder in the sidebar, adjust filters if needed,<br>then click Sort Photos to begin.</p>
        </div>
        <div class="tip-box">
            <p class="tip-box-title">💡 Quick start</p>
            <p class="tip-box-body">
                1. Export your event photos as JPG or TIFF into the <code>input/</code> folder<br>
                2. Leave all settings at defaults for your first run<br>
                3. Large events (150–500 people) typically take 5–20 min on Mac<br>
                4. Each output folder becomes a <strong>Set</strong> in your Pixieset Collection
            </p>
        </div>
    """, unsafe_allow_html=True)


def main():
    st.markdown(TOPAZ_CSS, unsafe_allow_html=True)

    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'error' not in st.session_state:
        st.session_state.error = None
    if 'running' not in st.session_state:
        st.session_state.running = False

    sidebar = render_sidebar()

    st.markdown("""
        <div class="main-header">
            <div>
                <p class="main-header-title">Face<span>Sorter</span></p>
                <p class="main-header-sub">AI-powered event photo organizer — sort once, deliver fast</p>
            </div>
            <div class="main-header-badge">InsightFace &nbsp;·&nbsp; buffalo_l</div>
        </div>
    """, unsafe_allow_html=True)

    if sidebar['run']:
        st.session_state.results = None
        st.session_state.error   = None
        st.session_state.running = True

        progress_bar = st.progress(0.0)
        status_text  = st.empty()

        def step_cb(phase, current, total, message):
            fractions = {'init': 0.02, 'scan': 0.65, 'cluster': 0.80, 'write': 1.0}
            prev = {'init': 0.0, 'scan': 0.02, 'cluster': 0.65, 'write': 0.80}
            low  = prev.get(phase, 0.0)
            high = fractions.get(phase, 1.0)
            frac = low + (current / max(total, 1)) * (high - low)
            progress_bar.progress(round(min(frac, 1.0), 3))
            status_text.markdown(
                f"<p style='color:#4A7888;font-size:12px;'>⏳ {message}</p>",
                unsafe_allow_html=True
            )

        try:
            from face_sorter import run_sort
            results = run_sort(sidebar['config'], step_cb=step_cb)
            st.session_state.results = results
        except Exception as e:
            st.session_state.error = str(e)
        finally:
            st.session_state.running = False
            progress_bar.empty()
            status_text.empty()

    if st.session_state.error:
        st.error(f"❌ {st.session_state.error}")
        render_idle()
    elif st.session_state.results:
        render_results(st.session_state.results)
    else:
        render_idle()


if __name__ == '__main__':
    main()
