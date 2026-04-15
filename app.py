"""
app.py - FaceSorter Dashboard
Montserrat typography, light/dark theme by time of day.
Run with: python3 -m streamlit run app.py
"""

import streamlit as st
import base64
from datetime import datetime

st.set_page_config(
    page_title="FaceSorter",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

hour = datetime.now().hour
is_dark = hour >= 18 or hour < 6

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Montserrat', sans-serif !important;
    background-color: #F7F5F0 !important;
    color: #1C1C1C !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.6rem !important; padding-bottom: 3rem !important; }
[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E8E4DC !important; }

.sidebar-brand { display:flex; align-items:center; gap:12px; padding-bottom:18px; margin-bottom:18px; border-bottom:1px solid #EDE9E1; }
.sidebar-brand-icon { width:36px; height:36px; background:#F0EBE0; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px; flex-shrink:0; }
.sidebar-brand-title { font-family:'Montserrat',sans-serif; font-size:16px; font-weight:700; color:#1C1C1C; letter-spacing:-.3px; }
.sidebar-brand-sub { font-size:10px; font-weight:400; color:#9E9890; margin-top:2px; letter-spacing:.02em; }

.section-label { font-family:'Montserrat',sans-serif; font-size:9px; font-weight:700; letter-spacing:.15em; text-transform:uppercase; color:#A09880; margin:16px 0 8px 0; padding-bottom:7px; border-bottom:1px solid #EDE9E1; }

.stTextInput > label { color:#6E6860 !important; font-size:11px !important; font-weight:600 !important; letter-spacing:.04em !important; text-transform:uppercase !important; }
.stTextInput > div > div > input { background:#FAF8F4 !important; border:1px solid #DDD9D0 !important; border-radius:8px !important; color:#1C1C1C !important; font-size:13px !important; font-family:'Montserrat',sans-serif !important; }
.stTextInput > div > div > input:focus { border-color:#C4A882 !important; box-shadow:0 0 0 3px rgba(196,168,130,.12) !important; }

.stSlider > label { color:#6E6860 !important; font-size:11px !important; font-weight:600 !important; letter-spacing:.04em !important; text-transform:uppercase !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] { background-color:#C4A882 !important; border-color:#C4A882 !important; }

.stButton > button { width:100% !important; background:#1C1C1C !important; color:#FFFFFF !important; border:none !important; border-radius:8px !important; font-family:'Montserrat',sans-serif !important; font-weight:600 !important; font-size:12px !important; padding:.7rem 1rem !important; letter-spacing:.08em !important; text-transform:uppercase !important; margin-top:6px !important; }
.stButton > button:hover { background:#3A3530 !important; }
.stButton > button:disabled { background:#D5D0C8 !important; color:#A09880 !important; }

.main-header { background:#FFFFFF; border:1px solid #E8E4DC; border-radius:14px; padding:24px 28px; display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
.main-header-title { font-family:'Montserrat',sans-serif; font-size:28px; font-weight:800; color:#1C1C1C; letter-spacing:-1px; margin:0; }
.main-header-title span { color:#C4A882; }
.main-header-sub { margin:6px 0 0 0; color:#9E9890; font-size:12px; font-weight:400; letter-spacing:.02em; }
.main-header-badge { background:#F5F0E8; border:1px solid #E0D8CB; color:#8A7860; border-radius:20px; padding:5px 14px; font-size:10px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }

.stat-row { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:20px; }
.stat-card { background:#FFFFFF; border:1px solid #E8E4DC; border-radius:12px; padding:20px 16px; text-align:center; }
.stat-card.hl { background:#F9F5EE; border-color:#DDD0B8; }
.stat-icon { font-size:20px; margin-bottom:8px; }
.stat-value { font-family:'Montserrat',sans-serif; font-size:32px; font-weight:700; color:#1C1C1C; line-height:1; margin-bottom:6px; letter-spacing:-1px; }
.stat-value.warm { color:#C4A882; }
.stat-label { font-size:9px; font-weight:700; color:#9E9890; letter-spacing:.12em; text-transform:uppercase; }

.section-card { background:#FFFFFF; border:1px solid #E8E4DC; border-radius:12px; padding:24px 22px; margin-bottom:16px; }
.section-card-title { font-family:'Montserrat',sans-serif; font-size:9px; font-weight:700; letter-spacing:.15em; text-transform:uppercase; color:#A09880; margin:0 0 20px 0; padding-bottom:10px; border-bottom:1px solid #EDE9E1; }

.person-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:24px; margin-top:4px; }
.person-card { display:flex; flex-direction:column; align-items:center; gap:10px; background:transparent; border:none; padding:8px 0; }
.person-thumb { width:110px; height:110px; border-radius:50%; object-fit:cover; display:block; border:3.5px solid #3D4535; }
.person-placeholder { width:110px; height:110px; border-radius:50%; background:#EDE9E1; border:3.5px solid #3D4535; display:flex; align-items:center; justify-content:center; font-size:36px; }
.person-name { font-family:'Montserrat',sans-serif; font-size:11px; font-weight:600; color:#3A3530; text-align:center; line-height:1.3; letter-spacing:.01em; }
.person-badge { font-family:'Montserrat',sans-serif; font-size:9px; font-weight:600; color:#8A7860; background:#EDE8DF; padding:3px 9px; border-radius:10px; letter-spacing:.04em; }

.idle-box { text-align:center; padding:56px 24px; background:#FFFFFF; border:1px solid #E8E4DC; border-radius:14px; margin-bottom:16px; }
.idle-box-icon { font-size:44px; margin-bottom:16px; }
.idle-box-title { font-family:'Montserrat',sans-serif; font-size:20px; font-weight:700; color:#3A3530; margin:0 0 8px 0; letter-spacing:-.3px; }
.idle-box-sub { font-size:13px; font-weight:400; color:#9E9890; margin:0; line-height:1.7; }

.tip-box { background:#F9F5EE; border:1px solid #DDD0B8; border-radius:10px; padding:14px 18px; margin-top:16px; }
.tip-box-title { font-family:'Montserrat',sans-serif; font-size:9px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#8A7860; margin:0 0 8px 0; }
.tip-box-body { font-size:12px; font-weight:400; color:#6E6860; line-height:1.8; margin:0; }
.tip-box-body code { background:#EDE8DF; padding:1px 6px; border-radius:4px; font-size:11px; color:#6A5E4A; font-family:monospace; }

.stProgress > div > div > div > div { background:linear-gradient(90deg,#C4A882,#A88A65) !important; border-radius:4px !important; }
.stProgress > div > div > div { background:#EDE9E1 !important; border-radius:4px !important; }
.theme-badge { font-family:'Montserrat',sans-serif; font-size:10px; font-weight:500; color:#A09880; text-align:center; padding-top:8px; letter-spacing:.04em; }
</style>
"""

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Montserrat', sans-serif !important;
    background-color: #0C1822 !important;
    color: #DFF0F6 !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.6rem !important; padding-bottom: 3rem !important; }
[data-testid="stSidebar"] { background-color: #081017 !important; border-right:1px solid #172D3E !important; }

.sidebar-brand { display:flex; align-items:center; gap:12px; padding-bottom:18px; margin-bottom:18px; border-bottom:1px solid #172D3E; }
.sidebar-brand-icon { width:36px; height:36px; background:rgba(0,196,218,.12); border:1px solid rgba(0,196,218,.25); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px; flex-shrink:0; }
.sidebar-brand-title { font-family:'Montserrat',sans-serif; font-size:16px; font-weight:700; color:#00C4DA; letter-spacing:-.3px; }
.sidebar-brand-sub { font-size:10px; font-weight:400; color:#4A7888; margin-top:2px; letter-spacing:.02em; }

.section-label { font-family:'Montserrat',sans-serif; font-size:9px; font-weight:700; letter-spacing:.15em; text-transform:uppercase; color:#4A7888; margin:16px 0 8px 0; padding-bottom:7px; border-bottom:1px solid #172D3E; }

.stTextInput > label { color:#7AAABB !important; font-size:11px !important; font-weight:600 !important; letter-spacing:.04em !important; text-transform:uppercase !important; }
.stTextInput > div > div > input { background:#0F2030 !important; border:1px solid #173040 !important; border-radius:8px !important; color:#DFF0F6 !important; font-size:13px !important; font-family:'Montserrat',sans-serif !important; }
.stTextInput > div > div > input:focus { border-color:#00C4DA !important; box-shadow:0 0 0 2px rgba(0,196,218,.14) !important; }

.stSlider > label { color:#7AAABB !important; font-size:11px !important; font-weight:600 !important; letter-spacing:.04em !important; text-transform:uppercase !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] { background-color:#00C4DA !important; border-color:#00C4DA !important; }

.stButton > button { width:100% !important; background:linear-gradient(135deg,#00C4DA,#0094AB) !important; color:#fff !important; border:none !important; border-radius:8px !important; font-family:'Montserrat',sans-serif !important; font-weight:600 !important; font-size:12px !important; padding:.7rem 1rem !important; letter-spacing:.08em !important; text-transform:uppercase !important; margin-top:6px !important; }
.stButton > button:hover { background:linear-gradient(135deg,#1AD6EC,#00AECA) !important; }
.stButton > button:disabled { background:#172D3E !important; color:#365060 !important; }

.main-header { background:#0F2030; border:1px solid #172D3E; border-radius:14px; padding:24px 28px; display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
.main-header-title { font-family:'Montserrat',sans-serif; font-size:28px; font-weight:800; color:#DFF0F6; letter-spacing:-1px; margin:0; }
.main-header-title span { color:#00C4DA; }
.main-header-sub { margin:6px 0 0 0; color:#4A7888; font-size:12px; font-weight:400; letter-spacing:.02em; }
.main-header-badge { background:rgba(0,196,218,.12); border:1px solid rgba(0,196,218,.25); color:#00C4DA; border-radius:20px; padding:5px 14px; font-size:10px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }

.stat-row { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:20px; }
.stat-card { background:#0F2030; border:1px solid #172D3E; border-radius:12px; padding:20px 16px; text-align:center; }
.stat-card.hl { background:rgba(0,196,218,.07); border-color:rgba(0,196,218,.4); }
.stat-icon { font-size:20px; margin-bottom:8px; }
.stat-value { font-family:'Montserrat',sans-serif; font-size:32px; font-weight:700; color:#DFF0F6; line-height:1; margin-bottom:6px; letter-spacing:-1px; }
.stat-value.warm { color:#00C4DA; }
.stat-label { font-size:9px; font-weight:700; color:#4A7888; letter-spacing:.12em; text-transform:uppercase; }

.section-card { background:#0F2030; border:1px solid #172D3E; border-radius:12px; padding:24px 22px; margin-bottom:16px; }
.section-card-title { font-family:'Montserrat',sans-serif; font-size:9px; font-weight:700; letter-spacing:.15em; text-transform:uppercase; color:#4A7888; margin:0 0 20px 0; padding-bottom:10px; border-bottom:1px solid #172D3E; }

.person-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:24px; margin-top:4px; }
.person-card { display:flex; flex-direction:column; align-items:center; gap:10px; background:transparent; border:none; padding:8px 0; }
.person-thumb { width:110px; height:110px; border-radius:50%; object-fit:cover; display:block; border:3.5px solid #00C4DA; }
.person-placeholder { width:110px; height:110px; border-radius:50%; background:#0F2030; border:3.5px solid #00C4DA; display:flex; align-items:center; justify-content:center; font-size:36px; }
.person-name { font-family:'Montserrat',sans-serif; font-size:11px; font-weight:600; color:#BCDCE8; text-align:center; line-height:1.3; letter-spacing:.01em; }
.person-badge { font-family:'Montserrat',sans-serif; font-size:9px; font-weight:600; color:#00C4DA; background:rgba(0,196,218,.1); padding:3px 9px; border-radius:10px; letter-spacing:.04em; }

.idle-box { text-align:center; padding:56px 24px; background:#0F2030; border:1px solid #172D3E; border-radius:14px; margin-bottom:16px; }
.idle-box-icon { font-size:44px; margin-bottom:16px; }
.idle-box-title { font-family:'Montserrat',sans-serif; font-size:20px; font-weight:700; color:#DFF0F6; margin:0 0 8px 0; letter-spacing:-.3px; }
.idle-box-sub { font-size:13px; font-weight:400; color:#4A7888; margin:0; line-height:1.7; }

.tip-box { background:rgba(0,196,218,.06); border:1px solid rgba(0,196,218,.2); border-radius:10px; padding:14px 18px; margin-top:16px; }
.tip-box-title { font-family:'Montserrat',sans-serif; font-size:9px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#00C4DA; margin:0 0 8px 0; }
.tip-box-body { font-size:12px; font-weight:400; color:#7AAABB; line-height:1.8; margin:0; }
.tip-box-body code { background:rgba(0,196,218,.12); padding:1px 6px; border-radius:4px; font-size:11px; color:#00C4DA; font-family:monospace; }

.stProgress > div > div > div > div { background:linear-gradient(90deg,#00C4DA,#0094AB) !important; border-radius:4px !important; }
.stProgress > div > div > div { background:#172D3E !important; border-radius:4px !important; }
.theme-badge { font-family:'Montserrat',sans-serif; font-size:10px; font-weight:500; color:#4A7888; text-align:center; padding-top:8px; letter-spacing:.04em; }
</style>
"""


def thumbnail_to_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


def make_person_card(folder_info):
    name = folder_info["name"]
    count = folder_info["count"]
    thumb_path = folder_info.get("thumbnail")
    label = str(count) + (" photos" if count != 1 else " photo")
    b64 = thumbnail_to_b64(thumb_path) if thumb_path else None
    card = '<div class="person-card">'
    if b64:
        card += '<img class="person-thumb" src="data:image/jpeg;base64,' + b64 + '" alt="' + name + '">'
    else:
        card += '<div class="person-placeholder">👤</div>'
    card += '<div class="person-name">' + name + "</div>"
    card += '<div class="person-badge">' + label + "</div>"
    card += "</div>"
    return card


def render_sidebar():
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

        st.markdown('<div class="section-label">Folders</div>', unsafe_allow_html=True)
        input_folder = st.text_input("Input folder", value="./input")
        output_folder = st.text_input("Output folder", value="./output")

        st.markdown('<div class="section-label">Face Detection</div>', unsafe_allow_html=True)
        min_face_size = st.slider("Min face size", 0.01, 0.15, 0.04, 0.01, format="%.2f",
                                  help="Fraction of image width. Raise to exclude background people.")
        min_confidence = st.slider("Min confidence", 0.30, 0.95, 0.55, 0.05, format="%.2f",
                                   help="Lower catches more faces including candids.")
        min_sharpness = st.slider("Min sharpness", 10, 150, 45,
                                  help="Lower = more blur-tolerant. Good for candid shots.")

        st.markdown('<div class="section-label">Pose & Candid Angles</div>', unsafe_allow_html=True)
        max_yaw = st.slider("Max yaw (°)", 15, 90, 60, help="Left/right head turn. 60+ is candid-friendly.")
        max_pitch = st.slider("Max pitch (°)", 15, 80, 45, help="Up/down tilt.")

        st.markdown('<div class="section-label">Clustering</div>', unsafe_allow_html=True)
        dbscan_eps = st.slider("Matching strictness", 0.25, 0.70, 0.45, 0.05, format="%.2f",
                               help="Lower = stricter. Raise if same person splits into two folders.")
        min_samples = st.slider("Min photos for folder", 1, 10, 2,
                                help="Person must appear in this many photos to get a folder.")

        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("Sort Photos", disabled=st.session_state.get("running", False))

        theme_label = "🌙 Night mode" if is_dark else "☀️ Day mode"
        st.markdown('<div class="theme-badge">' + theme_label + '</div>', unsafe_allow_html=True)

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


def render_results(r):
    st.success("Sort complete — " + str(r["people_found"]) + " people found across " + str(r["total_photos"]) + " photos.")

    st.markdown(
        '<div class="stat-row">'
        '<div class="stat-card"><div class="stat-icon">🖼️</div><div class="stat-value">' + str(r["total_photos"]) + '</div><div class="stat-label">Photos scanned</div></div>'
        '<div class="stat-card hl"><div class="stat-icon">👥</div><div class="stat-value warm">' + str(r["people_found"]) + '</div><div class="stat-label">People found</div></div>'
        '<div class="stat-card"><div class="stat-icon">✓</div><div class="stat-value">' + str(r["photos_sorted"]) + '</div><div class="stat-label">Photos sorted</div></div>'
        '<div class="stat-card"><div class="stat-icon">○</div><div class="stat-value">' + str(r["unmatched"]) + '</div><div class="stat-label">Unmatched</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    cards_html = '<div class="section-card"><div class="section-card-title">People Found</div><div class="person-grid">'
    for folder_info in r["person_folders"][:60]:
        cards_html += make_person_card(folder_info)
    if len(r["person_folders"]) > 60:
        extra = len(r["person_folders"]) - 60
        cards_html += '<div class="person-card"><div class="person-placeholder" style="font-size:12px;">+' + str(extra) + ' more</div></div>'
    cards_html += "</div></div>"
    st.markdown(cards_html, unsafe_allow_html=True)

    sk = r["skip_counts"]
    st.markdown(
        '<div class="tip-box">'
        '<p class="tip-box-title">Summary & Next Steps</p>'
        '<p class="tip-box-body">'
        "Output saved to <code>" + r["output_folder"] + "</code><br>"
        "Skipped " + str(sk.get("size", 0)) + " background &nbsp;·&nbsp; "
        + str(sk.get("blur", 0)) + " blurry &nbsp;·&nbsp; "
        + str(sk.get("angle", 0)) + " extreme angles &nbsp;·&nbsp; "
        + str(sk.get("confidence", 0)) + " low confidence<br>"
        "If the same person appears in two cards, merge their folders before uploading.<br>"
        "Upload each <code>person-XXX</code> folder as a <strong>Set</strong> inside your Pixieset Collection."
        "</p></div>",
        unsafe_allow_html=True
    )


def render_idle():
    st.markdown(
        '<div class="idle-box">'
        '<div class="idle-box-icon">📷</div>'
        '<p class="idle-box-title">Ready to Sort</p>'
        '<p class="idle-box-sub">Set your input folder path in the sidebar,<br>adjust filters if needed, then click Sort Photos.</p>'
        "</div>"
        '<div class="tip-box">'
        '<p class="tip-box-title">Quick Start</p>'
        '<p class="tip-box-body">'
        "1. Export your event photos as JPG or TIFF into the <code>input/</code> folder<br>"
        "2. Leave all settings at defaults for your first run<br>"
        "3. Large events (150–500 people) typically take 5–20 min on Mac<br>"
        "4. Each output folder becomes a <strong>Set</strong> in your Pixieset Collection"
        "</p></div>",
        unsafe_allow_html=True
    )


def main():
    st.markdown(DARK_CSS if is_dark else LIGHT_CSS, unsafe_allow_html=True)

    if "results" not in st.session_state:
        st.session_state.results = None
    if "error" not in st.session_state:
        st.session_state.error = None
    if "running" not in st.session_state:
        st.session_state.running = False

    sidebar = render_sidebar()

    st.markdown(
        '<div class="main-header">'
        "<div>"
        '<p class="main-header-title">Face<span>Sorter</span></p>'
        '<p class="main-header-sub">AI-powered event photo organizer — sort once, deliver fast</p>'
        "</div>"
        '<div class="main-header-badge">InsightFace · buffalo_l</div>'
        "</div>",
        unsafe_allow_html=True
    )

    if sidebar["run"]:
        st.session_state.results = None
        st.session_state.error = None
        st.session_state.running = True

        progress_bar = st.progress(0.0)
        status_text = st.empty()

        def step_cb(phase, current, total, message):
            prev = {"init": 0.0, "scan": 0.02, "cluster": 0.65, "write": 0.80}
            high = {"init": 0.02, "scan": 0.65, "cluster": 0.80, "write": 1.0}
            low = prev.get(phase, 0.0)
            top = high.get(phase, 1.0)
            frac = low + (current / max(total, 1)) * (top - low)
            progress_bar.progress(round(min(frac, 1.0), 3))
            status_text.markdown(
                "<p style='color:#A09880;font-size:12px;margin-top:4px;font-family:Montserrat,sans-serif;'>⏳ " + message + "</p>",
                unsafe_allow_html=True
            )

        try:
            from face_sorter import run_sort
            results = run_sort(sidebar["config"], step_cb=step_cb)
            st.session_state.results = results
        except Exception as e:
            st.session_state.error = str(e)
        finally:
            st.session_state.running = False
            progress_bar.empty()
            status_text.empty()

    if st.session_state.error:
        st.error("Error: " + st.session_state.error)
        render_idle()
    elif st.session_state.results:
        render_results(st.session_state.results)
    else:
        render_idle()


if __name__ == "__main__":
    main()
