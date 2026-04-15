"""
app.py - FaceSorter Dashboard
Topaz Labs inspired: cinematic dark premium SaaS aesthetic.
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

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"], .stApp {
    font-family: 'Montserrat', sans-serif !important;
    background-color: #111113 !important;
    color: #F2F2F7 !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #1C1C1F !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .block-container { padding-top: 0 !important; }

.sb-logo {
    display: flex; align-items: center; gap: 12px;
    padding: 24px 20px 20px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 8px;
}
.sb-logo-icon {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, #4E94FF, #2D6FD6);
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; flex-shrink: 0;
}
.sb-logo-title {
    font-size: 15px; font-weight: 700; color: #F2F2F7;
    letter-spacing: -.2px;
}
.sb-logo-sub { font-size: 10px; font-weight: 400; color: #636366; margin-top: 1px; }

.sb-section {
    font-size: 9px; font-weight: 700; letter-spacing: .14em;
    text-transform: uppercase; color: #48484A;
    padding: 16px 20px 6px 20px;
}

/* Streamlit input overrides */
.stTextInput > label {
    color: #636366 !important; font-size: 10px !important;
    font-weight: 700 !important; letter-spacing: .1em !important;
    text-transform: uppercase !important;
}
.stTextInput > div > div > input {
    background: #2C2C2F !important; border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; color: #F2F2F7 !important;
    font-size: 12px !important; font-family: 'Montserrat', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4E94FF !important;
    box-shadow: 0 0 0 3px rgba(78,148,255,0.15) !important;
}

.stSlider > label {
    color: #636366 !important; font-size: 10px !important;
    font-weight: 700 !important; letter-spacing: .1em !important;
    text-transform: uppercase !important;
}
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: #4E94FF !important; border-color: #4E94FF !important;
}
.stSlider [data-baseweb="slider"] [data-testid="stTickBar"] div {
    background-color: #4E94FF !important;
}

/* Sort button */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #4E94FF, #2D6FD6) !important;
    color: #FFFFFF !important; border: none !important;
    border-radius: 12px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important; font-size: 12px !important;
    padding: .75rem 1rem !important; letter-spacing: .08em !important;
    text-transform: uppercase !important; margin-top: 8px !important;
    box-shadow: 0 4px 20px rgba(78,148,255,0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6AABFF, #4282F0) !important;
    box-shadow: 0 6px 24px rgba(78,148,255,0.45) !important;
}
.stButton > button:disabled {
    background: #2C2C2F !important; color: #48484A !important;
    box-shadow: none !important;
}

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
    border-radius: 24px;
    padding: 36px 40px;
    margin: 20px 0 20px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(78,148,255,0.18) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-title {
    font-size: 36px; font-weight: 800; color: #F2F2F7;
    letter-spacing: -1.5px; margin: 0; line-height: 1;
}
.hero-title span { color: #4E94FF; }
.hero-sub {
    font-size: 13px; font-weight: 400; color: #8E8E93;
    margin: 8px 0 0 0; letter-spacing: .01em;
}
.hero-badge {
    background: rgba(78,148,255,0.15);
    border: 1px solid rgba(78,148,255,0.3);
    color: #4E94FF; border-radius: 20px;
    padding: 6px 16px; font-size: 10px;
    font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
}

/* ── Stat cards ── */
.stat-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 20px; }
.stat-card {
    background: #1C1C1F;
    border-radius: 18px;
    padding: 20px 18px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.05);
}
.stat-card.hl {
    background: linear-gradient(135deg, #1A2540, #1A2D50);
    border-color: rgba(78,148,255,0.25);
}
.stat-icon { font-size: 22px; margin-bottom: 8px; }
.stat-value {
    font-size: 32px; font-weight: 800; color: #F2F2F7;
    line-height: 1; margin-bottom: 6px; letter-spacing: -1px;
}
.stat-value.blue { color: #4E94FF; }
.stat-label {
    font-size: 9px; font-weight: 700; color: #48484A;
    letter-spacing: .14em; text-transform: uppercase;
}

/* ── Section block ── */
.section-block {
    background: #1C1C1F;
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 16px;
    border: 1px solid rgba(255,255,255,0.05);
}
.section-block-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px; padding-bottom: 14px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.section-block-title {
    font-size: 14px; font-weight: 700; color: #F2F2F7; letter-spacing: -.2px;
}
.section-block-sub {
    font-size: 11px; font-weight: 400; color: #48484A;
}

/* ── Person cards ── */
.person-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 16px;
}
.person-card {
    background: #242428;
    border-radius: 20px;
    overflow: hidden;
    display: flex; flex-direction: column; align-items: center;
    padding-bottom: 16px;
    border: 1px solid rgba(255,255,255,0.05);
    transition: border-color .2s;
}
.person-card:hover { border-color: rgba(78,148,255,0.4); }
.person-img-wrap {
    width: 100%; padding: 20px 0 14px 0;
    display: flex; justify-content: center;
}
.person-thumb {
    width: 88px; height: 88px;
    border-radius: 50%;
    object-fit: cover;
    border: 2.5px solid #4E94FF;
    display: block;
}
.person-placeholder {
    width: 88px; height: 88px;
    border-radius: 50%;
    background: #2C2C2F;
    border: 2.5px solid #4E94FF;
    display: flex; align-items: center; justify-content: center;
    font-size: 30px;
}
.person-name {
    font-size: 11px; font-weight: 600; color: #F2F2F7;
    text-align: center; letter-spacing: .01em;
    padding: 0 12px; margin-bottom: 6px;
}
.person-badge {
    font-size: 9px; font-weight: 700; color: #4E94FF;
    background: rgba(78,148,255,0.12);
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: .06em; text-transform: uppercase;
}

/* ── Idle / Ready state ── */
.idle-hero {
    background: linear-gradient(135deg, #1A1A2E, #111113);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 24px;
    padding: 64px 40px;
    text-align: center;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}
.idle-hero::before {
    content: '';
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(78,148,255,0.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.idle-icon { font-size: 52px; margin-bottom: 18px; }
.idle-title {
    font-size: 24px; font-weight: 800; color: #F2F2F7;
    margin: 0 0 10px 0; letter-spacing: -.5px;
}
.idle-sub { font-size: 13px; font-weight: 400; color: #636366; margin: 0; line-height: 1.7; }

/* ── Tip box ── */
.tip-box {
    background: rgba(78,148,255,0.07);
    border: 1px solid rgba(78,148,255,0.18);
    border-radius: 14px; padding: 16px 20px; margin-top: 16px;
}
.tip-title {
    font-size: 9px; font-weight: 700; letter-spacing: .14em;
    text-transform: uppercase; color: #4E94FF; margin: 0 0 8px 0;
}
.tip-body { font-size: 12px; font-weight: 400; color: #8E8E93; line-height: 1.8; margin: 0; }
.tip-body code {
    background: rgba(78,148,255,0.15); padding: 1px 6px;
    border-radius: 4px; font-size: 11px; color: #4E94FF; font-family: monospace;
}
.tip-body strong { color: #C8D8FF; font-weight: 600; }

/* ── Progress ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #4E94FF, #2D6FD6) !important;
    border-radius: 4px !important;
}
.stProgress > div > div > div {
    background: #2C2C2F !important; border-radius: 4px !important;
}

/* ── Success / Error ── */
div[data-testid="stSuccessMessage"] {
    background: rgba(52,199,89,0.1) !important;
    border-color: rgba(52,199,89,0.3) !important;
    border-radius: 12px !important;
    color: #34C759 !important;
}
div[data-testid="stErrorMessage"] {
    background: rgba(255,69,58,0.1) !important;
    border-color: rgba(255,69,58,0.3) !important;
    border-radius: 12px !important;
}

.theme-badge {
    font-size: 10px; font-weight: 500; color: #48484A;
    text-align: center; padding-top: 10px; letter-spacing: .04em;
}
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
    card += '<div class="person-img-wrap">'
    if b64:
        card += '<img class="person-thumb" src="data:image/jpeg;base64,' + b64 + '" alt="' + name + '">'
    else:
        card += '<div class="person-placeholder">👤</div>'
    card += '</div>'
    card += '<div class="person-name">' + name + "</div>"
    card += '<div class="person-badge">' + label + "</div>"
    card += "</div>"
    return card


def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div class="sb-logo">
                <div class="sb-logo-icon">📸</div>
                <div>
                    <div class="sb-logo-title">FaceSorter</div>
                    <div class="sb-logo-sub">InsightFace · buffalo_l</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sb-section">Folders</div>', unsafe_allow_html=True)
        input_folder = st.text_input("Input folder", value="./input")
        output_folder = st.text_input("Output folder", value="./output")

        st.markdown('<div class="sb-section">Face Detection</div>', unsafe_allow_html=True)
        min_face_size = st.slider("Min face size", 0.01, 0.15, 0.04, 0.01, format="%.2f",
                                  help="Fraction of image width. Raise to exclude background people.")
        min_confidence = st.slider("Min confidence", 0.30, 0.95, 0.55, 0.05, format="%.2f",
                                   help="Lower catches more faces including candids.")
        min_sharpness = st.slider("Min sharpness", 10, 150, 45,
                                  help="Lower = more blur-tolerant. Good for candid shots.")

        st.markdown('<div class="sb-section">Pose & Candid</div>', unsafe_allow_html=True)
        max_yaw = st.slider("Max yaw (°)", 15, 90, 60, help="Left/right head turn. 60+ is candid-friendly.")
        max_pitch = st.slider("Max pitch (°)", 15, 80, 45, help="Up/down tilt.")

        st.markdown('<div class="sb-section">Clustering</div>', unsafe_allow_html=True)
        dbscan_eps = st.slider("Matching strictness", 0.25, 0.70, 0.45, 0.05, format="%.2f",
                               help="Lower = stricter. Raise if same person splits into two folders.")
        min_samples = st.slider("Min photos for folder", 1, 10, 2,
                                help="Person must appear in this many photos to get a folder.")

        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("Sort Photos", disabled=st.session_state.get("running", False))

        hour = datetime.now().hour
        is_dark = hour >= 18 or hour < 6
        theme_label = "🌙 Night mode active" if is_dark else "☀️ Day mode active"
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
        '<div class="stat-card"><div class="stat-icon">🖼️</div><div class="stat-value">' + str(r["total_photos"]) + '</div><div class="stat-label">Photos Scanned</div></div>'
        '<div class="stat-card hl"><div class="stat-icon">👥</div><div class="stat-value blue">' + str(r["people_found"]) + '</div><div class="stat-label">People Found</div></div>'
        '<div class="stat-card"><div class="stat-icon">✓</div><div class="stat-value">' + str(r["photos_sorted"]) + '</div><div class="stat-label">Photos Sorted</div></div>'
        '<div class="stat-card"><div class="stat-icon">○</div><div class="stat-value">' + str(r["unmatched"]) + '</div><div class="stat-label">Unmatched</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    sk = r["skip_counts"]
    cards_html = (
        '<div class="section-block">'
        '<div class="section-block-header">'
        '<span class="section-block-title">People Found</span>'
        '<span class="section-block-sub">' + str(r["people_found"]) + ' unique identities detected</span>'
        '</div>'
        '<div class="person-grid">'
    )
    for folder_info in r["person_folders"][:60]:
        cards_html += make_person_card(folder_info)
    if len(r["person_folders"]) > 60:
        extra = len(r["person_folders"]) - 60
        cards_html += '<div class="person-card"><div class="person-img-wrap"><div class="person-placeholder" style="font-size:13px;color:#636366;">+' + str(extra) + '</div></div></div>'
    cards_html += "</div></div>"
    st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown(
        '<div class="tip-box">'
        '<p class="tip-title">Summary & Next Steps</p>'
        '<p class="tip-body">'
        "Output saved to <code>" + r["output_folder"] + "</code> &nbsp;·&nbsp; "
        "Skipped " + str(sk.get("size", 0)) + " background · "
        + str(sk.get("blur", 0)) + " blurry · "
        + str(sk.get("angle", 0)) + " extreme angles<br>"
        "If the same person appears in two cards, <strong>merge their folders</strong> before uploading. "
        "Upload each <code>person-XXX</code> folder as a <strong>Set</strong> inside your Pixieset Collection."
        "</p></div>",
        unsafe_allow_html=True
    )


def render_idle():
    st.markdown(
        '<div class="idle-hero">'
        '<div class="idle-icon">📷</div>'
        '<p class="idle-title">Ready to Sort</p>'
        '<p class="idle-sub">Drop your event photos into the <code style="background:rgba(78,148,255,0.15);padding:2px 7px;border-radius:5px;color:#4E94FF;font-size:12px;">input/</code> folder,<br>configure your settings in the sidebar, then hit Sort Photos.</p>'
        "</div>"
        '<div class="tip-box">'
        '<p class="tip-title">Quick Start</p>'
        '<p class="tip-body">'
        "1. Export your event photos as JPG or TIFF into the <code>input/</code> folder<br>"
        "2. Leave all settings at defaults for your first run<br>"
        "3. Large events (150–500 people) typically take 5–20 min on Mac<br>"
        "4. Each output folder = one <strong>Set</strong> in your Pixieset Collection"
        "</p></div>",
        unsafe_allow_html=True
    )


def main():
    st.markdown(CSS, unsafe_allow_html=True)

    if "results" not in st.session_state:
        st.session_state.results = None
    if "error" not in st.session_state:
        st.session_state.error = None
    if "running" not in st.session_state:
        st.session_state.running = False

    sidebar = render_sidebar()

    st.markdown(
        '<div class="hero">'
        "<div>"
        '<p class="hero-title">Face<span>Sorter</span></p>'
        '<p class="hero-sub">AI-powered event photo organizer — sort once, deliver fast</p>'
        "</div>"
        '<div class="hero-badge">InsightFace · buffalo_l</div>'
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
                "<p style='color:#636366;font-size:12px;margin-top:6px;font-family:Montserrat,sans-serif;letter-spacing:.02em;'>⏳ " + message + "</p>",
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
