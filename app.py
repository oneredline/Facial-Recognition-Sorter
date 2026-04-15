"""
app.py - FaceSorter
Premium AI workflow command center.
Run with: python3 -m streamlit run app.py
"""

import os
import streamlit as st
import base64
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="FaceSorter",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Presets ────────────────────────────────────────────────────────────────────
PRESETS = {
    "Fast Pass": {
        "min_face_size_ratio": 0.06, "min_confidence": 0.65, "min_sharpness": 65,
        "max_yaw_angle": 45, "max_pitch_angle": 35, "dbscan_eps": 0.40, "dbscan_min_samples": 2,
        "desc": "Subjects only, strict matching, fastest run"
    },
    "Balanced": {
        "min_face_size_ratio": 0.04, "min_confidence": 0.55, "min_sharpness": 45,
        "max_yaw_angle": 60, "max_pitch_angle": 45, "dbscan_eps": 0.45, "dbscan_min_samples": 2,
        "desc": "Recommended for most events"
    },
    "Precision": {
        "min_face_size_ratio": 0.025, "min_confidence": 0.45, "min_sharpness": 25,
        "max_yaw_angle": 75, "max_pitch_angle": 60, "dbscan_eps": 0.52, "dbscan_min_samples": 2,
        "desc": "Candid-heavy events, wider angle tolerance"
    },
    "Custom": {
        "desc": "Manually tune all parameters"
    }
}

STEPS = [
    ("init",    "Loading AI Model",    "Initializing InsightFace buffalo_l"),
    ("scan",    "Scanning Faces",      "Detecting and encoding faces in every photo"),
    ("cluster", "Clustering Guests",   "Grouping faces by identity"),
    ("write",   "Building Galleries",  "Copying photos into person folders"),
    ("done",    "Export Complete",     "All galleries ready for Pixieset upload"),
]

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.tiff', '.tif'}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Montserrat', sans-serif !important;
    background-color: #0E0E11 !important;
    color: #EDEDF2 !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #14141A !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}

.sb-header {
    padding: 22px 18px 18px 18px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 4px;
}
.sb-logo-row { display:flex; align-items:center; gap:10px; margin-bottom:12px; }
.sb-logo-mark {
    width:34px; height:34px; border-radius:10px;
    background: linear-gradient(135deg, #4F8EF7 0%, #7B5FEA 100%);
    display:flex; align-items:center; justify-content:center;
    font-size:16px; flex-shrink:0;
}
.sb-product-name { font-size:15px; font-weight:800; color:#EDEDF2; letter-spacing:-.3px; }
.sb-product-sub  { font-size:9px;  font-weight:500; color:#44445A; letter-spacing:.1em; text-transform:uppercase; margin-top:1px; }

.sb-mode-label { font-size:9px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:#44445A; margin-bottom:8px; }
.mode-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:5px; }
.mode-btn {
    background:#1E1E26; border:1px solid rgba(255,255,255,0.07); border-radius:9px;
    padding:7px 4px; text-align:center; font-size:9px; font-weight:700;
    color:#55556A; letter-spacing:.05em; text-transform:uppercase; cursor:pointer;
}
.mode-btn.active {
    background:rgba(79,142,247,0.14); border-color:rgba(79,142,247,0.45); color:#4F8EF7;
}

.sb-section { font-size:9px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:#33334A; padding:14px 18px 5px 18px; }
.sb-divider { height:1px; background:rgba(255,255,255,0.04); margin:10px 0; }

.stTextInput > label { color:#55556A !important; font-size:9px !important; font-weight:700 !important; letter-spacing:.12em !important; text-transform:uppercase !important; }
.stTextInput > div > div > input {
    background:#1E1E26 !important; border:1px solid rgba(255,255,255,0.07) !important;
    border-radius:9px !important; color:#EDEDF2 !important; font-size:12px !important;
    font-family:'Montserrat',sans-serif !important; padding:8px 10px !important;
}
.stTextInput > div > div > input:focus {
    border-color:rgba(79,142,247,0.6) !important;
    box-shadow:0 0 0 3px rgba(79,142,247,0.12) !important;
}

.stSlider > label { color:#55556A !important; font-size:9px !important; font-weight:700 !important; letter-spacing:.12em !important; text-transform:uppercase !important; }
.stSlider > div > div { padding-top:4px !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background:#4F8EF7 !important; border-color:#4F8EF7 !important;
    width:14px !important; height:14px !important;
    box-shadow:0 0 0 3px rgba(79,142,247,0.25) !important;
}
.stSlider [data-baseweb="slider"] > div:first-child > div:first-child {
    height:3px !important;
}

.microcopy { font-size:10px; font-weight:400; color:#44445A; line-height:1.5; margin-top:-4px; margin-bottom:8px; padding:0 2px; }

.stButton > button {
    width:100% !important;
    background:linear-gradient(135deg,#4F8EF7,#7B5FEA) !important;
    color:#FFFFFF !important; border:none !important; border-radius:12px !important;
    font-family:'Montserrat',sans-serif !important; font-weight:700 !important;
    font-size:11px !important; padding:.75rem !important;
    letter-spacing:.1em !important; text-transform:uppercase !important;
    margin-top:6px !important;
    box-shadow:0 4px 20px rgba(79,142,247,0.35) !important;
}
.stButton > button:hover { box-shadow:0 6px 28px rgba(79,142,247,0.5) !important; }
.stButton > button:disabled { background:#1E1E26 !important; color:#33334A !important; box-shadow:none !important; }

/* ── Header ── */
.page-header {
    background:linear-gradient(135deg, #12122A 0%, #0E1A3A 60%, #0E0E11 100%);
    border-radius:20px; padding:28px 32px;
    margin:18px 0 18px 0;
    display:flex; align-items:center; justify-content:space-between;
    border:1px solid rgba(79,142,247,0.12);
    position:relative; overflow:hidden;
}
.page-header::after {
    content:''; position:absolute; top:-80px; right:-80px;
    width:320px; height:320px;
    background:radial-gradient(circle,rgba(79,142,247,0.15) 0%,transparent 68%);
    border-radius:50%; pointer-events:none;
}
.header-left { z-index:1; }
.header-eyebrow { font-size:9px; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:#4F8EF7; margin-bottom:6px; }
.header-title { font-size:30px; font-weight:800; color:#EDEDF2; letter-spacing:-1.2px; margin:0; line-height:1; }
.header-title span { color:#4F8EF7; }
.header-sub { font-size:12px; font-weight:400; color:#55556A; margin:7px 0 0 0; letter-spacing:.01em; }
.header-stats { display:flex; gap:12px; z-index:1; }
.hstat {
    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.07);
    border-radius:12px; padding:10px 16px; text-align:center; min-width:80px;
}
.hstat-val { font-size:20px; font-weight:800; color:#EDEDF2; letter-spacing:-.5px; line-height:1; }
.hstat-val.blue { color:#4F8EF7; }
.hstat-lbl { font-size:8px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#44445A; margin-top:4px; }

/* ── Workspace ── */
.workspace {
    background:#12121A;
    border:1px solid rgba(255,255,255,0.05);
    border-radius:20px;
    padding:48px 32px;
    text-align:center;
    margin-bottom:14px;
    position:relative;
    overflow:hidden;
    min-height:360px;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
}
.workspace::before {
    content:''; position:absolute; top:50%; left:50%;
    transform:translate(-50%,-50%);
    width:500px; height:500px;
    background:radial-gradient(circle,rgba(79,142,247,0.05) 0%,transparent 65%);
    border-radius:50%; pointer-events:none;
}
.ws-drop-zone {
    border:2px dashed rgba(79,142,247,0.25); border-radius:16px;
    padding:32px 48px; margin-bottom:24px; width:100%; max-width:500px;
    background:rgba(79,142,247,0.03);
}
.ws-drop-icon { font-size:48px; margin-bottom:12px; line-height:1; }
.ws-drop-title { font-size:16px; font-weight:700; color:#EDEDF2; margin:0 0 6px 0; letter-spacing:-.2px; }
.ws-drop-sub { font-size:12px; font-weight:400; color:#55556A; margin:0; line-height:1.6; }
.ws-path {
    display:inline-flex; align-items:center; gap:6px;
    background:#1E1E26; border:1px solid rgba(255,255,255,0.07);
    border-radius:8px; padding:5px 12px; margin-top:12px;
    font-size:11px; font-weight:600; color:#4F8EF7; font-family:monospace;
}

.ws-photo-grid { display:flex; gap:8px; flex-wrap:wrap; justify-content:center; margin:16px 0; }
.ws-photo-slot {
    width:52px; height:52px; border-radius:50%;
    background:#1E1E26; border:1.5px solid rgba(255,255,255,0.07);
    display:flex; align-items:center; justify-content:center;
    font-size:10px; color:#33334A; font-weight:700;
}
.ws-photo-slot.filled {
    background:linear-gradient(135deg,rgba(79,142,247,0.2),rgba(123,95,234,0.2));
    border-color:rgba(79,142,247,0.3); color:#4F8EF7;
}

.status-chip {
    display:inline-flex; align-items:center; gap:6px;
    border-radius:20px; padding:5px 14px;
    font-size:10px; font-weight:700; letter-spacing:.06em; text-transform:uppercase;
}
.status-ready    { background:rgba(52,199,89,0.12); color:#34C759; border:1px solid rgba(52,199,89,0.25); }
.status-empty    { background:rgba(255,214,10,0.10); color:#FFD60A; border:1px solid rgba(255,214,10,0.2); }
.status-running  { background:rgba(79,142,247,0.12); color:#4F8EF7; border:1px solid rgba(79,142,247,0.3); }
.status-complete { background:rgba(123,95,234,0.12); color:#A78BFA; border:1px solid rgba(123,95,234,0.3); }

/* ── AI Step Indicator ── */
.step-panel {
    width:100%; max-width:560px; text-align:left;
}
.step-row {
    display:flex; align-items:flex-start; gap:14px;
    padding:10px 0; position:relative;
}
.step-row:not(:last-child)::after {
    content:''; position:absolute; left:15px; top:36px;
    width:2px; height:calc(100% - 10px);
    background:rgba(255,255,255,0.06);
}
.step-dot {
    width:30px; height:30px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    flex-shrink:0; font-size:12px; z-index:1;
    border:2px solid rgba(255,255,255,0.08);
    background:#1E1E26; color:#44445A;
}
.step-dot.active {
    border-color:#4F8EF7; background:rgba(79,142,247,0.15); color:#4F8EF7;
    box-shadow:0 0 12px rgba(79,142,247,0.35);
}
.step-dot.done {
    border-color:rgba(52,199,89,0.5); background:rgba(52,199,89,0.12); color:#34C759;
}
.step-content { padding-top:4px; }
.step-name { font-size:12px; font-weight:700; color:#55556A; letter-spacing:.02em; }
.step-name.active { color:#EDEDF2; }
.step-name.done   { color:#34C759; }
.step-desc { font-size:10px; font-weight:400; color:#33334A; margin-top:2px; }
.step-desc.active { color:#55556A; }

/* ── Result stats ── */
.stat-row { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:16px; }
.stat-card {
    background:#16161E; border:1px solid rgba(255,255,255,0.05);
    border-radius:16px; padding:18px 14px; text-align:center;
}
.stat-card.hl {
    background:linear-gradient(135deg,#141430,#141C40);
    border-color:rgba(79,142,247,0.2);
}
.stat-icon  { font-size:20px; margin-bottom:6px; }
.stat-value { font-size:30px; font-weight:800; color:#EDEDF2; line-height:1; margin-bottom:4px; letter-spacing:-1px; }
.stat-value.blue { color:#4F8EF7; }
.stat-label { font-size:8px; font-weight:700; color:#33334A; letter-spacing:.14em; text-transform:uppercase; }

/* ── People section ── */
.people-section {
    background:#12121A; border:1px solid rgba(255,255,255,0.05);
    border-radius:20px; padding:22px; margin-bottom:14px;
}
.people-header {
    display:flex; align-items:center; justify-content:space-between;
    margin-bottom:18px; padding-bottom:12px;
    border-bottom:1px solid rgba(255,255,255,0.05);
}
.people-title { font-size:13px; font-weight:700; color:#EDEDF2; letter-spacing:-.1px; }
.people-meta  { font-size:10px; font-weight:500; color:#44445A; }

.person-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:12px; }
.person-card {
    background:#1A1A24; border:1px solid rgba(255,255,255,0.05);
    border-radius:18px; overflow:hidden;
    display:flex; flex-direction:column; align-items:center;
    padding:18px 12px 14px 12px;
}
.person-card:hover { border-color:rgba(79,142,247,0.35); }
.person-thumb {
    width:80px; height:80px; border-radius:50%; object-fit:cover;
    border:2.5px solid #4F8EF7; margin-bottom:10px;
    box-shadow:0 0 0 4px rgba(79,142,247,0.12);
}
.person-placeholder {
    width:80px; height:80px; border-radius:50%;
    background:#1E1E26; border:2.5px solid rgba(79,142,247,0.4);
    display:flex; align-items:center; justify-content:center;
    font-size:28px; margin-bottom:10px;
}
.person-name  { font-size:11px; font-weight:600; color:#EDEDF2; text-align:center; margin-bottom:5px; }
.person-badge {
    font-size:8px; font-weight:700; color:#4F8EF7;
    background:rgba(79,142,247,0.1); padding:3px 9px;
    border-radius:20px; letter-spacing:.08em; text-transform:uppercase;
}

/* ── Summary tip ── */
.summary-box {
    background:rgba(79,142,247,0.06); border:1px solid rgba(79,142,247,0.14);
    border-radius:14px; padding:16px 20px; margin-top:14px;
}
.summary-title { font-size:9px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:#4F8EF7; margin:0 0 8px 0; }
.summary-body  { font-size:11px; font-weight:400; color:#55556A; line-height:1.8; margin:0; }
.summary-body code { background:rgba(79,142,247,0.14); padding:1px 6px; border-radius:4px; font-size:10px; color:#4F8EF7; font-family:monospace; }
.summary-body strong { color:#9AB4FF; font-weight:600; }

/* ── Progress ── */
.stProgress > div > div > div > div {
    background:linear-gradient(90deg,#4F8EF7,#7B5FEA) !important; border-radius:3px !important;
}
.stProgress > div > div > div { background:#1E1E26 !important; border-radius:3px !important; }

/* ── Radio as mode tabs ── */
div[data-testid="stRadio"] > label { display:none !important; }
div[data-testid="stRadio"] > div {
    display:grid !important; grid-template-columns:repeat(4,1fr) !important;
    gap:5px !important; background:transparent !important;
}
div[data-testid="stRadio"] > div > label {
    background:#1E1E26 !important; border:1px solid rgba(255,255,255,0.07) !important;
    border-radius:9px !important; padding:7px 4px !important; cursor:pointer !important;
    display:flex !important; justify-content:center !important; align-items:center !important;
}
div[data-testid="stRadio"] > div > label > div { display:none !important; }
div[data-testid="stRadio"] > div > label > div:last-child {
    display:block !important; font-size:9px !important; font-weight:700 !important;
    color:#55556A !important; letter-spacing:.06em !important; text-transform:uppercase !important;
    text-align:center !important;
}
div[data-testid="stRadio"] > div > label:has(input:checked) {
    background:rgba(79,142,247,0.14) !important; border-color:rgba(79,142,247,0.45) !important;
}
div[data-testid="stRadio"] > div > label:has(input:checked) > div:last-child { color:#4F8EF7 !important; }
div[data-testid="stRadio"] input[type="radio"] { display:none !important; }

div[data-testid="stSuccessMessage"] { background:rgba(52,199,89,0.08) !important; border-color:rgba(52,199,89,0.25) !important; border-radius:12px !important; color:#34C759 !important; }
div[data-testid="stErrorMessage"]   { background:rgba(255,69,58,0.08) !important;  border-color:rgba(255,69,58,0.25) !important;  border-radius:12px !important; }

.sb-footer { font-size:9px; font-weight:500; color:#33334A; text-align:center; padding:12px 0 4px 0; letter-spacing:.06em; }
</style>
"""


def thumbnail_to_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


def count_photos(folder_str):
    try:
        p = Path(folder_str)
        if not p.exists():
            return 0
        return sum(1 for f in p.rglob('*') if f.suffix.lower() in SUPPORTED_EXTENSIONS)
    except Exception:
        return 0


def make_person_card(folder_info):
    name = folder_info["name"]
    count = folder_info["count"]
    label = str(count) + (" photos" if count != 1 else " photo")
    b64 = thumbnail_to_b64(folder_info.get("thumbnail")) if folder_info.get("thumbnail") else None
    card = '<div class="person-card">'
    if b64:
        card += '<img class="person-thumb" src="data:image/jpeg;base64,' + b64 + '" alt="' + name + '">'
    else:
        card += '<div class="person-placeholder">👤</div>'
    card += '<div class="person-name">' + name + '</div>'
    card += '<div class="person-badge">' + label + '</div>'
    card += '</div>'
    return card


def render_step_indicator(current_phase):
    phase_order = ["init", "scan", "cluster", "write", "done"]
    try:
        current_idx = phase_order.index(current_phase)
    except ValueError:
        current_idx = 0

    html = '<div class="step-panel">'
    for i, (phase, name, desc) in enumerate(STEPS):
        if i < current_idx:
            dot_class = "done"
            name_class = "done"
            dot_icon = "✓"
        elif i == current_idx:
            dot_class = "active"
            name_class = "active"
            dot_icon = "●"
        else:
            dot_class = ""
            name_class = ""
            dot_icon = str(i + 1)

        html += (
            '<div class="step-row">'
            '<div class="step-dot ' + dot_class + '">' + dot_icon + '</div>'
            '<div class="step-content">'
            '<div class="step-name ' + name_class + '">' + name + '</div>'
            '<div class="step-desc ' + ("active" if i == current_idx else "") + '">' + desc + '</div>'
            '</div></div>'
        )
    html += '</div>'
    return html


def render_sidebar(photo_count):
    with st.sidebar:
        st.markdown("""
            <div class="sb-header">
                <div class="sb-logo-row">
                    <div class="sb-logo-mark">📸</div>
                    <div>
                        <div class="sb-product-name">FaceSorter</div>
                        <div class="sb-product-sub">Event Face Intelligence</div>
                    </div>
                </div>
                <div class="sb-mode-label">Processing Mode</div>
            </div>
        """, unsafe_allow_html=True)

        mode = st.radio(
            "mode",
            ["Fast Pass", "Balanced", "Precision", "Custom"],
            index=1,
            label_visibility="collapsed"
        )

        preset = PRESETS[mode]
        p = preset if mode != "Custom" else PRESETS["Balanced"]

        st.markdown('<div class="sb-section">Folders</div>', unsafe_allow_html=True)
        input_folder = st.text_input("Input folder", value="./input")
        output_folder = st.text_input("Output folder", value="./output")

        if mode == "Custom":
            st.markdown('<div class="sb-section">Face Detection</div>', unsafe_allow_html=True)
            min_face_size = st.slider("Min Face Size", 0.01, 0.15, float(p["min_face_size_ratio"]), 0.01, format="%.2f")
            st.markdown('<div class="microcopy">Ignore tiny background faces. Lower for wide crowd shots.</div>', unsafe_allow_html=True)

            min_confidence = st.slider("Min Confidence", 0.30, 0.95, float(p["min_confidence"]), 0.05, format="%.2f")
            st.markdown('<div class="microcopy">Raise for cleaner matches. Lower for aggressive detection.</div>', unsafe_allow_html=True)

            min_sharpness = st.slider("Min Sharpness", 10, 150, int(p["min_sharpness"]))
            st.markdown('<div class="microcopy">Lower tolerates motion blur — good for candid events.</div>', unsafe_allow_html=True)

            st.markdown('<div class="sb-section">Pose & Candid Angles</div>', unsafe_allow_html=True)
            max_yaw = st.slider("Max Yaw (°)", 15, 90, int(p["max_yaw_angle"]))
            st.markdown('<div class="microcopy">Left/right head turn limit. Raise for candid-heavy shoots.</div>', unsafe_allow_html=True)

            max_pitch = st.slider("Max Pitch (°)", 15, 80, int(p["max_pitch_angle"]))

            st.markdown('<div class="sb-section">Clustering</div>', unsafe_allow_html=True)
            dbscan_eps = st.slider("Matching Strictness", 0.25, 0.70, float(p["dbscan_eps"]), 0.05, format="%.2f")
            st.markdown('<div class="microcopy">Higher = fewer false matches. Lower = broader clustering.</div>', unsafe_allow_html=True)

            min_samples = st.slider("Min Photos for Folder", 1, 10, int(p["dbscan_min_samples"]))
            st.markdown('<div class="microcopy">Minimum appearances to create a person folder.</div>', unsafe_allow_html=True)
        else:
            min_face_size = float(p["min_face_size_ratio"])
            min_confidence = float(p["min_confidence"])
            min_sharpness  = int(p["min_sharpness"])
            max_yaw        = int(p["max_yaw_angle"])
            max_pitch      = int(p["max_pitch_angle"])
            dbscan_eps     = float(p["dbscan_eps"])
            min_samples    = int(p["dbscan_min_samples"])
            st.markdown(
                '<div style="margin:10px 18px;background:rgba(79,142,247,0.07);border:1px solid rgba(79,142,247,0.14);border-radius:10px;padding:10px 12px;">'
                '<div style="font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#4F8EF7;margin-bottom:4px;">' + mode + '</div>'
                '<div style="font-size:10px;font-weight:400;color:#55556A;line-height:1.5;">' + preset["desc"] + '</div>'
                '</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        disabled = st.session_state.get("running", False) or photo_count == 0
        run = st.button(
            "Sort Photos" if photo_count > 0 else "Add Photos to Input Folder",
            disabled=disabled
        )

        hour = datetime.now().hour
        is_dark = hour >= 18 or hour < 6
        st.markdown(
            '<div class="sb-footer">' + ("🌙 Night mode" if is_dark else "☀️ Day mode") + ' &nbsp;·&nbsp; FaceSorter v2</div>',
            unsafe_allow_html=True
        )

    return {
        "run": run,
        "config": {
            "input_folder": input_folder,
            "output_folder": output_folder,
            "min_face_size_ratio": min_face_size,
            "min_confidence": min_confidence,
            "min_sharpness": float(min_sharpness),
            "max_yaw_angle": float(max_yaw),
            "max_pitch_angle": float(max_pitch),
            "dbscan_eps": dbscan_eps,
            "dbscan_min_samples": min_samples,
        }
    }


def render_header(photo_count, results):
    people = str(results["people_found"]) if results else "—"
    sorted_count = str(results["photos_sorted"]) if results else "—"
    photos_val = str(photo_count) if photo_count > 0 else "—"

    people_class = "blue" if results else ""

    st.markdown(
        '<div class="page-header">'
        '<div class="header-left">'
        '<div class="header-eyebrow">AI Face Intelligence · buffalo_l</div>'
        '<p class="header-title">Face<span>Sorter</span></p>'
        '<p class="header-sub">Scan. Cluster. Deliver. — Event photo sorting at scale.</p>'
        '</div>'
        '<div class="header-stats">'
        '<div class="hstat"><div class="hstat-val">' + photos_val + '</div><div class="hstat-lbl">In Queue</div></div>'
        '<div class="hstat"><div class="hstat-val ' + people_class + '">' + people + '</div><div class="hstat-lbl">Identities</div></div>'
        '<div class="hstat"><div class="hstat-val">' + sorted_count + '</div><div class="hstat-lbl">Sorted</div></div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


def render_workspace_idle(photo_count, input_folder):
    if photo_count == 0:
        status = '<div class="status-chip status-empty">⚠ No photos detected</div>'
        drop_content = (
            '<div class="ws-drop-icon">📂</div>'
            '<p class="ws-drop-title">Input Folder is Empty</p>'
            '<p class="ws-drop-sub">Export your event photos as JPG or TIFF<br>and place them in your input folder.</p>'
            '<div class="ws-path">📁 ' + str(input_folder) + '</div>'
        )
        grid_html = ""
    else:
        status = '<div class="status-chip status-ready">● Ready to Sort</div>'
        slot_html = ""
        show = min(photo_count, 9)
        for i in range(show):
            slot_html += '<div class="ws-photo-slot filled">' + str(i + 1) + '</div>'
        if photo_count > 9:
            slot_html += '<div class="ws-photo-slot">+' + str(photo_count - 9) + '</div>'
        grid_html = '<div class="ws-photo-grid">' + slot_html + '</div>'
        drop_content = (
            '<div class="ws-drop-icon">✅</div>'
            '<p class="ws-drop-title">' + str(photo_count) + ' Photo' + ('s' if photo_count != 1 else '') + ' Ready</p>'
            '<p class="ws-drop-sub">Hit Sort Photos in the sidebar to begin.<br>Estimated time: ' + str(max(1, round(photo_count * 2 / 60))) + '–' + str(max(2, round(photo_count * 4 / 60))) + ' min on Mac.</p>'
            '<div class="ws-path">📁 ' + str(input_folder) + '</div>'
        )

    st.markdown(
        '<div class="workspace">'
        + status +
        '<div style="height:20px;"></div>'
        '<div class="ws-drop-zone">' + drop_content + '</div>'
        + grid_html +
        '</div>'
        '<div class="summary-box">'
        '<p class="summary-title">Quick Start</p>'
        '<p class="summary-body">'
        '1. Export event photos as JPG or TIFF into <code>' + str(input_folder) + '</code><br>'
        '2. Select a processing mode — <strong>Balanced</strong> works for most events<br>'
        '3. Hit <strong>Sort Photos</strong> — each output folder = one Pixieset Set<br>'
        '4. Large events (150–500 people) run in 5–20 min on Mac'
        '</p></div>',
        unsafe_allow_html=True
    )


def render_workspace_running(current_phase, message):
    st.markdown(
        '<div class="workspace">'
        '<div class="status-chip status-running" style="margin-bottom:28px;">⚙ AI Processing</div>'
        + render_step_indicator(current_phase) +
        '<div style="margin-top:20px;font-size:11px;color:#44445A;font-weight:500;letter-spacing:.02em;">'
        + message +
        '</div></div>',
        unsafe_allow_html=True
    )


def render_workspace_results(r):
    st.success("Sort complete — " + str(r["people_found"]) + " identities found across " + str(r["total_photos"]) + " photos.")

    st.markdown(
        '<div class="stat-row">'
        '<div class="stat-card"><div class="stat-icon">🖼️</div><div class="stat-value">' + str(r["total_photos"]) + '</div><div class="stat-label">Scanned</div></div>'
        '<div class="stat-card hl"><div class="stat-icon">👥</div><div class="stat-value blue">' + str(r["people_found"]) + '</div><div class="stat-label">Identities</div></div>'
        '<div class="stat-card"><div class="stat-icon">✓</div><div class="stat-value">' + str(r["photos_sorted"]) + '</div><div class="stat-label">Sorted</div></div>'
        '<div class="stat-card"><div class="stat-icon">○</div><div class="stat-value">' + str(r["unmatched"]) + '</div><div class="stat-label">Unmatched</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    cards_html = (
        '<div class="people-section">'
        '<div class="people-header">'
        '<span class="people-title">People Found</span>'
        '<span class="people-meta">' + str(r["people_found"]) + ' unique identities · sorted by frequency</span>'
        '</div>'
        '<div class="person-grid">'
    )
    for fi in r["person_folders"][:60]:
        cards_html += make_person_card(fi)
    if len(r["person_folders"]) > 60:
        cards_html += '<div class="person-card"><div class="person-placeholder" style="font-size:12px;color:#44445A;">+' + str(len(r["person_folders"]) - 60) + '</div></div>'
    cards_html += '</div></div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    sk = r["skip_counts"]
    st.markdown(
        '<div class="summary-box">'
        '<p class="summary-title">Export Summary</p>'
        '<p class="summary-body">'
        'Output saved to <code>' + r["output_folder"] + '</code><br>'
        'Skipped ' + str(sk.get("size",0)) + ' background · ' + str(sk.get("blur",0)) + ' blurry · ' + str(sk.get("angle",0)) + ' extreme angles<br>'
        'Merge any duplicate person cards before uploading. '
        'Upload each <code>person-XXX</code> folder as a <strong>Set</strong> in Pixieset.'
        '</p></div>',
        unsafe_allow_html=True
    )


def main():
    st.markdown(CSS, unsafe_allow_html=True)

    if "results"       not in st.session_state: st.session_state.results       = None
    if "error"         not in st.session_state: st.session_state.error         = None
    if "running"       not in st.session_state: st.session_state.running       = False
    if "current_phase" not in st.session_state: st.session_state.current_phase = "init"
    if "live_message"  not in st.session_state: st.session_state.live_message  = ""
    if "input_folder"  not in st.session_state: st.session_state.input_folder  = "./input"

    photo_count = count_photos(st.session_state.get("input_folder", "./input"))
    sidebar = render_sidebar(photo_count)

    st.session_state.input_folder = sidebar["config"]["input_folder"]
    photo_count = count_photos(sidebar["config"]["input_folder"])

    render_header(photo_count, st.session_state.results)

    if sidebar["run"]:
        st.session_state.results = None
        st.session_state.error   = None
        st.session_state.running = True
        st.session_state.current_phase = "init"

        progress_bar  = st.progress(0.0)
        workspace_slot = st.empty()

        def step_cb(phase, current, total, message):
            prev = {"init":0.0,"scan":0.02,"cluster":0.65,"write":0.80,"done":1.0}
            high = {"init":0.02,"scan":0.65,"cluster":0.80,"write":1.0,"done":1.0}
            low  = prev.get(phase, 0.0)
            top  = high.get(phase, 1.0)
            frac = low + (current / max(total,1)) * (top - low)
            progress_bar.progress(round(min(frac, 1.0), 3))
            with workspace_slot.container():
                render_workspace_running(phase, message)

        try:
            from face_sorter import run_sort
            results = run_sort(sidebar["config"], step_cb=step_cb)
            st.session_state.results = results
        except Exception as e:
            st.session_state.error = str(e)
        finally:
            st.session_state.running = False
            progress_bar.empty()
            workspace_slot.empty()

    if st.session_state.error:
        st.error("Error: " + st.session_state.error)
        render_workspace_idle(photo_count, sidebar["config"]["input_folder"])
    elif st.session_state.results:
        render_workspace_results(st.session_state.results)
    else:
        render_workspace_idle(photo_count, sidebar["config"]["input_folder"])


if __name__ == "__main__":
    main()
