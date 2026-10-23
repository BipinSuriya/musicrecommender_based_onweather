import importlib
import re
from urllib.parse import quote_plus
import streamlit as st

# Optional geolocation support with dynamic import and safety shielding
streamlit_geolocation = None
HAS_GEOLOCATION = False
try:
    _geo_mod = importlib.import_module("streamlit_geolocation")
    streamlit_geolocation = getattr(_geo_mod, "streamlit_geolocation", None)
    HAS_GEOLOCATION = callable(streamlit_geolocation)
except Exception:
    streamlit_geolocation = None
    HAS_GEOLOCATION = False

from main import (
    get_weather_and_time,
    get_dynamic_music_recommendations,
    get_weather_vibe_summary,
    reverse_geocode_city,
    get_current_location,
)

# --- Safe HTML Renderer (Prevents Markdown Code Fence Formatting) ------
def render_html(html_str):
    """Safely render HTML in Streamlit without Markdown interpreting indentation as code fences."""
    cleaned = re.sub(r"\s+", " ", html_str).strip()
    st.markdown(cleaned, unsafe_allow_html=True)

# --- Streamlit Page Configuration -------------------------------------
st.set_page_config(
    page_title="Weather Beats — Soundtracks of the Sky",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Official Streaming Icon SVGs -------------------------------------
APPLE_MUSIC_ICON_SVG = (
    '<svg class="stream-icon" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<rect width="100" height="100" rx="22" fill="#FC3C44"/>'
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M69.5 24.5C69.5 23.4 68.6 22.5 67.5 22.7L37.5 28.7C36.6 28.9 36 29.7 36 30.6V63.5C33.8 62.6 31 62.5 28.5 63.5C23.8 65.4 21 70 22.2 74.5C23.4 79 28.2 81.6 32.9 79.7C37 78.1 39.8 74.3 39.8 70.3V41.5L65.5 36.4V57.5C63.3 56.6 60.5 56.5 58 57.5C53.3 59.4 50.5 64 51.7 68.5C52.9 73 57.7 75.6 62.4 73.7C66.5 72.1 69.3 68.3 69.5 64.3V24.5Z" fill="white"/>'
    '</svg>'
)

SPOTIFY_ICON_SVG = (
    '<svg class="stream-icon" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="50" cy="50" r="50" fill="#1DB954"/>'
    '<path d="M72.5 45.4C58 36.8 34 36 20.1 40.2C17.9 40.9 15.5 39.6 14.8 37.4C14.1 35.2 15.4 32.8 17.6 32.1C33.6 27.2 60.1 28.2 76.8 38.1C78.8 39.3 79.4 41.9 78.2 43.9C77.1 45.8 74.5 46.5 72.5 45.4ZM72 59.8C71 61.3 69.1 61.8 67.6 60.8C55.4 53.3 36.5 51.1 22 55.5C20.3 56 18.5 55.1 18 53.4C17.5 51.7 18.4 49.9 20.1 49.4C36.7 44.4 57.6 46.8 71.3 55.3C72.8 56.2 73.2 58.2 72 59.8ZM66.4 73.6C65.6 74.8 64 75.2 62.8 74.4C52.3 68 39 66.5 22.9 70.2C21.5 70.5 20.2 69.6 19.9 68.2C19.6 66.8 20.5 65.5 21.9 65.2C39.5 61.2 54.2 62.9 65.8 70C67 70.7 67.3 72.3 66.4 73.6Z" fill="#121212"/>'
    '</svg>'
)

YOUTUBE_ICON_SVG = (
    '<svg class="stream-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" fill="#FF0000"/>'
    '</svg>'
)

# --- Helper URL Builders ----------------------------------------------
def spotify_search_url(title, artist):
    query = quote_plus(f"{title} {artist}")
    return f"https://open.spotify.com/search/{query}"

def youtube_search_url(title, artist):
    query = quote_plus(f"{title} {artist} official audio")
    return f"https://www.youtube.com/results?search_query={query}"

# --- Caching Wrappers -------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def cached_weather(city_name):
    return get_weather_and_time(city_name)

@st.cache_data(ttl=600, show_spinner=False)
def cached_recommendations(condition, time_of_day, temp, genre, count, seed_offset):
    mock_weather = {
        "condition": condition,
        "time_of_day": time_of_day,
        "temperature": temp,
    }
    return get_dynamic_music_recommendations(
        mock_weather, genre=genre, count=count, seed_offset=seed_offset
    )

# --- State Initialization & Callback Handlers -------------------------
if "city" not in st.session_state:
    st.session_state.city = "London"
if "city_input_box" not in st.session_state:
    st.session_state.city_input_box = st.session_state.city
if "seed_offset" not in st.session_state:
    st.session_state.seed_offset = 0
if "location_toast" not in st.session_state:
    st.session_state.location_toast = None
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

def set_city_callback(new_city):
    """Callback triggered before script run: safely updates city state without widget key collisions."""
    clean_city = new_city.strip()
    st.session_state.city = clean_city
    st.session_state.city_input_box = clean_city

def on_city_input_change():
    """Callback triggered when user types and enters a city into the text input."""
    typed = st.session_state.city_input_box.strip()
    if typed:
        st.session_state.city = typed

def auto_detect_callback():
    """Callback triggered by auto-detect button: detects city via multi-provider IP and sets state."""
    detected = get_current_location()
    if detected:
        set_city_callback(detected)
        st.session_state.location_toast = f"📍 Sky synchronized with {detected}!"
    else:
        st.session_state.location_toast = "⚠️ Could not auto-detect location. Please type your city name."

def toggle_theme_callback():
    """Callback to switch between Dark and Light mode."""
    st.session_state.theme_mode = "light" if st.session_state.theme_mode == "dark" else "dark"
    mode_name = "☀️ Daylight Light Mode" if st.session_state.theme_mode == "light" else "🌙 Luxury Dark Mode"
    st.session_state.location_toast = f"Switched to {mode_name}"

def shuffle_callback():
    """Callback for discovery shuffler."""
    st.session_state.seed_offset += 1

# Display any pending toasts from callbacks
if st.session_state.location_toast:
    st.toast(st.session_state.location_toast, icon="🌦️")
    st.session_state.location_toast = None

# --- Ambient Weather Theme Gradients (Dark vs Light) ------------------
THEME_GRADIENTS_DARK = {
    "sunny": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(245, 158, 11, 0.24) 0%, rgba(217, 119, 6, 0.08) 50%, rgba(8, 12, 21, 0) 100%), "
        "linear-gradient(180deg, #0d121f 0%, #080c15 100%)"
    ),
    "night": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(99, 102, 241, 0.28) 0%, rgba(79, 70, 229, 0.10) 50%, rgba(8, 12, 21, 0) 100%), "
        "linear-gradient(180deg, #090e1c 0%, #060912 100%)"
    ),
    "rain": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(14, 165, 233, 0.25) 0%, rgba(56, 189, 248, 0.09) 50%, rgba(8, 12, 21, 0) 100%), "
        "linear-gradient(180deg, #08111f 0%, #070c16 100%)"
    ),
    "rain-night": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(20, 184, 166, 0.22) 0%, rgba(15, 118, 110, 0.09) 50%, rgba(8, 12, 21, 0) 100%), "
        "linear-gradient(180deg, #07121b 0%, #050a10 100%)"
    ),
    "clouds": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(148, 163, 184, 0.22) 0%, rgba(100, 116, 139, 0.09) 50%, rgba(8, 12, 21, 0) 100%), "
        "linear-gradient(180deg, #0d121c 0%, #080c14 100%)"
    ),
    "snow": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(186, 230, 253, 0.26) 0%, rgba(125, 211, 252, 0.10) 50%, rgba(8, 12, 21, 0) 100%), "
        "linear-gradient(180deg, #0a1322 0%, #070c16 100%)"
    ),
    "storm": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(168, 85, 247, 0.30) 0%, rgba(126, 34, 206, 0.14) 50%, rgba(8, 12, 21, 0) 100%), "
        "linear-gradient(180deg, #100b1d 0%, #08060f 100%)"
    ),
    "mist": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(192, 132, 252, 0.22) 0%, rgba(147, 51, 234, 0.09) 50%, rgba(8, 12, 21, 0) 100%), "
        "linear-gradient(180deg, #0f0f1c 0%, #080812 100%)"
    ),
}

THEME_GRADIENTS_LIGHT = {
    "sunny": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(251, 191, 36, 0.32) 0%, rgba(245, 158, 11, 0.10) 50%, rgba(248, 250, 252, 0) 100%), "
        "linear-gradient(180deg, #FFFDF7 0%, #F1F5F9 100%)"
    ),
    "night": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(99, 102, 241, 0.22) 0%, rgba(129, 140, 248, 0.08) 50%, rgba(241, 245, 249, 0) 100%), "
        "linear-gradient(180deg, #EEF2FF 0%, #E2E8F0 100%)"
    ),
    "rain": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(14, 165, 233, 0.24) 0%, rgba(56, 189, 248, 0.09) 50%, rgba(241, 245, 249, 0) 100%), "
        "linear-gradient(180deg, #F0F9FF 0%, #E2E8F0 100%)"
    ),
    "rain-night": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(20, 184, 166, 0.20) 0%, rgba(15, 118, 110, 0.08) 50%, rgba(241, 245, 249, 0) 100%), "
        "linear-gradient(180deg, #F0FDFA 0%, #E2E8F0 100%)"
    ),
    "clouds": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(148, 163, 184, 0.24) 0%, rgba(100, 116, 139, 0.08) 50%, rgba(241, 245, 249, 0) 100%), "
        "linear-gradient(180deg, #F8FAFC 0%, #E2E8F0 100%)"
    ),
    "snow": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(186, 230, 253, 0.32) 0%, rgba(125, 211, 252, 0.12) 50%, rgba(241, 245, 249, 0) 100%), "
        "linear-gradient(180deg, #F8FAFC 0%, #E0F2FE 100%)"
    ),
    "storm": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(168, 85, 247, 0.24) 0%, rgba(126, 34, 206, 0.10) 50%, rgba(241, 245, 249, 0) 100%), "
        "linear-gradient(180deg, #FAF5FF 0%, #EDE9FE 100%)"
    ),
    "mist": (
        "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(192, 132, 252, 0.22) 0%, rgba(147, 51, 234, 0.08) 50%, rgba(241, 245, 249, 0) 100%), "
        "linear-gradient(180deg, #FAF5FF 0%, #E2E8F0 100%)"
    ),
}

is_dark = (st.session_state.theme_mode == "dark")

# --- Dynamic CSS Variables (Dark Luxury vs Apple-Grade Light Frosted) --
if is_dark:
    CSS_VARIABLES = """
    :root {
        --bg-app: #080C15;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --card-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.015) 100%);
        --card-border: rgba(255, 255, 255, 0.09);
        --card-hover-border: rgba(99, 102, 241, 0.45);
        --card-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.45);
        --hero-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.015) 100%);
        --hero-border: rgba(255, 255, 255, 0.12);
        --badge-chip-bg: rgba(255, 255, 255, 0.07);
        --badge-chip-border: rgba(255, 255, 255, 0.12);
        --badge-chip-text: #E2E8F0;
        --metric-tile-bg: rgba(255, 255, 255, 0.04);
        --metric-tile-border: rgba(255, 255, 255, 0.08);
        --sidebar-bg: #0b101c;
        --sidebar-border: rgba(255, 255, 255, 0.07);
        --input-bg: rgba(255, 255, 255, 0.05);
        --input-border: rgba(255, 255, 255, 0.12);
        --input-text: #F8FAFC;
        --btn-bg: rgba(255, 255, 255, 0.05);
        --btn-border: rgba(255, 255, 255, 0.12);
        --btn-text: #F8FAFC;
        --stream-btn-bg: rgba(255, 255, 255, 0.05);
        --stream-btn-border: rgba(255, 255, 255, 0.1);
        --stream-btn-text: #FFFFFF;
        --brand-title-grad: linear-gradient(135deg, #FFFFFF 30%, #A5B4FC 100%);
        --audio-filter: invert(0.92) hue-rotate(180deg) brightness(1.15);
        --status-pill-bg: rgba(16, 185, 129, 0.1);
        --status-pill-border: rgba(16, 185, 129, 0.3);
        --status-pill-text: #6EE7B7;
        --header-border: rgba(255, 255, 255, 0.08);
        --theme-toggle-bg: rgba(255, 255, 255, 0.06);
        --theme-toggle-border: rgba(255, 255, 255, 0.14);
        --theme-toggle-text: #F8FAFC;
    }
    """
else:
    CSS_VARIABLES = """
    :root {
        --bg-app: #F8FAFC;
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --text-muted: #64748B;
        --card-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.90) 0%, rgba(255, 255, 255, 0.75) 100%);
        --card-border: rgba(226, 232, 240, 0.95);
        --card-hover-border: rgba(99, 102, 241, 0.6);
        --card-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.06), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
        --hero-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(255, 255, 255, 0.80) 100%);
        --hero-border: rgba(226, 232, 240, 0.95);
        --badge-chip-bg: rgba(241, 245, 249, 0.95);
        --badge-chip-border: rgba(203, 213, 225, 0.8);
        --badge-chip-text: #1E293B;
        --metric-tile-bg: rgba(255, 255, 255, 0.9);
        --metric-tile-border: rgba(226, 232, 240, 0.95);
        --sidebar-bg: #FFFFFF;
        --sidebar-border: rgba(226, 232, 240, 0.85);
        --input-bg: #FFFFFF;
        --input-border: #CBD5E1;
        --input-text: #0F172A;
        --btn-bg: #FFFFFF;
        --btn-border: #CBD5E1;
        --btn-text: #0F172A;
        --stream-btn-bg: #F8FAFC;
        --stream-btn-border: #E2E8F0;
        --stream-btn-text: #0F172A;
        --brand-title-grad: linear-gradient(135deg, #1E1B4B 20%, #4338CA 100%);
        --audio-filter: none;
        --status-pill-bg: rgba(16, 185, 129, 0.12);
        --status-pill-border: rgba(16, 185, 129, 0.4);
        --status-pill-text: #065F46;
        --header-border: rgba(226, 232, 240, 0.8);
        --theme-toggle-bg: #FFFFFF;
        --theme-toggle-border: #CBD5E1;
        --theme-toggle-text: #0F172A;
    }
    """

# --- Premium Global CSS Design System ---------------------------------
CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@500;600&display=swap');

{CSS_VARIABLES}

html, body, [class*="css"], .stApp {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-primary) !important;
    background-color: var(--bg-app) !important;
}}

h1, h2, h3, h4, .outfit-font {{
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: -0.02em;
    color: var(--text-primary) !important;
}}

/* Custom scrollbars */
::-webkit-scrollbar {{
    width: 7px;
    height: 7px;
}}
::-webkit-scrollbar-track {{
    background: rgba(0, 0, 0, 0.05);
}}
::-webkit-scrollbar-thumb {{
    background: rgba(148, 163, 184, 0.4);
    border-radius: 999px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: rgba(99, 102, 241, 0.6);
}}

/* Hide unneeded Streamlit top decorative bar */
header[data-testid="stHeader"] {{
    background: transparent !important;
}}

/* Sidebar styling */
section[data-testid="stSidebar"] {{
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-border) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15) !important;
}}

section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {{
    background: var(--input-bg) !important;
    border: 1px solid var(--input-border) !important;
    border-radius: 12px !important;
    color: var(--input-text) !important;
}}

section[data-testid="stSidebar"] .stTextInput input:focus {{
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
}}

/* Audio Wave Visualizer Animation */
.sound-wave {{
    display: inline-flex;
    align-items: flex-end;
    gap: 3.5px;
    height: 22px;
    vertical-align: middle;
    margin-left: 10px;
}}
.sound-wave .bar {{
    width: 3.5px;
    background: linear-gradient(180deg, #818CF8 0%, #EC4899 100%);
    border-radius: 999px;
    animation: soundWave 1.1s ease-in-out infinite alternate;
}}
.sound-wave .b1 {{ height: 35%; animation-delay: 0.1s; }}
.sound-wave .b2 {{ height: 85%; animation-delay: 0.45s; }}
.sound-wave .b3 {{ height: 50%; animation-delay: 0.25s; }}
.sound-wave .b4 {{ height: 100%; animation-delay: 0.6s; }}
.sound-wave .b5 {{ height: 65%; animation-delay: 0.35s; }}

@keyframes soundWave {{
    0% {{ transform: scaleY(0.35); }}
    100% {{ transform: scaleY(1); }}
}}

/* Pulsing Status Dot */
.pulse-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse 1.8s infinite;
    margin-right: 6px;
    vertical-align: middle;
}}
@keyframes pulse {{
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
    70% {{ transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }}
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
}}

/* Premium Top Header Brand Bar */
.brand-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0 20px 0;
    border-bottom: 1px solid var(--header-border);
    margin-bottom: 24px;
}}
.brand-title {{
    font-size: 2.3rem;
    font-weight: 800;
    margin: 0;
    background: var(--brand-title-grad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: flex;
    align-items: center;
}}
.brand-subtitle {{
    color: var(--text-secondary);
    font-size: 0.95rem;
    margin-top: 4px;
    font-weight: 400;
}}
.status-pill {{
    display: inline-flex;
    align-items: center;
    background: var(--status-pill-bg);
    border: 1px solid var(--status-pill-border);
    color: var(--status-pill-text);
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}}

/* Glassmorphism Hero Showcase Deck */
.weather-hero-deck {{
    border-radius: 24px;
    padding: 30px 34px;
    margin-bottom: 28px;
    background: var(--hero-bg);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid var(--hero-border);
    box-shadow: var(--card-shadow);
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}}
.weather-hero-deck:hover {{
    border-color: rgba(99, 102, 241, 0.4);
}}

.hero-meta-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 16px;
}}
.badge-chip {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 999px;
    background: var(--badge-chip-bg);
    color: var(--badge-chip-text);
    border: 1px solid var(--badge-chip-border);
}}
.badge-condition {{
    background: rgba(99, 102, 241, 0.18);
    color: #4F46E5;
    border-color: rgba(99, 102, 241, 0.35);
}}

.hero-main-content {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
}}
.temp-display {{
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--metric-tile-bg);
    border: 1px solid var(--metric-tile-border);
    padding: 12px 24px;
    border-radius: 20px;
}}
.temp-number {{
    font-family: 'Outfit', sans-serif;
    font-size: 3.8rem;
    font-weight: 800;
    line-height: 1;
    color: var(--text-primary);
}}
.temp-unit {{
    font-size: 1.8rem;
    font-weight: 600;
    color: #6366F1;
}}
.temp-subtext {{
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-top: 2px;
}}

.hero-headline {{
    font-size: 1.85rem;
    font-weight: 700;
    margin: 8px 0 6px 0;
    color: var(--text-primary);
    font-family: 'Outfit', sans-serif;
}}
.hero-desc {{
    font-size: 1.05rem;
    color: var(--text-secondary);
    line-height: 1.6;
    max-width: 680px;
    margin: 0;
}}

.hero-metrics-grid {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 22px;
    padding-top: 18px;
    border-top: 1px solid var(--hero-border);
}}
.metric-tile {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--metric-tile-bg);
    border: 1px solid var(--metric-tile-border);
    border-radius: 14px;
    padding: 8px 16px;
    font-size: 0.92rem;
    color: var(--text-primary);
    transition: all 0.2s ease;
}}
.metric-tile:hover {{
    border-color: rgba(99, 102, 241, 0.4);
    transform: translateY(-1px);
}}

/* Container Border Wrapper Card Styling (Streamlit Native Containers) */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: var(--card-bg) !important;
    backdrop-filter: blur(18px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(160%) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 20px !important;
    padding: 18px 20px !important;
    box-shadow: var(--card-shadow) !important;
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease, box-shadow 0.25s ease !important;
    margin-bottom: 18px !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    transform: translateY(-4px) !important;
    border-color: var(--card-hover-border) !important;
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.12), 0 0 20px 0 rgba(99, 102, 241, 0.15) !important;
}}

/* Track Card Metadata */
.card-header-line {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}}
.track-rank {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: #6366F1;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.25);
    padding: 2px 8px;
    border-radius: 8px;
}}
.track-name-text {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 4px 0 2px 0;
    line-height: 1.3;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.track-artist-text {{
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.track-album-text {{
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-bottom: 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}

/* Native Streamlit Audio Player Styling */
div[data-testid="stAudio"] {{
    margin: 8px 0 12px 0;
}}
div[data-testid="stAudio"] audio {{
    width: 100%;
    height: 38px;
    border-radius: 999px;
    outline: none;
    filter: var(--audio-filter);
}}

/* External Streaming Link Buttons */
.stream-actions-group {{
    display: flex;
    gap: 8px;
    margin-top: 10px;
}}
.stream-action-pill {{
    flex: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    padding: 8px 12px;
    border-radius: 12px;
    font-size: 0.84rem;
    font-weight: 600;
    text-decoration: none !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    border: 1px solid var(--stream-btn-border);
    background: var(--stream-btn-bg);
    color: var(--stream-btn-text) !important;
}}
.stream-action-pill:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);
}}
.btn-apple:hover {{
    background: rgba(252, 60, 68, 0.15);
    border-color: rgba(252, 60, 68, 0.6);
    color: #FC3C44 !important;
}}
.btn-spotify:hover {{
    background: rgba(29, 185, 84, 0.15);
    border-color: rgba(29, 185, 84, 0.6);
    color: #1DB954 !important;
}}
.btn-youtube:hover {{
    background: rgba(255, 0, 0, 0.15);
    border-color: rgba(255, 0, 0, 0.6);
    color: #FF0000 !important;
}}

.stream-icon {{
    width: 17px;
    height: 17px;
    display: inline-block;
    vertical-align: middle;
    flex-shrink: 0;
}}

/* Styled Streamlit Button Overrides */
div[data-testid="stButton"] button {{
    border-radius: 14px !important;
    border: 1px solid var(--btn-border) !important;
    background: var(--btn-bg) !important;
    color: var(--btn-text) !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}}
div[data-testid="stButton"] button:hover {{
    background: rgba(99, 102, 241, 0.15) !important;
    border-color: rgba(99, 102, 241, 0.5) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.15) !important;
}}

/* Auto-Detect Location Button Accent */
.detect-btn-wrapper div[data-testid="stButton"] button {{
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%) !important;
    border: 1px solid rgba(99, 102, 241, 0.45) !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}}
.detect-btn-wrapper div[data-testid="stButton"] button:hover {{
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.35) 0%, rgba(168, 85, 247, 0.35) 100%) !important;
    border-color: rgba(168, 85, 247, 0.7) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.25) !important;
}}

/* Theme Switcher Button Accent */
.theme-switch-btn div[data-testid="stButton"] button {{
    background: var(--theme-toggle-bg) !important;
    border: 1px solid var(--theme-toggle-border) !important;
    color: var(--theme-toggle-text) !important;
    font-weight: 700 !important;
    border-radius: 999px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
}}
.theme-switch-btn div[data-testid="stButton"] button:hover {{
    border-color: #6366F1 !important;
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.3) !important;
}}

/* Primary discovery button */
.shuffle-btn-wrapper div[data-testid="stButton"] button {{
    background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 24px -4px rgba(99, 102, 241, 0.5) !important;
}}
.shuffle-btn-wrapper div[data-testid="stButton"] button:hover {{
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 12px 30px -4px rgba(168, 85, 247, 0.6) !important;
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --- Sidebar Navigation & Atmosphere Console ---------------------------
with st.sidebar:
    render_html(
        """
        <div style="padding: 10px 0 16px 0; border-bottom: 1px solid var(--sidebar-border); margin-bottom: 16px;">
            <div style="font-size: 1.3rem; font-weight: 800; font-family: 'Outfit', sans-serif;">
                🎛️ Atmospheric Studio
            </div>
            <div style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 3px;">
                Fine-tune your skies, themes & music
            </div>
        </div>
        """
    )

    # Theme Switcher in Sidebar
    theme_switch_label = "☀️ Switch to Light Mode" if is_dark else "🌙 Switch to Dark Mode"
    st.markdown('<div class="theme-switch-btn">', unsafe_allow_html=True)
    st.button(
        theme_switch_label,
        on_click=toggle_theme_callback,
        key="sidebar_theme_toggle",
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 1-Click Fast, Bulletproof Auto-Detect Location Button using Callback
    st.markdown('<div class="detect-btn-wrapper">', unsafe_allow_html=True)
    st.button("🎯 Auto-Detect My Location", on_click=auto_detect_callback, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Optional Precision Satellite GPS in collapsed expander
    if HAS_GEOLOCATION and callable(streamlit_geolocation):
        with st.expander("📡 Precision Satellite GPS", expanded=False):
            st.caption("Query device GPS sensor (requires permission):")
            try:
                loc = streamlit_geolocation()
                if loc and loc.get("latitude") and loc.get("longitude"):
                    detected = reverse_geocode_city(loc["latitude"], loc["longitude"])
                    if detected and detected.lower() != st.session_state.city.lower():
                        set_city_callback(detected)
                        st.toast(f"📍 GPS locked: {detected}", icon="🛰️")
                        st.rerun()
            except Exception:
                st.caption("Satellite GPS idle. Network telemetry active.")

    # Synchronized City Input Box with on_change callback
    city_input = st.text_input(
        "🏙️ City or Destination",
        key="city_input_box",
        on_change=on_city_input_change,
        placeholder="e.g. London, Tokyo, New York, Chennai...",
    )

    # Quick City Presets using on_click callbacks (safe & collision-free)
    st.markdown(
        "<span style='font-size: 0.82rem; font-weight: 600; color: var(--text-secondary);'>⚡ Quick Teleport Destinations:</span>",
        unsafe_allow_html=True,
    )
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.button("🇬🇧 London", on_click=set_city_callback, args=("London",), use_container_width=True)
        st.button("🇯🇵 Tokyo", on_click=set_city_callback, args=("Tokyo",), use_container_width=True)
        st.button("🇮🇳 Chennai", on_click=set_city_callback, args=("Chennai",), use_container_width=True)
        st.button("🇮🇸 Reykjavík", on_click=set_city_callback, args=("Reykjavik",), use_container_width=True)
    with col_p2:
        st.button("🇺🇸 New York", on_click=set_city_callback, args=("New York",), use_container_width=True)
        st.button("🇫🇷 Paris", on_click=set_city_callback, args=("Paris",), use_container_width=True)
        st.button("🇦🇺 Sydney", on_click=set_city_callback, args=("Sydney",), use_container_width=True)
        st.button("🌴 Miami", on_click=set_city_callback, args=("Miami",), use_container_width=True)

    st.markdown("<hr style='border-color: var(--sidebar-border); margin: 20px 0;'>", unsafe_allow_html=True)

    # Genre Selector
    genre = st.selectbox(
        "🎧 Musical Atmosphere",
        [
            "Pop",
            "Rock",
            "Lo-fi",
            "Hip-Hop",
            "Romantic",
            "Tamil",
            "Indie / Acoustic",
            "Electronic / Chill",
        ],
        index=0,
    )

    # Track count
    song_count = st.slider(
        "🔢 Soundscapes to Recommend",
        min_value=10,
        max_value=40,
        value=24,
        step=2,
        help="Recommends a deep non-repeating playlist of unique studio tracks.",
    )

    # Shuffle button with callback
    st.markdown('<div class="shuffle-btn-wrapper">', unsafe_allow_html=True)
    st.button("🎲 Shuffle & Fresh Discoveries", on_click=shuffle_callback, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Sidebar Footer Specs Card
    render_html(
        """
        <div style="margin-top: 28px; padding: 16px; border-radius: 14px; background: var(--badge-chip-bg); border: 1px solid var(--badge-chip-border);">
            <div style="font-size: 0.78rem; font-weight: 700; color: #6366F1; letter-spacing: 0.05em; text-transform: uppercase;">
                ✨ Studio Audio Engine
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 6px; line-height: 1.5;">
                • High-Res 600px Retina Covers<br>
                • 30s High-Fidelity Audio Previews<br>
                • Multi-provider telemetry & auto-sync<br>
                • Dark Luxury & Daylight Frost modes
            </div>
        </div>
        """
    )


# --- Main Application Header ------------------------------------------
col_head_left, col_head_right = st.columns([3, 1.3])
with col_head_left:
    render_html(
        """
        <div>
            <h1 class="brand-title">
                🌦️ Weather Beats
                <span class="sound-wave">
                    <span class="bar b1"></span>
                    <span class="bar b2"></span>
                    <span class="bar b3"></span>
                    <span class="bar b4"></span>
                    <span class="bar b5"></span>
                </span>
            </h1>
            <div class="brand-subtitle">
                Dynamic soundtracks algorithmically curated to your skies, temperature & time.
            </div>
        </div>
        """
    )
with col_head_right:
    col_status, col_theme = st.columns([1, 1])
    with col_status:
        render_html(
            """
            <div style="padding-top: 10px;">
                <span class="status-pill">
                    <span class="pulse-dot"></span>
                    Live Sync
                </span>
            </div>
            """
        )
    with col_theme:
        st.markdown('<div class="theme-switch-btn" style="padding-top: 4px;">', unsafe_allow_html=True)
        top_switch_text = "☀️ Light" if is_dark else "🌙 Dark"
        st.button(
            top_switch_text,
            on_click=toggle_theme_callback,
            key="header_theme_toggle",
            help="Switch between Light and Dark mode",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 12px; border-bottom: 1px solid var(--header-border); margin-bottom: 24px;'></div>", unsafe_allow_html=True)


# --- Weather & Recommendation Processing ------------------------------
current_city = st.session_state.city.strip()

if not current_city:
    st.info("👈 Enter a city or pick a preset from the sidebar to begin your journey.")
else:
    with st.spinner(f"📡 Fetching live atmospheric conditions for {current_city}..."):
        try:
            weather = cached_weather(current_city)
        except Exception:
            weather = None

    if not weather:
        st.error(
            f"❌ Unable to find weather telemetry for **'{current_city}'**. "
            "Please check the spelling or select a quick preset from below."
        )
        col_err1, col_err2 = st.columns(2)
        with col_err1:
            st.button("🔄 Reset to London", on_click=set_city_callback, args=("London",), use_container_width=True)
        with col_err2:
            st.button("🎯 Detect My Location", on_click=auto_detect_callback, use_container_width=True)
    else:
        vibe = get_weather_vibe_summary(weather, genre=genre)
        theme_key = vibe.get("theme", "sunny")

        # Dynamically inject atmospheric theme gradient onto page (Dark or Light)
        gradients_dict = THEME_GRADIENTS_DARK if is_dark else THEME_GRADIENTS_LIGHT
        ambient_bg = gradients_dict.get(theme_key, gradients_dict["sunny"])
        st.markdown(
            f"""<style>.stApp {{ background: {ambient_bg} !important; background-attachment: fixed !important; }}</style>""",
            unsafe_allow_html=True,
        )

        flag = f"({weather['country']})" if weather.get("country") else ""
        icon_url = f"https://openweathermap.org/img/wn/{weather['icon']}@2x.png" if weather.get("icon") else ""

        # Luxury Frosted Hero Deck (Safely rendered via render_html)
        hero_html = f"""
        <div class="weather-hero-deck">
            <div class="hero-meta-row">
                <span class="badge-chip">📍 <b>{weather['city']}</b> {flag}</span>
                <span class="badge-chip">🕒 <b>{weather['time_of_day']}time</b></span>
                <span class="badge-chip badge-condition">{vibe['icon']} {weather['condition']}</span>
                <span class="badge-chip">🎧 {genre} Mode</span>
            </div>
            <div class="hero-main-content">
                <div>
                    <h2 class="hero-headline">{vibe['headline']}</h2>
                    <p class="hero-desc">{vibe['desc']}</p>
                </div>
                <div class="temp-display">
                    <div class="temp-number">{weather['temperature']}</div>
                    <div>
                        <div class="temp-unit">°C</div>
                        <div class="temp-subtext">Feels {weather['feels_like']}°C</div>
                    </div>
                </div>
            </div>
            <div class="hero-metrics-grid">
                <div class="metric-tile">💧 Humidity: <b>{weather['humidity']}%</b></div>
                <div class="metric-tile">💨 Wind: <b>{weather['wind_speed']} m/s</b></div>
                <div class="metric-tile">🌤️ Atmosphere: <b>{weather['description'].title()}</b></div>
                <div class="metric-tile">✨ Curated Mood: <b>{weather['condition']} Sky</b></div>
            </div>
        </div>
        """
        render_html(hero_html)

        # Fetch dynamic non-repeated recommendations
        with st.spinner(f"🎶 Mixing {song_count} studio tracks for {genre} in {weather['condition']} skies..."):
            try:
                songs = cached_recommendations(
                    weather["condition"],
                    weather["time_of_day"],
                    weather["temperature"],
                    genre,
                    song_count,
                    st.session_state.seed_offset,
                )
            except Exception:
                songs = []

        if not songs:
            st.warning(f"No songs discovered for {genre} right now. Try switching genres or tapping Shuffle!")
        else:
            # Control Deck: Search Filter & Stats
            col_sec_title, col_sec_filter = st.columns([1.8, 1.2])
            with col_sec_title:
                render_html(
                    f"""
                    <div style="display: flex; align-items: baseline; gap: 10px; margin-top: 10px;">
                        <h3 class="section-title">🎶 Curated Soundscapes</h3>
                        <span style="color: var(--text-secondary); font-size: 0.9rem; font-weight: 500;">
                            ({len(songs)} Unique Studio Master Tracks)
                        </span>
                    </div>
                    """
                )
            with col_sec_filter:
                filter_text = st.text_input(
                    "Search songs or artists",
                    placeholder="🔍 Filter by song, artist, album...",
                    label_visibility="collapsed",
                )

            # Filter songs if user entered query
            if filter_text and filter_text.strip():
                query = filter_text.strip().lower()
                displayed_songs = [
                    s for s in songs
                    if query in s["title"].lower() or query in s["artist"].lower() or query in s["album"].lower()
                ]
            else:
                displayed_songs = songs

            render_html(
                f"""
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 20px;">
                    Showing <b style="color: var(--text-primary);">{len(displayed_songs)}</b> of <b style="color: var(--text-primary);">{len(songs)}</b> de-duplicated tracks • Instant 30s preview enabled
                </div>
                """
            )

            # Render in a Responsive 2-Column Grid with Native Border Containers
            cols_per_row = 2
            for i in range(0, len(displayed_songs), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for col_idx, song_idx in enumerate(range(i, min(i + cols_per_row, len(displayed_songs)))):
                    song = displayed_songs[song_idx]
                    with row_cols[col_idx]:
                        with st.container(border=True):
                            art_col, meta_col = st.columns([1, 2.3])

                            with art_col:
                                art_url = song.get("artwork") or "https://placehold.co/600x600/121829/FFFFFF?text=Music"
                                st.image(
                                    art_url,
                                    use_container_width=True,
                                    output_format="JPEG",
                                )

                            with meta_col:
                                # Header badges row
                                rank_num = f"#{song_idx + 1:02d}"
                                duration_chip = f"<span class='badge-chip' style='padding: 2px 8px; font-size: 0.75rem;'>⏱️ {song['duration']}</span>" if song.get("duration") else ""
                                year_chip = f"<span class='badge-chip' style='padding: 2px 8px; font-size: 0.75rem;'>📅 {song['year']}</span>" if song.get("year") else ""

                                card_meta_html = f"""
                                <div class="card-header-line">
                                    <span class="track-rank">{rank_num}</span>
                                    <div>{duration_chip} {year_chip}</div>
                                </div>
                                <div class="track-name-text" title="{song['title']}">{song['title']}</div>
                                <div class="track-artist-text">👤 <b>{song['artist']}</b></div>
                                <div class="track-album-text" title="{song['album']}">💿 {song['album']}</div>
                                """
                                render_html(card_meta_html)

                                # Audio preview player
                                if song.get("preview"):
                                    st.audio(song["preview"])
                                else:
                                    render_html(
                                        "<div style='font-size: 0.8rem; color: var(--text-muted); padding: 8px 0;'>ℹ️ Preview restricted by record label</div>"
                                    )

                                # External Streaming Action Links
                                apple_link = song.get("link", "#")
                                spotify_url = spotify_search_url(song["title"], song["artist"])
                                youtube_url = youtube_search_url(song["title"], song["artist"])

                                actions_html = f"""
                                <div class="stream-actions-group">
                                    <a href="{apple_link}" target="_blank" rel="noopener noreferrer" class="stream-action-pill btn-apple" title="Listen on Apple Music">
                                        {APPLE_MUSIC_ICON_SVG}
                                        <span>Apple</span>
                                    </a>
                                    <a href="{spotify_url}" target="_blank" rel="noopener noreferrer" class="stream-action-pill btn-spotify" title="Search on Spotify">
                                        {SPOTIFY_ICON_SVG}
                                        <span>Spotify</span>
                                    </a>
                                    <a href="{youtube_url}" target="_blank" rel="noopener noreferrer" class="stream-action-pill btn-youtube" title="Search on YouTube">
                                        {YOUTUBE_ICON_SVG}
                                        <span>YouTube</span>
                                    </a>
                                </div>
                                """
                                render_html(actions_html)