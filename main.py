import os
import requests

# --- Config -----------------------------------------------------------

# Prefer environment variables over hardcoded secrets (never commit real keys to GitHub).
WEATHER_API_KEY = os.environ.get("bea8c83ea8fd937b2de8885a3acaac72", "")

genre_artists = {
    "Pop": {
        "Clear_Day": "Dua Lipa",
        "Clear_Night": "The Weeknd",
        "Rain_Day": "Ed Sheeran",
        "Rain_Night": "Billie Eilish",
        "Clouds": "Coldplay",
    },
    "Rock": {
        "Clear_Day": "Imagine Dragons",
        "Clear_Night": "Linkin Park",
        "Rain_Day": "Coldplay",
        "Rain_Night": "Arctic Monkeys",
        "Clouds": "OneRepublic",
    },
    "Lo-fi": {
        "Clear_Day": "lofi girl",
        "Clear_Night": "lofi sleep",
        "Rain_Day": "rain lofi",
        "Rain_Night": "night lofi",
        "Clouds": "coffee lofi",
    },
    "Hip-Hop": {
        "Clear_Day": "Drake",
        "Clear_Night": "Travis Scott",
        "Rain_Day": "Eminem",
        "Rain_Night": "Post Malone",
        "Clouds": "Kendrick Lamar",
    },
    "Romantic": {
        "Clear_Day": "Ed Sheeran",
        "Clear_Night": "Bruno Mars",
        "Rain_Day": "Adele",
        "Rain_Night": "Lana Del Rey",
        "Clouds": "John Legend",
    },
    "Tamil": {
        "Clear_Day": "Anirudh",
        "Clear_Night": "Yuvan Shankar Raja",
        "Rain_Day": "A R Rahman",
        "Rain_Night": "Sid Sriram",
        "Clouds": "Harris Jayaraj",
    },
}


# --- Location / Weather -------------------------------------------------

def get_current_location():
    """Best-effort IP-based city lookup. Returns None on failure."""
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        response.raise_for_status()
        return response.json().get("city")
    except requests.RequestException:
        return None


def get_weather_and_time(city_name):
    """Fetch current weather for a city. Returns a dict, or None on failure."""
    if not city_name:
        return None

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid":'bea8c83ea8fd937b2de8885a3acaac72',
        "units": "metric",
    }

    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return None

    data = response.json()

    try:
        condition = data["weather"][0]["main"]
        current_time = data["dt"]
        sunrise = data["sys"]["sunrise"]
        sunset = data["sys"]["sunset"]
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
    except (KeyError, IndexError):
        return None

    is_day = sunrise <= current_time < sunset
    time_of_day = "Day" if is_day else "Night"

    return {
        "condition": condition,
        "time_of_day": time_of_day,
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
    }


def reverse_geocode_city(lat, lon):
    """Convert browser GPS coordinates to a city name using OpenWeatherMap's geocoding API."""
    url = "http://api.openweathermap.org/geo/1.0/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "limit": 1,
        "appid": WEATHER_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return None

    results = response.json()
    if not results:
        return None

    return results[0].get("name")


# --- Mapping --------------------------------------------------------------

def map_weather_to_music(weather_info, genre="Pop"):
    """Pick a search-query artist based on weather condition/time and genre."""
    condition = weather_info["condition"]
    time_of_day = weather_info["time_of_day"]

    if condition == "Clear":
        key = f"Clear_{time_of_day}"
    elif condition in ("Rain", "Drizzle", "Thunderstorm"):
        key = f"Rain_{time_of_day}"
    elif condition in ("Clouds", "Mist", "Fog"):
        key = "Clouds"
    else:
        return "Taylor Swift"

    return genre_artists.get(genre, genre_artists["Pop"]).get(key, "Taylor Swift")


# --- iTunes -----------------------------------------------------------

def get_itunes_tracks(search_query, limit=10):
    """Return a list of song dicts (may be empty) — never None."""
    if not search_query:
        return []

    url = "https://itunes.apple.com/search"
    params = {
        "term": search_query,
        "entity": "song",
        "limit": limit,
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return []

    data = response.json()

    if data.get("resultCount", 0) == 0:
        return []

    songs = []
    for track in data["results"]:
        artwork = track.get("artworkUrl100", "").replace("100x100", "300x300")
        songs.append(
            {
                "title": track.get("trackName", "Unknown"),
                "artist": track.get("artistName", "Unknown"),
                "album": track.get("collectionName", "Unknown"),
                "preview": track.get("previewUrl"),
                "link": track.get("trackViewUrl"),
                "artwork": artwork,
            }
        )
    return songs


# --- CLI entry point ------------------------------------------------------

if __name__ == "__main__":
    city = input("Enter your city: ")
    weather_data = get_weather_and_time(city)

    if weather_data:
        mood = map_weather_to_music(weather_data, "Hip-Hop")
        tracks = get_itunes_tracks(mood)

        if tracks:
            print(f"\n🎵 Top {len(tracks)} Recommendations 🎵\n")
            for i, song in enumerate(tracks, start=1):
                print(f"{i}. {song['title']} — {song['artist']} ({song['album']})")
        else:
            print("No songs found.")
    else:
        print("❌ Error fetching weather data.")