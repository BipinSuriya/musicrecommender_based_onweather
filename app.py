import importlib
from urllib.parse import quote_plus

import streamlit as st

# Optional geolocation support with dynamic import to prevent IDE missing-import warnings
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
)

# --- Streamlit Page Configuration -------------------------------------
st.set_page_config(
    page_title="Weather Beats — Soundtracks of the Sky",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Styling & CSS Design System --------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

h1, h2, h3, h4, .hero-title, .track-title {
    font-family: 'Outfit', sans-serif;
}

/* Glassmorphism Hero Card */
.weather-hero {
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 12px 32px 0 rgba(0, 0, 0, 0.25);
    transition: all 0.3s ease;
}

.weather-hero:hover {
    border-color: rgba(255, 255, 255, 0.2);
    box-shadow: 0 16px 40px 0 rgba(0, 0, 0, 0.35);
}

/* Metric Pills */
.metric-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    padding: 8px 16px;
    border-radius: 999px;
    font-size: 0.95rem;
    font-weight: 500;
    margin-right: 8px;
    margin-bottom: 8px;
}

/* Song Recommendation Card */
.song-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    backdrop-filter: blur(10px);
}

.song-card:hover {
    transform: translateY(-3px);
    border-color: rgba(99, 179, 237, 0.4);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.song-cover {
    border-radius: 12px;
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: cover;
    box-shadow: 0 8px 16px rgba(0,0,0,0.3);
}

.badge-tag {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 12px;
    background: rgba(99, 179, 237, 0.18);
    color: #90cdf4;
    border: 1px solid rgba(99, 179, 237, 0.3);
    display: inline-block;
    margin-right: 6px;
}

.track-number {
    font-size: 0.85rem;
    font-weight: 700;
    color: #a0aec0;
    letter-spacing: 0.5px;
}

.track-artist {
    color: #cbd5e0;
    font-size: 0.95rem;
    font-weight: 500;
}

.vibe-badge {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    display: inline-block;
    letter-spacing: 0.4px;
}

/* Quick city chip buttons */
div[data-testid="stHorizontalBlock"] button {
    border-radius: 20px;
}

/* Music Streaming Action Buttons */
.stream-btn-container {
    display: flex;
    gap: 8px;
    margin-top: 12px;
}

.stream-btn {
    flex: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 10px;
    font-size: 0.88rem;
    font-weight: 600;
    text-decoration: none !important;
    transition: all 0.2s ease;
    border: 1px solid rgba(255, 255, 255, 0.12);
    cursor: pointer;
    background: rgba(255, 255, 255, 0.06);
    color: #ffffff !important;
}

.stream-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
}

.stream-btn-apple:hover {
    background: rgba(250, 45, 72, 0.2);
    border-color: rgba(250, 45, 72, 0.6);
    color: #ffffff !important;
}

.stream-btn-spotify:hover {
    background: rgba(29, 185, 84, 0.2);
    border-color: rgba(29, 185, 84, 0.6);
    color: #ffffff !important;
}

.stream-icon {
    width: 19px;
    height: 19px;
    display: inline-block;
    vertical-align: middle;
    flex-shrink: 0;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Official App Icon SVGs
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


# --- Helper URL Builders ----------------------------------------------
def spotify_search_url(title, artist):
    query = quote_plus(f"{title} {artist}")
    return f"https://open.spotify.com/search/{query}"


def youtube_search_url(title, artist):
    query = quote_plus(f"{title} {artist}")
    return f"https://www.youtube.com/results?search_query={query}"


# --- Caching Wrappers -------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def cached_weather(city_name):
    return get_weather_and_time(city_name)


@st.cache_data(ttl=600, show_spinner=False)
def cached_recommendations(condition, time_of_day, temp, genre, count, seed_offset):
    # Simulated weather dict for caching key stability
    mock_weather = {
        "condition": condition,
        "time_of_day": time_of_day,
        "temperature": temp,
    }
    return get_dynamic_music_recommendations(
        mock_weather, genre=genre, count=count, seed_offset=seed_offset
    )


# --- Session State Initialization -------------------------------------
if "city" not in st.session_state:
    st.session_state.city = "London"
if "seed_offset" not in st.session_state:
    st.session_state.seed_offset = 0
if "search_filter" not in st.session_state:
    st.session_state.search_filter = ""


# --- Sidebar Navigation & Controls ------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ **Atmospheric Control**")

    # Geolocation support
    if HAS_GEOLOCATION and callable(streamlit_geolocation):
        st.caption("📍 Pinpoint your local atmospheric vibe")
        loc = streamlit_geolocation()
        if loc and loc.get("latitude"):
            with st.spinner("Resolving GPS coordinates..."):
                detected = reverse_geocode_city(loc["latitude"], loc["longitude"])
                if detected:
                    st.session_state.city = detected
                    st.success(f"📍 Set to **{detected}**")
                else:
                    st.warning("Could not resolve GPS to city name.")

    city_input = st.text_input(
        "🏙️ City Name",
        value=st.session_state.city,
        placeholder="e.g. New York, Tokyo, Paris, Chennai...",
        key="city_input_box",
    )
    if city_input:
        st.session_state.city = city_input.strip()

    # Quick City Presets
    st.caption("⚡ Quick City Presets:")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        if st.button("🇬🇧 London", use_container_width=True):
            st.session_state.city = "London"
            st.rerun()
        if st.button("🇯🇵 Tokyo", use_container_width=True):
            st.session_state.city = "Tokyo"
            st.rerun()
    with col_p2:
        if st.button("🇺🇸 New York", use_container_width=True):
            st.session_state.city = "New York"
            st.rerun()
        if st.button("🇮🇳 Chennai", use_container_width=True):
            st.session_state.city = "Chennai"
            st.rerun()
    with col_p3:
        if st.button("🇫🇷 Paris", use_container_width=True):
            st.session_state.city = "Paris"
            st.rerun()
        if st.button("🇦🇺 Sydney", use_container_width=True):
            st.session_state.city = "Sydney"
            st.rerun()

    st.divider()

    # Genre Selector
    genre = st.selectbox(
        "🎧 Musical Atmosphere (Genre)",
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

    # Song Count Slider (Allowing 10 to 40+ non-repeating songs)
    song_count = st.slider(
        "🔢 Number of Songs to Recommend",
        min_value=10,
        max_value=40,
        value=24,
        step=2,
        help="Recommends a deep, rich non-repeating playlist of unique tracks.",
    )

    # Refresh / Shuffle Button
    if st.button("🎲 Shuffle & Fresh Discoveries", use_container_width=True):
        st.session_state.seed_offset += 1
        st.rerun()

    st.markdown("---")
    st.caption("✨ Powered by **OpenWeatherMap** & **Apple Music / iTunes Engine**")


# --- Main Application Header ------------------------------------------
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(
        """
        # 🌦️ **Weather Beats**
        ##### *Dynamic soundtracks algorithmically curated to your skies, temperature & time.*
        """
    )
with col_head2:
    st.markdown(
        """
        <div style="text-align: right; padding-top: 15px;">
            <span class="vibe-badge">⚡ Real-Time Weather Sync</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px;'>", unsafe_allow_html=True)


# --- Weather & Recommendation Processing ------------------------------
current_city = st.session_state.city.strip()

if not current_city:
    st.info("👈 Please enter a city or select a preset from the sidebar to begin.")
else:
    with st.spinner(f"📡 Fetching live atmospheric conditions for {current_city}..."):
        weather = cached_weather(current_city)

    if not weather:
        st.error(
            f"❌ Unable to find weather data for **'{current_city}'**. "
            "Please verify the city spelling or try another city."
        )
    else:
        # Determine current vibe profile
        vibe = get_weather_vibe_summary(weather, genre=genre)

        # Dynamic Weather Banner / Hero Card
        flag = f"({weather['country']})" if weather.get('country') else ""
        icon_url = f"https://openweathermap.org/img/wn/{weather['icon']}@2x.png" if weather.get("icon") else ""

        banner_html = f"""
        <div class="weather-hero">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
                <div>
                    <span class="badge-tag">📍 {weather['city']} {flag}</span>
                    <span class="badge-tag">🕒 {weather['time_of_day']}time</span>
                    <span class="badge-tag">{vibe['icon']} {weather['condition']}</span>
                    <h2 style="margin: 12px 0 6px 0; font-size: 2.1rem; font-weight: 700;">{vibe['headline']}</h2>
                    <p style="color: #cbd5e0; margin: 0 0 14px 0; font-size: 1.05rem; max-width: 750px;">
                        {vibe['desc']}
                    </p>
                    <div style="display: flex; flex-wrap: wrap; margin-top: 8px;">
                        <div class="metric-pill">🌡️ <b>{weather['temperature']}°C</b> (Feels {weather['feels_like']}°C)</div>
                        <div class="metric-pill">💧 Humidity: <b>{weather['humidity']}%</b></div>
                        <div class="metric-pill">💨 Wind: <b>{weather['wind_speed']} m/s</b></div>
                        <div class="metric-pill">🌤️ Sky: <b>{weather['description']}</b></div>
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(banner_html, unsafe_allow_html=True)

        # Fetch dynamic non-repeated recommendations
        with st.spinner(f"🎶 Mixing {song_count} non-repeated tracks for {genre} in {weather['condition']} skies..."):
            songs = cached_recommendations(
                weather["condition"],
                weather["time_of_day"],
                weather["temperature"],
                genre,
                song_count,
                st.session_state.seed_offset,
            )

        if not songs:
            st.warning(f"No songs found for {genre} right now. Try switching genres or refreshing!")
        else:
            # Control bar for results: Filter & stats
            sub_col1, sub_col2 = st.columns([2, 1])
            with sub_col1:
                st.subheader(f"🎶 Curated Playlist ({len(songs)} Unique Tracks • No Repeats)")
            with sub_col2:
                filter_text = st.text_input(
                    "🔍 Filter songs or artists",
                    placeholder="Type to filter...",
                    label_visibility="collapsed",
                )

            # Filter songs if user typed a keyword
            if filter_text.strip():
                query = filter_text.strip().lower()
                displayed_songs = [
                    s for s in songs
                    if query in s["title"].lower() or query in s["artist"].lower() or query in s["album"].lower()
                ]
            else:
                displayed_songs = songs

            st.caption(
                f"Showing **{len(displayed_songs)}** of **{len(songs)}** non-repeated tracks. "
                "All songs are de-duplicated by title and artist identity."
            )

            # Render Cards in a 2-Column Responsive Grid Layout
            cols_per_row = 2
            for i in range(0, len(displayed_songs), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for col_idx, song_idx in enumerate(range(i, min(i + cols_per_row, len(displayed_songs)))):
                    song = displayed_songs[song_idx]
                    with row_cols[col_idx]:
                        with st.container():
                            # Inner columns for artwork & metadata
                            art_col, meta_col = st.columns([1, 2.2])

                            with art_col:
                                if song.get("artwork"):
                                    st.image(
                                        song["artwork"],
                                        use_container_width=True,
                                        output_format="JPEG",
                                    )
                                else:
                                    st.image(
                                        "https://placehold.co/400x400/222/white?text=Music",
                                        use_container_width=True,
                                    )

                            with meta_col:
                                # Header badges
                                tag_row = f"<span class='track-number'>#{song_idx + 1}</span> "
                                if song.get("duration"):
                                    tag_row += f"<span class='badge-tag'>⏱️ {song['duration']}</span> "
                                if song.get("year"):
                                    tag_row += f"<span class='badge-tag'>📅 {song['year']}</span>"
                                st.markdown(tag_row, unsafe_allow_html=True)

                                # Title and artist
                                st.markdown(f"**{song['title']}**")
                                st.markdown(f"<span class='track-artist'>👤 {song['artist']}</span>", unsafe_allow_html=True)
                                st.caption(f"💿 {song['album']}")

                                # Audio preview player
                                if song.get("preview"):
                                    st.audio(song["preview"])
                                else:
                                    st.caption("ℹ️ Preview unavailable from publisher")

                                # External streaming links with official app icons
                                apple_link = song.get("link", "#")
                                spotify_url = spotify_search_url(song["title"], song["artist"])

                                st.markdown(
                                    f"""
                                    <div class="stream-btn-container">
                                        <a href="{apple_link}" target="_blank" rel="noopener noreferrer" class="stream-btn stream-btn-apple">
                                            {APPLE_MUSIC_ICON_SVG}
                                            <span>Apple Music</span>
                                        </a>
                                        <a href="{spotify_url}" target="_blank" rel="noopener noreferrer" class="stream-btn stream-btn-spotify">
                                            {SPOTIFY_ICON_SVG}
                                            <span>Spotify</span>
                                        </a>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                        st.markdown("<hr style='margin: 12px 0 20px 0; opacity: 0.2;'>", unsafe_allow_html=True)