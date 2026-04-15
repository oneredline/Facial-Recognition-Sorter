"""
app.py - FaceSorter
Premium AI workflow command center.
Run with: python3 -m streamlit run app.py
"""

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

PRESETS = {
    "Fast Pass": {"min_face_size_ratio":0.06,"min_confidence":0.65,"min_sharpness":65,"max_yaw_angle":45,"max_pitch_angle":35,"dbscan_eps":0.40,"dbscan_min_samples":2,
                  "desc":"Subjects only. Fastest run, strictest matching. Best for formal events."},
    "Balanced":  {"min_face_size_ratio":0.04,"min_confidence":0.55,"min_sharpness":45,"max_yaw_angle":60,"max_pitch_angle":45,"dbscan_eps":0.45,"dbscan_min_samples":2,
                  "desc":"Recommended for most events. Balances speed, coverage, and accuracy."},
    "Precision": {"min_face_size_ratio":0.025,"min_confidence":0.45,"min_sharpness":25,"max_yaw_angle":75,"max_pitch_angle":60,"dbscan_eps":0.52,"dbscan_min_samples":2,
                  "desc":"Candid-heavy shoots. Wider angle tolerance, more inclusive detection."},
    "Custom":    {"desc":"Manually tune all detection and clustering parameters."},
}

STEPS = [
    ("init",    "Loading AI Model",   "Initializing InsightFace buffalo_l"),
    ("scan",    "Scanning Faces",     "Detecting and encoding faces in every photo"),
    ("cluster", "Clustering Guests",  "Grouping faces into identity sets"),
    ("write",   "Building Galleries", "Copying photos into person folders"),
    ("done",    "Export Complete",    "All galleries ready for Pixieset upload"),
]

SUPPORTED = {'.jpg','.jpeg','.tiff','.tif'}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');

html,body,[class*="css"],.stApp {
    font-family:'Montserrat',sans-serif !important;
    background-color:#0C0C10 !important;
    color:#E8E8F0 !important;
}
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:2rem !important; max-width:100% !important; }

[data-testid="stSidebar"] {
    background:#111118 !important;
    border-right:1px solid rgba(255,255,255,0.05) !important;
}

.sb-top { padding:22px 18px 16px; border-bottom:1px solid rgba(255,255,255,0.05); }
.sb-logo { display:flex; align-items:center; gap:10px; margin-bottom:0; }
.sb-icon { width:36px; height:36px; border-radius:10px; background:linear-gradient(135deg,#4F8EF7,#7C60EB); display:flex; align-items:center; justify-content:center; font-size:17px; flex-shrink:0; }
.sb-name { font-size:15px; font-weight:800; color:#E8E8F0; letter-spacing:-.3px; }
.sb-sub  { font-size:9px;  font-weight:600; color:#2E2E40; letter-spacing:.14em; text-transform:uppercase; margin-top:2px; }

.sb-section { font-size:9px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:#2A2A3C; padding:14px 18px 5px; }

.stSelectbox > label { display:none !important; }
.stSelectbox > div > div { background:#191924 !important; border:1px solid rgba(255,255,255,0.08) !important; border-radius:10px !important; color:#E8E8F0 !important; font-family:'Montserrat',sans-serif !important; font-size:12px !important; font-weight:600 !important; }
.stSelectbox > div > div:focus-within { border-color:rgba(79,142,247,0.5) !important; box-shadow:0 0 0 3px rgba(79,142,247,0.1) !important; }

.preset-chip { margin:6px 0 10px; background:rgba(79,142,247,0.07); border:1px solid rgba(79,142,247,0.14); border-radius:9px; padding:8px 12px; font-size:10px; font-weight:400; color:#4A4A66; line-height:1.5; }
.preset-chip b { color:#6E9EFF; font-weight:600; }

.stTextInput > label { color:#3A3A52 !important; font-size:9px !important; font-weight:700 !important; letter-spacing:.12em !important; text-transform:uppercase !important; }
.stTextInput > div > div > input { background:#191924 !important; border:1px solid rgba(255,255,255,0.07) !important; border-radius:9px !important; color:#E8E8F0 !important; font-size:12px !important; font-family:'Montserrat',sans-serif !important; padding:8px 11px !important; }
.stTextInput > div > div > input:focus { border-color:rgba(79,142,247,0.5) !important; box-shadow:0 0 0 3px rgba(79,142,247,0.1) !important; }

.stSlider > label { color:#3A3A52 !important; font-size:9px !important; font-weight:700 !important; letter-spacing:.12em !important; text-transform:uppercase !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] { background:#4F8EF7 !important; border-color:#4F8EF7 !important; width:13px !important; height:13px !important; box-shadow:0 0 0 4px rgba(79,142,247,0.18) !important; }
.microcopy { font-size:10px; color:#333348; line-height:1.5; margin:-2px 0 10px; padding:0 2px; }

.stButton > button {
    width:100% !important; background:linear-gradient(135deg,#4F8EF7,#7C60EB) !important;
    color:#fff !important; border:none !important; border-radius:12px !important;
    font-family:'Montserrat',sans-serif !important; font-weight:700 !important;
    font-size:11px !important; padding:.8rem !important; letter-spacing:.1em !important;
    text-transform:uppercase !important; margin-top:6px !important;
    box-shadow:0 4px 22px rgba(79,142,247,0.3) !important;
}
.stButton > button:hover { box-shadow:0 6px 30px rgba(79,142,247,0.48) !important; }
.stButton > button:disabled { background:#191924 !important; color:#252535 !important; box-shadow:none !important; }

/* Header */
.page-header {
    background:linear-gradient(135deg,#0F1128 0%,#0C1838 55%,#0C0C10 100%);
    border-radius:20px; padding:26px 32px; margin:16px 0 14px;
    display:flex; align-items:center; justify-content:space-between;
    border:1px solid rgba(79,142,247,0.1); position:relative; overflow:hidden;
}
.page-header::after { content:''; position:absolute; top:-90px; right:-90px; width:340px; height:340px; background:radial-gradient(circle,rgba(79,142,247,0.12) 0%,transparent 65%); border-radius:50%; pointer-events:none; }
.h-eyebrow { font-size:9px; font-weight:700; letter-spacing:.2em; text-transform:uppercase; color:#4F8EF7; margin-bottom:6px; }
.h-title   { font-size:30px; font-weight:800; color:#E8E8F0; letter-spacing:-1.3px; margin:0; line-height:1; }
.h-title span { color:#4F8EF7; }
.h-sub     { font-size:12px; font-weight:400; color:#3A3A52; margin:6px 0 0; }
.h-stats   { display:flex; gap:10px; z-index:1; }
.hstat { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:10px 16px; text-align:center; min-width:86px; }
.hstat-val { font-size:20px; font-weight:800; color:#E8E8F0; letter-spacing:-.5px; line-height:1; }
.hstat-val.blue { color:#4F8EF7; }
.hstat-sub { font-size:9px; font-weight:600; color:#252535; text-transform:uppercase; letter-spacing:.1em; margin-top:3px; }

/* Workspace */
.ws-card { background:#0F0F18; border:1px solid rgba(255,255,255,0.05); border-radius:20px; padding:0; margin-bottom:12px; overflow:hidden; }

/* Mode strip */
.mode-strip { background:rgba(79,142,247,0.06); border-bottom:1px solid rgba(79,142,247,0.1); padding:12px 22px; display:flex; align-items:center; gap:10px; }
.mode-pill { background:rgba(79,142,247,0.14); border:1px solid rgba(79,142,247,0.3); color:#6E9EFF; border-radius:20px; padding:3px 12px; font-size:10px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; }
.mode-desc { font-size:11px; color:#3A3A52; font-weight:400; }

/* Ready state content */
.ws-body { padding:28px 26px 24px; }
.ws-headline { font-size:22px; font-weight:800; color:#E8E8F0; letter-spacing:-.5px; margin:0 0 6px; }
.ws-headline span { color:#4F8EF7; }
.ws-tagline { font-size:12px; color:#4A4A66; margin:0 0 24px; line-height:1.6; font-weight:400; }

/* Pipeline */
.pipeline { display:flex; align-items:center; gap:0; margin-bottom:22px; }
.pipe-step { display:flex; flex-direction:column; align-items:center; gap:5px; flex:1; }
.pipe-icon { width:42px; height:42px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:18px; border:1.5px solid rgba(255,255,255,0.07); background:#191924; }
.pipe-icon.done { background:rgba(52,199,89,0.1); border-color:rgba(52,199,89,0.3); }
.pipe-icon.active { background:rgba(79,142,247,0.12); border-color:rgba(79,142,247,0.35); box-shadow:0 0 12px rgba(79,142,247,0.2); }
.pipe-label { font-size:9px; font-weight:700; color:#2E2E40; letter-spacing:.08em; text-transform:uppercase; text-align:center; }
.pipe-label.done { color:#34C759; }
.pipe-label.active { color:#4F8EF7; }
.pipe-arrow { font-size:14px; color:#1E1E28; padding:0 4px; margin-top:-16px; }

/* Output preview */
.output-preview { background:#13131E; border:1px solid rgba(255,255,255,0.05); border-radius:14px; padding:14px 18px; margin-bottom:20px; }
.op-label { font-size:9px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:#2E2E40; margin-bottom:10px; }
.op-row   { display:flex; align-items:center; gap:10px; }
.op-card  { background:#1C1C28; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:8px 12px; display:flex; align-items:center; gap:8px; }
.op-avatar { width:28px; height:28px; border-radius:50%; background:rgba(79,142,247,0.15); border:1.5px solid rgba(79,142,247,0.3); display:flex; align-items:center; justify-content:center; font-size:13px; flex-shrink:0; }
.op-info  { font-size:10px; }
.op-name  { font-weight:700; color:#9090A8; }
.op-count { font-size:9px; color:#2E2E40; font-weight:500; margin-top:1px; }
.op-more  { font-size:11px; color:#2A2A3A; font-weight:600; padding:0 6px; }
.op-arrow { font-size:11px; color:#252535; margin:0 4px; }

/* Main CTA area */
.cta-area { display:flex; flex-direction:column; gap:8px; }
.trust-row { display:flex; align-items:center; justify-content:center; gap:16px; flex-wrap:wrap; }
.trust-item { font-size:10px; font-weight:500; color:#2C2C3E; display:flex; align-items:center; gap:5px; }
.trust-item span { color:#3A3A52; }

/* Empty onboarding */
.checklist { padding:28px 26px 24px; }
.cl-title  { font-size:13px; font-weight:700; color:#E8E8F0; margin:0 0 18px; letter-spacing:-.1px; }
.cl-item   { display:flex; align-items:flex-start; gap:12px; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.04); }
.cl-item:last-child { border-bottom:none; }
.cl-dot    { width:22px; height:22px; border-radius:50%; border:2px solid #1E1E28; background:#111118; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:700; color:#252535; flex-shrink:0; margin-top:1px; }
.cl-dot.done   { background:rgba(52,199,89,0.12); border-color:rgba(52,199,89,0.4); color:#34C759; }
.cl-dot.active { background:rgba(79,142,247,0.12); border-color:rgba(79,142,247,0.4); color:#4F8EF7; }
.cl-text   { flex:1; }
.cl-step   { font-size:12px; font-weight:600; color:#3A3A52; }
.cl-step.done   { color:#34C759; }
.cl-step.active { color:#E8E8F0; }
.cl-hint   { font-size:10px; color:#252535; margin-top:2px; line-height:1.5; font-weight:400; }
.cl-hint.active { color:#3A3A52; }

/* Output preview in empty state */
.after-preview { background:#13131E; border:1px solid rgba(255,255,255,0.05); border-radius:14px; padding:16px 18px; margin:18px 0 0; }
.ap-label { font-size:9px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:#2A2A3A; margin-bottom:12px; }
.ap-grid  { display:flex; gap:8px; }
.ap-card  { flex:1; background:#191924; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:12px 10px; display:flex; flex-direction:column; align-items:center; gap:6px; }
.ap-circle { width:36px; height:36px; border-radius:50%; background:rgba(79,142,247,0.1); border:1.5px solid rgba(79,142,247,0.25); display:flex; align-items:center; justify-content:center; font-size:14px; }
.ap-name  { font-size:9px; font-weight:600; color:#2E2E40; }
.ap-cnt   { font-size:8px; color:#1E1E28; }
.ap-more  { font-size:11px; color:#1E1E28; font-weight:600; align-self:center; padding:0 6px; }
.ap-note  { font-size:10px; color:#2A2A3A; margin-top:8px; line-height:1.5; font-weight:400; }

/* Running */
.ws-running { padding:40px 26px; display:flex; flex-direction:column; align-items:center; }
.step-panel { width:100%; max-width:500px; }
.step-row { display:flex; align-items:flex-start; gap:13px; padding:8px 0; position:relative; }
.step-row:not(:last-child)::after { content:''; position:absolute; left:13px; top:30px; width:2px; height:calc(100% - 4px); background:rgba(255,255,255,0.04); }
.step-dot { width:26px; height:26px; border-radius:50%; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:700; z-index:1; border:2px solid rgba(255,255,255,0.06); background:#191924; color:#252535; }
.step-dot.active { border-color:#4F8EF7; background:rgba(79,142,247,0.14); color:#4F8EF7; box-shadow:0 0 12px rgba(79,142,247,0.3); }
.step-dot.done   { border-color:rgba(52,199,89,0.4); background:rgba(52,199,89,0.1); color:#34C759; }
.step-name { font-size:12px; font-weight:700; color:#252535; padding-top:3px; }
.step-name.active { color:#E8E8F0; }
.step-name.done   { color:#34C759; }
.step-desc { font-size:10px; color:#1E1E28; margin-top:2px; }
.step-desc.active { color:#3A3A52; }

/* Results */
.stat-row { display:grid; grid-template-columns:repeat(4,1fr); gap:11px; margin-bottom:14px; }
.stat-card { background:#111118; border:1px solid rgba(255,255,255,0.05); border-radius:15px; padding:16px 13px; text-align:center; }
.stat-card.hl { background:linear-gradient(135deg,#0F0F28,#0C1838); border-color:rgba(79,142,247,0.18); }
.sc-icon { font-size:18px; margin-bottom:6px; }
.sc-val  { font-size:28px; font-weight:800; color:#E8E8F0; line-height:1; margin-bottom:4px; letter-spacing:-1px; }
.sc-val.blue { color:#4F8EF7; }
.sc-lbl  { font-size:8px; font-weight:700; color:#252535; letter-spacing:.14em; text-transform:uppercase; }

.people-block { background:#0F0F18; border:1px solid rgba(255,255,255,0.05); border-radius:20px; padding:20px; margin-bottom:12px; }
.pb-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid rgba(255,255,255,0.04); }
.pb-title  { font-size:13px; font-weight:700; color:#E8E8F0; }
.pb-meta   { font-size:10px; color:#252535; }
.person-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(120px,1fr)); gap:10px; }
.person-card { background:#141420; border:1px solid rgba(255,255,255,0.05); border-radius:16px; display:flex; flex-direction:column; align-items:center; padding:16px 10px 12px; }
.person-card:hover { border-color:rgba(79,142,247,0.3); }
.person-thumb { width:72px; height:72px; border-radius:50%; object-fit:cover; border:2.5px solid #4F8EF7; margin-bottom:9px; box-shadow:0 0 0 4px rgba(79,142,247,0.08); }
.person-placeholder { width:72px; height:72px; border-radius:50%; background:#191924; border:2.5px solid rgba(79,142,247,0.3); display:flex; align-items:center; justify-content:center; font-size:26px; margin-bottom:9px; }
.p-name  { font-size:10px; font-weight:600; color:#E8E8F0; text-align:center; margin-bottom:4px; }
.p-badge { font-size:8px; font-weight:700; color:#4F8EF7; background:rgba(79,142,247,0.1); padding:2px 8px; border-radius:20px; letter-spacing:.08em; text-transform:uppercase; }

.sum-box { background:rgba(79,142,247,0.05); border:1px solid rgba(79,142,247,0.1); border-radius:13px; padding:14px 18px; margin-top:12px; }
.sum-title { font-size:9px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:#4F8EF7; margin:0 0 7px; }
.sum-body  { font-size:11px; color:#3A3A52; line-height:1.8; margin:0; }
.sum-body code { background:rgba(79,142,247,0.12); padding:1px 6px; border-radius:4px; font-size:10px; color:#4F8EF7; font-family:monospace; }
.sum-body strong { color:#7A9EFF; font-weight:600; }

.status-chip { display:inline-flex; align-items:center; gap:6px; border-radius:20px; padding:4px 12px; font-size:9px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.s-ready   { background:rgba(52,199,89,0.1);  color:#34C759; border:1px solid rgba(52,199,89,0.22); }
.s-empty   { background:rgba(255,214,10,0.08); color:#FFD60A; border:1px solid rgba(255,214,10,0.18); }
.s-running { background:rgba(79,142,247,0.1);  color:#4F8EF7; border:1px solid rgba(79,142,247,0.28); }

.stProgress > div > div > div > div { background:linear-gradient(90deg,#4F8EF7,#7C60EB) !important; border-radius:3px !important; }
.stProgress > div > div > div { background:#191924 !important; border-radius:3px !important; }
div[data-testid="stSuccessMessage"] { background:rgba(52,199,89,0.08) !important; border-color:rgba(52,199,89,0.22) !important; border-radius:11px !important; color:#34C759 !important; }
div[data-testid="stErrorMessage"]   { background:rgba(255,69,58,0.08) !important; border-color:rgba(255,69,58,0.22) !important; border-radius:11px !important; }
.sb-footer { font-size:9px; color:#1E1E28; text-align:center; padding:10px 0 2px; letter-spacing:.06em; font-weight:500; }
</style>
"""


def thumbnail_to_b64(path):
    try:
        with open(path,"rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


def count_photos(folder_str):
    try:
        p = Path(folder_str)
        if not p.exists():
            return 0
        return sum(1 for f in p.rglob('*') if f.suffix.lower() in SUPPORTED)
    except Exception:
        return 0


def make_person_card(fi):
    name = fi["name"]; count = fi["count"]
    label = str(count) + (" photos" if count != 1 else " photo")
    b64 = thumbnail_to_b64(fi.get("thumbnail")) if fi.get("thumbnail") else None
    card = '<div class="person-card">'
    card += ('<img class="person-thumb" src="data:image/jpeg;base64,' + b64 + '" alt="' + name + '">'
             if b64 else '<div class="person-placeholder">👤</div>')
    card += '<div class="p-name">' + name + '</div>'
    card += '<div class="p-badge">' + label + '</div>'
    return card + '</div>'


def render_steps(phase):
    order = ["init","scan","cluster","write","done"]
    try:    idx = order.index(phase)
    except: idx = 0
    html = '<div class="step-panel">'
    for i,(ph,name,desc) in enumerate(STEPS):
        if i < idx:    dc,nc,ic = "done","done","✓"
        elif i == idx: dc,nc,ic = "active","active","●"
        else:          dc,nc,ic = "","",str(i+1)
        html += ('<div class="step-row"><div class="step-dot ' + dc + '">' + ic + '</div>'
                 '<div><div class="step-name ' + nc + '">' + name + '</div>'
                 '<div class="step-desc ' + ("active" if i==idx else "") + '">' + desc + '</div></div></div>')
    return html + '</div>'


def render_sidebar(photo_count):
    with st.sidebar:
        st.markdown("""
            <div class="sb-top">
                <div class="sb-logo">
                    <div class="sb-icon">📸</div>
                    <div><div class="sb-name">FaceSorter</div><div class="sb-sub">Event Face Intelligence</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="sb-section">Processing Mode</span>', unsafe_allow_html=True)
        mode = st.selectbox("mode", list(PRESETS.keys()), index=1, label_visibility="collapsed")
        p = PRESETS[mode] if mode != "Custom" else PRESETS["Balanced"]
        st.markdown('<div class="preset-chip"><b>' + mode + '</b> — ' + PRESETS[mode]["desc"] + '</div>', unsafe_allow_html=True)

        st.markdown('<span class="sb-section">Folders</span>', unsafe_allow_html=True)
        input_folder  = st.text_input("Input folder",  value="./input")
        output_folder = st.text_input("Output folder", value="./output")

        if mode == "Custom":
            st.markdown('<span class="sb-section">Face Detection</span>', unsafe_allow_html=True)
            min_face_size  = st.slider("Min Face Size",  0.01,0.15,float(p["min_face_size_ratio"]),0.01,format="%.2f")
            st.markdown('<div class="microcopy">Ignore tiny background faces. Lower for wide crowd shots.</div>', unsafe_allow_html=True)
            min_confidence = st.slider("Min Confidence", 0.30,0.95,float(p["min_confidence"]),0.05,format="%.2f")
            st.markdown('<div class="microcopy">Raise for cleaner matches. Lower for more detection.</div>', unsafe_allow_html=True)
            min_sharpness  = st.slider("Min Sharpness",  10,150,int(p["min_sharpness"]))
            st.markdown('<div class="microcopy">Lower tolerates motion blur — good for candid events.</div>', unsafe_allow_html=True)
            st.markdown('<span class="sb-section">Pose & Candid</span>', unsafe_allow_html=True)
            max_yaw   = st.slider("Max Yaw (°)",   15,90,int(p["max_yaw_angle"]))
            st.markdown('<div class="microcopy">Left/right head turn. Raise for candid-heavy shoots.</div>', unsafe_allow_html=True)
            max_pitch = st.slider("Max Pitch (°)", 15,80,int(p["max_pitch_angle"]))
            st.markdown('<span class="sb-section">Clustering</span>', unsafe_allow_html=True)
            dbscan_eps  = st.slider("Matching Strictness",  0.25,0.70,float(p["dbscan_eps"]),0.05,format="%.2f")
            st.markdown('<div class="microcopy">Higher = fewer false matches. Lower = broader grouping.</div>', unsafe_allow_html=True)
            min_samples = st.slider("Min Photos for Folder",1,10,int(p["dbscan_min_samples"]))
            st.markdown('<div class="microcopy">Minimum appearances to create a person folder.</div>', unsafe_allow_html=True)
        else:
            min_face_size=float(p["min_face_size_ratio"]); min_confidence=float(p["min_confidence"])
            min_sharpness=int(p["min_sharpness"]); max_yaw=int(p["max_yaw_angle"])
            max_pitch=int(p["max_pitch_angle"]); dbscan_eps=float(p["dbscan_eps"]); min_samples=int(p["dbscan_min_samples"])

        st.markdown("<br>", unsafe_allow_html=True)
        disabled = st.session_state.get("running",False) or photo_count == 0
        run_sb = st.button("Sort Photos" if photo_count > 0 else "Add Photos First", disabled=disabled, key="sort_sb")
        hour = datetime.now().hour
        st.markdown('<div class="sb-footer">' + ("🌙 Night" if hour>=18 or hour<6 else "☀️ Day") + ' · FaceSorter v2</div>', unsafe_allow_html=True)

    return {
        "run_sb": run_sb,
        "config": {
            "input_folder":input_folder, "output_folder":output_folder,
            "min_face_size_ratio":min_face_size, "min_confidence":min_confidence,
            "min_sharpness":float(min_sharpness), "max_yaw_angle":float(max_yaw),
            "max_pitch_angle":float(max_pitch), "dbscan_eps":dbscan_eps,
            "dbscan_min_samples":min_samples,
        },
        "mode": mode,
        "mode_desc": PRESETS[mode]["desc"],
    }


def render_header(photo_count, results):
    ppl_val = str(results["people_found"]) if results else "0"
    srt_val = str(results["photos_sorted"]) if results else "0"
    ppl_sub = "Identities" if results else "Pending Scan"
    srt_sub = "Sorted" if results else "Not Started"
    q_val   = str(photo_count)
    bc = "blue" if results else ""
    st.markdown(
        '<div class="page-header"><div style="z-index:1">'
        '<div class="h-eyebrow">AI Face Intelligence · InsightFace buffalo_l</div>'
        '<p class="h-title">Face<span>Sorter</span></p>'
        '<p class="h-sub">Scan. Cluster. Deliver. — Event photo sorting at scale.</p>'
        '</div><div class="h-stats">'
        '<div class="hstat"><div class="hstat-val">' + q_val + '</div><div class="hstat-sub">In Queue</div></div>'
        '<div class="hstat"><div class="hstat-val ' + bc + '">' + ppl_val + '</div><div class="hstat-sub">' + ppl_sub + '</div></div>'
        '<div class="hstat"><div class="hstat-val">' + srt_val + '</div><div class="hstat-sub">' + srt_sub + '</div></div>'
        '</div></div>',
        unsafe_allow_html=True
    )


def render_ready(photo_count, mode, mode_desc, output_folder):
    est_lo = max(1, round(photo_count * 2 / 60))
    est_hi = max(2, round(photo_count * 4 / 60))
    est_ids_lo = max(1, round(photo_count * 0.08))
    est_ids_hi = max(2, round(photo_count * 0.18))

    st.markdown(
        '<div class="ws-card">'
        '<div class="mode-strip">'
        '<div class="mode-pill">' + mode + '</div>'
        '<div class="mode-desc">' + mode_desc + '</div>'
        '</div>'
        '<div class="ws-body">'
        '<p class="ws-headline"><span>' + str(photo_count) + ' photos</span> loaded and ready</p>'
        '<p class="ws-tagline">' + mode + ' mode will sort these into identity groups in approximately ' + str(est_lo) + '–' + str(est_hi) + ' min.<br>'
        'Expected output: ' + str(est_ids_lo) + '–' + str(est_ids_hi) + ' identity sets → ready to upload as Pixieset Sets.</p>'
        '<div class="pipeline">'
        '<div class="pipe-step"><div class="pipe-icon done">📁</div><div class="pipe-label done">Loaded</div></div>'
        '<div class="pipe-arrow">→</div>'
        '<div class="pipe-step"><div class="pipe-icon active">👁</div><div class="pipe-label active">Scan</div></div>'
        '<div class="pipe-arrow">→</div>'
        '<div class="pipe-step"><div class="pipe-icon">🧩</div><div class="pipe-label">Cluster</div></div>'
        '<div class="pipe-arrow">→</div>'
        '<div class="pipe-step"><div class="pipe-icon">📤</div><div class="pipe-label">Export</div></div>'
        '</div>'
        '<div class="output-preview">'
        '<div class="op-label">Output preview — one folder per identity</div>'
        '<div class="op-row">'
        '<div class="op-card"><div class="op-avatar">👤</div><div class="op-info"><div class="op-name">person-001</div><div class="op-count">~12 photos</div></div></div>'
        '<div class="op-arrow">·</div>'
        '<div class="op-card"><div class="op-avatar">👤</div><div class="op-info"><div class="op-name">person-002</div><div class="op-count">~8 photos</div></div></div>'
        '<div class="op-arrow">·</div>'
        '<div class="op-card"><div class="op-avatar">👤</div><div class="op-info"><div class="op-name">person-003</div><div class="op-count">~6 photos</div></div></div>'
        '<div class="op-more">+ ' + str(est_ids_lo) + '–' + str(est_ids_hi) + ' more</div>'
        '</div></div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    run_main = st.button("Sort Photos", key="sort_main")

    st.markdown(
        '<div class="trust-row" style="display:flex;gap:16px;flex-wrap:wrap;justify-content:center;margin:8px 0 4px;">'
        '<div class="trust-item">🔒 <span>Originals are never modified</span></div>'
        '<div class="trust-item">📁 <span>Output written to ' + str(output_folder) + '</span></div>'
        '<div class="trust-item">🖼 <span>Best for JPG &amp; TIFF exports</span></div>'
        '</div>',
        unsafe_allow_html=True
    )
    return run_main


def render_empty(photo_count, input_folder, mode):
    steps_html = ""
    items = [
        (photo_count > 0, "Add photos to input folder",
         "Export your event photos as JPG or TIFF into <code style='font-size:10px;color:#3A3A52;'>" + str(input_folder) + "</code>"),
        (True,  "Select processing mode",
         "<b style='color:#6E9EFF'>" + mode + "</b> selected — change it in the sidebar if needed"),
        (False, "Sort Photos",
         "Hit Sort Photos once your input folder is loaded"),
    ]
    for done, title, hint in items:
        dc = "done" if done else ("active" if not done and (photo_count > 0 or title != "Add photos to input folder") else "")
        icon = "✓" if done else ("1" if title.startswith("Add") else ("2" if title.startswith("Select") else "3"))
        steps_html += (
            '<div class="cl-item">'
            '<div class="cl-dot ' + dc + '">' + icon + '</div>'
            '<div class="cl-text">'
            '<div class="cl-step ' + ("done" if done else "") + '">' + title + '</div>'
            '<div class="cl-hint ' + ("active" if not done else "") + '">' + hint + '</div>'
            '</div></div>'
        )

    st.markdown(
        '<div class="ws-card">'
        '<div class="checklist">'
        '<div class="cl-title">Setup checklist</div>'
        + steps_html +
        '<div class="after-preview">'
        '<div class="ap-label">What FaceSorter creates — one folder per identity</div>'
        '<div class="ap-grid">'
        '<div class="ap-card"><div class="ap-circle">👤</div><div class="ap-name">person-001</div><div class="ap-cnt">N photos</div></div>'
        '<div class="ap-card"><div class="ap-circle">👤</div><div class="ap-name">person-002</div><div class="ap-cnt">N photos</div></div>'
        '<div class="ap-card"><div class="ap-circle">👤</div><div class="ap-name">person-003</div><div class="ap-cnt">N photos</div></div>'
        '<div class="ap-more">+ more</div>'
        '</div>'
        '<div class="ap-note">Each folder uploads as a Set inside your Pixieset Collection. Clients browse to their own Set and download directly.</div>'
        '</div>'
        '</div></div>',
        unsafe_allow_html=True
    )


def render_running(phase, message):
    st.markdown(
        '<div class="ws-card"><div class="ws-running">'
        '<div class="status-chip s-running" style="margin-bottom:24px;">⚙ AI Processing</div>'
        + render_steps(phase) +
        '<div style="margin-top:16px;font-size:11px;color:#252535;font-weight:500;letter-spacing:.02em;">' + message + '</div>'
        '</div></div>',
        unsafe_allow_html=True
    )


def render_results(r):
    st.success("Sort complete — " + str(r["people_found"]) + " identities found across " + str(r["total_photos"]) + " photos.")
    st.markdown(
        '<div class="stat-row">'
        '<div class="stat-card"><div class="sc-icon">🖼️</div><div class="sc-val">' + str(r["total_photos"]) + '</div><div class="sc-lbl">Scanned</div></div>'
        '<div class="stat-card hl"><div class="sc-icon">👥</div><div class="sc-val blue">' + str(r["people_found"]) + '</div><div class="sc-lbl">Identities</div></div>'
        '<div class="stat-card"><div class="sc-icon">✓</div><div class="sc-val">' + str(r["photos_sorted"]) + '</div><div class="sc-lbl">Sorted</div></div>'
        '<div class="stat-card"><div class="sc-icon">○</div><div class="sc-val">' + str(r["unmatched"]) + '</div><div class="sc-lbl">Unmatched</div></div>'
        '</div>',
        unsafe_allow_html=True
    )
    cards = (
        '<div class="people-block">'
        '<div class="pb-header"><span class="pb-title">People Found</span>'
        '<span class="pb-meta">' + str(r["people_found"]) + ' unique identities · sorted by frequency</span></div>'
        '<div class="person-grid">'
    )
    for fi in r["person_folders"][:60]:
        cards += make_person_card(fi)
    if len(r["person_folders"]) > 60:
        cards += '<div class="person-card"><div class="person-placeholder" style="font-size:11px;color:#252535;">+' + str(len(r["person_folders"])-60) + '</div></div>'
    cards += '</div></div>'
    st.markdown(cards, unsafe_allow_html=True)
    sk = r["skip_counts"]
    st.markdown(
        '<div class="sum-box"><p class="sum-title">Export Summary</p>'
        '<p class="sum-body">Output saved to <code>' + r["output_folder"] + '</code> · '
        'Skipped ' + str(sk.get("size",0)) + ' background · ' + str(sk.get("blur",0)) + ' blurry · ' + str(sk.get("angle",0)) + ' extreme angles<br>'
        'Merge any duplicate cards before uploading. Upload each <code>person-XXX</code> folder as a <strong>Set</strong> in your Pixieset Collection.'
        '</p></div>',
        unsafe_allow_html=True
    )


def main():
    st.markdown(CSS, unsafe_allow_html=True)

    for k,v in [("results",None),("error",None),("running",False)]:
        if k not in st.session_state:
            st.session_state[k] = v

    photo_count = count_photos("./input")
    sidebar     = render_sidebar(photo_count)
    input_folder  = sidebar["config"]["input_folder"]
    output_folder = sidebar["config"]["output_folder"]
    photo_count   = count_photos(input_folder)

    render_header(photo_count, st.session_state.results)

    run_main = False

    if st.session_state.running:
        pbar = st.progress(0.0)
        slot = st.empty()
        def step_cb(phase,current,total,message):
            prev={"init":0.0,"scan":0.02,"cluster":0.65,"write":0.80,"done":1.0}
            high={"init":0.02,"scan":0.65,"cluster":0.80,"write":1.0,"done":1.0}
            low=prev.get(phase,0.0); top=high.get(phase,1.0)
            pbar.progress(round(min(low+(current/max(total,1))*(top-low),1.0),3))
            with slot.container(): render_running(phase,message)
        try:
            from face_sorter import run_sort
            st.session_state.results = run_sort(sidebar["config"],step_cb=step_cb)
        except Exception as e:
            st.session_state.error = str(e)
        finally:
            st.session_state.running = False
            pbar.empty(); slot.empty()

    elif st.session_state.error:
        st.error("Error: " + st.session_state.error)
        render_empty(photo_count, input_folder, sidebar["mode"])

    elif st.session_state.results:
        render_results(st.session_state.results)

    elif photo_count > 0:
        run_main = render_ready(photo_count, sidebar["mode"], sidebar["mode_desc"], output_folder)

    else:
        render_empty(photo_count, input_folder, sidebar["mode"])

    if (sidebar["run_sb"] or run_main) and not st.session_state.get("running",False):
        st.session_state.results = None
        st.session_state.error   = None
        st.session_state.running = True
        st.rerun()


if __name__ == "__main__":
    main()
