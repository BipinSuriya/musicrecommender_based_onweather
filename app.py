from urllib.parse import quote_plus

import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from main import (
    get_weather_and_time,
    map_weather_to_music,
    get_itunes_tracks,
    reverse_geocode_city,
)

st.title("🌦️ Weather Music Recommender")

# --- Cached wrappers (avoid re-hitting APIs on every rerun) -------------

@st.cache_data(ttl=600)
def cached_weather(city_name):
    return get_weather_and_time(city_name)


@st.cache_data(ttl=600)
def cached_tracks(search_query):
    return get_itunes_tracks(search_query)


def spotify_search_url(title, artist):
    query = quote_plus(f"{title} {artist}")
    return f"https://open.spotify.com/search/{query}"


# --- Session state -------------------------------------------------------

if "city" not in st.session_state:
    st.session_state.city = ""

st.write("📍 Detect My Location")
location = streamlit_geolocation()

if location and location.get("latitude"):
    detected_city = reverse_geocode_city(location["latitude"], location["longitude"])
    if detected_city:
        st.session_state.city = detected_city
    else:
        st.warning("Couldn't resolve your location to a city. Please enter it manually.")

city = st.text_input("Enter your city", key="city")
genre = st.selectbox(
    "🎵 Select Genre",
    ["Pop", "Rock", "Lo-fi", "Hip-Hop", "Romantic", "Tamil"],
)

if st.button("Recommend Songs"):
    if not city.strip():
        st.error("Please enter a city name.")
    else:
        weather = cached_weather(city)

        if not weather:
            st.error("Couldn't fetch weather for that city. Check the spelling and try again.")
        else:
            st.subheader("🌦️ Current Weather")

            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ Temperature", f"{weather['temperature']} °C")
            col2.metric("💧 Humidity", f"{weather['humidity']} %")
            col3.metric("💨 Wind Speed", f"{weather['wind_speed']} m/s")

            st.write(f"🌦️ **Weather:** {weather['condition']}")
            st.write(f"🕒 **Time:** {weather['time_of_day']}")

            search_query = map_weather_to_music(weather, genre)
            songs = cached_tracks(search_query)

            if not songs:
                st.warning(f"No songs found for **{search_query}**. Try a different genre.")
            else:
                st.header("🎶 Recommended Songs")
                for i, song in enumerate(songs, start=1):
                    with st.container():
                        col1, col2 = st.columns([1, 3])

                        with col1:
                            if song["artwork"]:
                                st.image(song["artwork"], width=150)

                        with col2:
                            st.subheader(f"🎵 {i}. {song['title']}")
                            st.write(f"👤 **Artist:** {song['artist']}")
                            st.write(f"💿 **Album:** {song['album']}")

                            if song["preview"]:
                                st.audio(song["preview"])

                            btn_col1, btn_col2 = st.columns(2)

                            with btn_col1:
                                if song["link"]:
                                    st.link_button(
                                        "🍎 Full song on Apple Music",
                                        song["link"],
                                        use_container_width=True,
                                    )

                            with btn_col2:
                                st.link_button(
                                    "🎧 Full song on Spotify",
                                    spotify_search_url(song["title"], song["artist"]),
                                    use_container_width=True,
                                )

                        st.divider()