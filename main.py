import os
import random
import requests
from urllib.parse import quote_plus

# Load .env file if present (python-dotenv is optional but recommended)
try:
    from dotenv import load_dotenv
    import pathlib
    _env_path = pathlib.Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=_env_path, override=True)
except ImportError:
    pass  # dotenv not installed; rely on system environment variables

# --- Config -----------------------------------------------------------

# Read API key exclusively from environment variable (set in .env or system env)
WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
if not WEATHER_API_KEY:
    raise EnvironmentError(
        "OpenWeatherMap API key not found. "
        "Create a .env file in the project root with:\n"
        "  OPENWEATHER_API_KEY=your_key_here"
    )

# --- Weather Mood Catalog ---------------------------------------------
# Curated pools of top artists and genre keywords tailored to each weather condition and time of day
GENRE_WEATHER_CATALOG = {
    "Pop": {
        "Clear_Day": ["Dua Lipa", "Harry Styles", "Olivia Rodrigo", "Bruno Mars", "Katy Perry", "Justin Bieber"],
        "Clear_Night": ["The Weeknd", "Billie Eilish", "Post Malone", "Doja Cat", "ZAYN", "Troye Sivan"],
        "Rain_Day": ["Ed Sheeran", "Taylor Swift", "Shawn Mendes", "Adele", "Sam Smith", "Lewis Capaldi"],
        "Rain_Night": ["Lorde", "Billie Eilish", "Joji", "Finneas", "Conan Gray", "Gracie Abrams"],
        "Clouds": ["Coldplay", "OneRepublic", "Maroon 5", "Sia", "Lauv", "Dean Lewis"],
        "Snow": ["Taylor Swift", "Michael Buble", "Norah Jones", "Birdy", "Sara Bareilles"],
        "Thunderstorm": ["Imagine Dragons", "Fall Out Boy", "Halsey", "Panic! At The Disco", "Twenty One Pilots"],
        "Atmosphere": ["Lana Del Rey", "Lorde", "Aurora", "Hozier", "Florence and the Machine"],
    },
    "Rock": {
        "Clear_Day": ["Imagine Dragons", "Foo Fighters", "Red Hot Chili Peppers", "The Killers", "Queen", "Fall Out Boy"],
        "Clear_Night": ["Linkin Park", "Arctic Monkeys", "The Neighbourhood", "Muse", "Green Day", "The Black Keys"],
        "Rain_Day": ["Coldplay", "Radiohead", "Oasis", "U2", "Snow Patrol", "Keane"],
        "Rain_Night": ["Arctic Monkeys", "Nirvana", "Deftones", "The Smashing Pumpkins", "Pink Floyd", "Radiohead"],
        "Clouds": ["OneRepublic", "The Fray", "Kings of Leon", "Fleetwood Mac", "R.E.M.", "Paramore"],
        "Snow": ["Bon Iver", "Sigur Ros", "Death Cab for Cutie", "Coldplay", "The National"],
        "Thunderstorm": ["Linkin Park", "AC/DC", "Metallica", "Bring Me The Horizon", "Evanescence", "Avenged Sevenfold"],
        "Atmosphere": ["Radiohead", "The Cure", "Depeche Mode", "Pink Floyd", "My Bloody Valentine"],
    },
    "Lo-fi": {
        "Clear_Day": ["Lofi Girl", "Chillhop Music", "Kupla", "Idealism", "Saib", "birocratic"],
        "Clear_Night": ["Lofi Sleep", "Kudasaibeats", "Jinsang", "Tomppabeats", "Elijah Who", "Sleepy Fish"],
        "Rain_Day": ["Rain Lofi", "In Love With a Ghost", "Sarcastic Sounds", "Wun Two", "HM Surf", "eevee"],
        "Rain_Night": ["Night Lofi", "Aso", "Nokiaa", "Philanthrope", "Sleepy Fish", "Idealism"],
        "Clouds": ["Coffee Lofi", "potsu", "SwuM", "burbank", "Kupla", "invention_"],
        "Snow": ["Winter Lofi", "Kalaido", "Biosphere lofi", "Snow Chill lofi", "Slo"],
        "Thunderstorm": ["Dark Lofi", "Thunder Lofi", "Sad Lofi", "Rain Thunder Chillhop", "Kudasai"],
        "Atmosphere": ["Ambient Lofi", "Dream Lofi", "Kavv", "Ethereal Lofi", "Tycho"],
    },
    "Hip-Hop": {
        "Clear_Day": ["Drake", "Kendrick Lamar", "Snoop Dogg", "Chance The Rapper", "Amine", "Jack Harlow"],
        "Clear_Night": ["Travis Scott", "Playboi Carti", "Future", "Kid Cudi", "Don Toliver", "21 Savage"],
        "Rain_Day": ["J. Cole", "Eminem", "Mac Miller", "Logic", "Kanye West", "Nas"],
        "Rain_Night": ["Post Malone", "Juice WRLD", "XXXTENTACION", "Lil Peep", "A$AP Rocky", "Roddy Ricch"],
        "Clouds": ["Kendrick Lamar", "Tyler, The Creator", "Childish Gambino", "SZA", "Joey Bada$$"],
        "Snow": ["Drake", "Kanye West", "Kid Cudi", "Mac Miller", "Lil Yachty"],
        "Thunderstorm": ["DMX", "21 Savage", "Travis Scott", "Eminem", "Pop Smoke", "Metro Boomin"],
        "Atmosphere": ["A$AP Rocky", "Kid Cudi", "Frank Ocean", "Earl Sweatshirt", "Freddie Gibbs"],
    },
    "Romantic": {
        "Clear_Day": ["Bruno Mars", "Ed Sheeran", "Jason Mraz", "Colbie Caillat", "John Mayer", "Jack Johnson"],
        "Clear_Night": ["The Weeknd", "Frank Ocean", "Daniel Caesar", "Giveon", "Brent Faiyaz", "Leon Bridges"],
        "Rain_Day": ["Adele", "Sam Smith", "Lewis Capaldi", "Ruth B", "James Arthur", "Calum Scott"],
        "Rain_Night": ["Lana Del Rey", "SZA", "Jhene Aiko", "H.E.R.", "Snoh Aalegra", "Kiana Lede"],
        "Clouds": ["John Legend", "Alicia Keys", "Leon Bridges", "Norah Jones", "Lauv", "Bazzi"],
        "Snow": ["Michael Buble", "Celine Dion", "Sia", "Adele", "Josh Groban"],
        "Thunderstorm": ["The Weeknd", "Beyonce", "Labrinth", "Rihanna", "Billie Eilish"],
        "Atmosphere": ["Cigarettes After Sex", "Beach House", "Lana Del Rey", "Sade", "Mazzy Star"],
    },
    "Tamil": {
        "Clear_Day": ["Anirudh Ravichander", "A.R. Rahman", "Santhosh Narayanan", "GV Prakash Kumar", "D. Imman"],
        "Clear_Night": ["Yuvan Shankar Raja", "Harris Jayaraj", "Sid Sriram", "Pradeep Kumar", "Ilayaraja"],
        "Rain_Day": ["A.R. Rahman", "Harris Jayaraj", "Bombay Jayashri", "Unni Menon", "Karthik", "Hariharan"],
        "Rain_Night": ["Sid Sriram", "Yuvan Shankar Raja", "Pradeep Kumar", "Dhibu Ninan Thomas", "Leon James"],
        "Clouds": ["Harris Jayaraj", "A.R. Rahman", "Anirudh Ravichander", "Sean Roldan", "Govind Vasantha"],
        "Snow": ["A.R. Rahman", "Harris Jayaraj", "Karthik", "Hariharan", "SP Balasubrahmanyam"],
        "Thunderstorm": ["Anirudh Ravichander", "Yuvan Shankar Raja", "Santhosh Narayanan", "Ghibran", "Sam CS"],
        "Atmosphere": ["Ilayaraja", "Pradeep Kumar", "Govind Vasantha", "Sean Roldan", "Darbuka Siva"],
    },
    "Indie / Acoustic": {
        "Clear_Day": ["Vance Joy", "Luminiers", "George Ezra", "Mumford & Sons", "Of Monsters and Men"],
        "Clear_Night": ["Lord Huron", "Phoebe Bridgers", "Bon Iver", "The Paper Kites", "Gregory Alan Isakov"],
        "Rain_Day": ["Ben Howard", "Passenger", "Damien Rice", "Iron & Wine", "The Tallest Man on Earth"],
        "Rain_Night": ["Phoebe Bridgers", "Sufjan Stevens", "Julien Baker", "Elliott Smith", "Daughter"],
        "Clouds": ["Fleet Foxes", "Hozier", "The Head and the Heart", "Novo Amor", "Angus & Julia Stone"],
        "Snow": ["Bon Iver", "Sufjan Stevens", "Novo Amor", "The Japanese House"],
        "Thunderstorm": ["Florence and the Machine", "The Black Keys", "Kaleo", "Bishop Briggs"],
        "Atmosphere": ["Beach House", "Slowdive", "Men I Trust", "Alvvays", "Cigarettes After Sex"],
    },
    "Electronic / Chill": {
        "Clear_Day": ["Kygo", "Avicii", "Calvin Harris", "Disclosure", "Galantis", "Robin Schulz"],
        "Clear_Night": ["ODESZA", "Flume", "RÜFÜS DU SOL", "Lane 8", "Kaskade", "Deadmau5"],
        "Rain_Day": ["Tycho", "Bonobo", "Petit Biscuit", "Shallou", "Emancipator"],
        "Rain_Night": ["Burial", "Four Tet", "Kiasmos", "Jon Hopkins", "Massive Attack"],
        "Clouds": ["Tourist", "Chet Faker", "Kasbo", "San Holo", "Elderbrook"],
        "Snow": ["Kiasmos", "Olafur Arnalds", "Tycho", "Nils Frahm"],
        "Thunderstorm": ["Skrillex", "The Prodigy", "Pendulum", "Rezz", "ZHU"],
        "Atmosphere": ["Boards of Canada", "Aphex Twin", "Brian Eno", "Tycho", "Carbon Based Lifeforms"],
    },
}

# --- Weather & Location Service ----------------------------------------

def get_saved_default_city():
    """Retrieve the saved default home city from persistent config, defaulting to Coimbatore."""
    pref_file = os.path.join(os.path.dirname(__file__), "user_preferences.json")
    if os.path.exists(pref_file):
        try:
            import json
            with open(pref_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                city = data.get("default_city")
                if city and isinstance(city, str) and city.strip():
                    return city.strip()
        except Exception:
            pass
    return "Coimbatore"


def save_default_city(city_name):
    """Save the user's preferred default home city to persistent storage."""
    if not city_name or not city_name.strip():
        return
    pref_file = os.path.join(os.path.dirname(__file__), "user_preferences.json")
    try:
        import json
        with open(pref_file, "w", encoding="utf-8") as f:
            json.dump({"default_city": city_name.strip()}, f, indent=2)
    except Exception:
        pass


def get_current_location():
    """
    Resilient multi-provider location detector (ipinfo -> ip-api -> freeipapi).
    Corrects ISP regional gateway routing (e.g. ISP Chennai gateway) to Coimbatore.
    """
    saved_home = get_saved_default_city()
    endpoints = [
        ("https://ipinfo.io/json", "city"),
        ("http://ip-api.com/json", "city"),
        ("https://freeipapi.com/api/json", "cityName"),
    ]
    for url, key in endpoints:
        try:
            resp = requests.get(url, timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                city = data.get(key)
                if city and isinstance(city, str) and city.strip():
                    detected = city.strip()
                    # If ISP routes Tamil Nadu traffic to Chennai gateway, honor user's actual location (Coimbatore)
                    if detected.lower() in ["chennai", "madras"] and saved_home.lower() == "coimbatore":
                        return "Coimbatore"
                    return detected
        except Exception:
            continue
    return saved_home or "Coimbatore"


def get_weather_and_time(city_name):
    """Fetch real-time weather and daylight status for a city. Returns structured dict or None."""
    if not city_name or not city_name.strip():
        return None

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name.strip(),
        "appid": WEATHER_API_KEY,
        "units": "metric",
    }

    try:
        response = requests.get(base_url, params=params, timeout=6)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    try:
        condition = data["weather"][0]["main"]
        description = data["weather"][0]["description"].title()
        icon = data["weather"][0]["icon"]
        current_time = data.get("dt", 0)
        sys_data = data.get("sys", {})
        sunrise = sys_data.get("sunrise", 0)
        sunset = sys_data.get("sunset", 0)
        temperature = round(data["main"]["temp"], 1)
        feels_like = round(data["main"].get("feels_like", temperature), 1)
        humidity = data["main"].get("humidity", 0)
        wind_speed = round(data.get("wind", {}).get("speed", 0), 1)
        city_display = data.get("name", city_name)
        country = sys_data.get("country", "")
    except (KeyError, IndexError):
        return None

    is_day = sunrise <= current_time < sunset if sunrise and sunset else True
    time_of_day = "Day" if is_day else "Night"

    return {
        "city": city_display,
        "country": country,
        "condition": condition,
        "description": description,
        "icon": icon,
        "time_of_day": time_of_day,
        "temperature": temperature,
        "feels_like": feels_like,
        "humidity": humidity,
        "wind_speed": wind_speed,
    }


def reverse_geocode_city(lat, lon):
    """Convert browser GPS coordinates to city name using OpenWeatherMap's geocoding API."""
    url = "https://api.openweathermap.org/geo/1.0/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "limit": 1,
        "appid": WEATHER_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        results = response.json()
        if results and len(results) > 0:
            return results[0].get("name")
    except requests.RequestException:
        return None

    return None


# --- Weather-to-Mood Determination ------------------------------------

def get_weather_mood_key(weather_info):
    """Determine the normalized mood category key based on weather condition and daylight."""
    condition = weather_info.get("condition", "Clear")
    time_of_day = weather_info.get("time_of_day", "Day")

    if condition == "Clear":
        return f"Clear_{time_of_day}"
    elif condition in ("Rain", "Drizzle"):
        return f"Rain_{time_of_day}"
    elif condition == "Thunderstorm":
        return "Thunderstorm"
    elif condition == "Snow":
        return "Snow"
    elif condition in ("Mist", "Fog", "Haze", "Smoke", "Dust", "Sand", "Ash", "Squall", "Tornado"):
        return "Atmosphere"
    elif condition in ("Clouds",):
        return "Clouds"
    return f"Clear_{time_of_day}"


def get_weather_vibe_summary(weather_info, genre="Pop"):
    """Returns an evocative visual badge, mood headline, and description for the current vibe."""
    condition = weather_info.get("condition", "Clear")
    time_of_day = weather_info.get("time_of_day", "Day")
    temp = weather_info.get("temperature", 20)

    mood_map = {
        "Clear_Day": {
            "headline": "Golden Sun & Uplifting Energy",
            "desc": f"Bright skies and {temp}°C warmth call for vibrant, feel-good rhythms to fuel your day.",
            "icon": "☀️",
            "theme": "sunny",
        },
        "Clear_Night": {
            "headline": "Starlit Midnight Horizons",
            "desc": f"Cool {temp}°C evening skies inspire smooth, dreamy night drives and late-night grooves.",
            "icon": "✨",
            "theme": "night",
        },
        "Rain_Day": {
            "headline": "Cozy Rainy Afternoon Vibe",
            "desc": f"Gentle raindrops and {temp}°C air pair with warm acoustic strings and reflective melodies.",
            "icon": "🌧️",
            "theme": "rain",
        },
        "Rain_Night": {
            "headline": "Late-Night Rain Melancholy",
            "desc": f"The calming sound of nighttime rainfall calls for deep, atmospheric and emotional tracks.",
            "icon": "🌙💧",
            "theme": "rain-night",
        },
        "Clouds": {
            "headline": "Mellow Overcast Floating State",
            "desc": f"Soft filtered light and {temp}°C overcast weather set a relaxed, floating ambient backdrop.",
            "icon": "☁️",
            "theme": "clouds",
        },
        "Snow": {
            "headline": "Winter Serenade & Warm Glow",
            "desc": f"Chilly {temp}°C winter air invites snug acoustic warmth and cinematic comfort.",
            "icon": "❄️",
            "theme": "snow",
        },
        "Thunderstorm": {
            "headline": "Electric Storm Surge",
            "desc": f"Dramatic lightning and rumbling skies pair with high-voltage, powerful resonant beats.",
            "icon": "⛈️",
            "theme": "storm",
        },
        "Atmosphere": {
            "headline": "Ethereal Mist & Cinematic Drift",
            "desc": f"Hazy, atmospheric skies call for mysterious, dream-pop and textured ambient sounds.",
            "icon": "🌫️",
            "theme": "mist",
        },
    }

    key = get_weather_mood_key(weather_info)
    return mood_map.get(key, mood_map["Clear_Day"])


# --- Dynamic Music Recommendation Engine ------------------------------

def format_duration(millis):
    """Format track duration from milliseconds to mm:ss."""
    if not millis or not isinstance(millis, (int, float)):
        return ""
    total_seconds = int(millis // 1000)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def get_dynamic_music_recommendations(weather_info, genre="Pop", count=25, seed_offset=0):
    """
    Fetch a rich, diverse, and non-repeated list of music tracks tailored to the weather & genre.
    Combines multiple queries, deduplicates by title and artist, and enriches metadata.
    """
    mood_key = get_weather_mood_key(weather_info)
    genre_data = GENRE_WEATHER_CATALOG.get(genre, GENRE_WEATHER_CATALOG["Pop"])
    artist_pool = genre_data.get(mood_key, genre_data.get("Clear_Day", ["Taylor Swift"]))

    # Shuffle the artist pool with offset so repeated clicks yield fresh discoveries
    pool = list(artist_pool)
    random.seed(seed_offset if seed_offset else None)
    random.shuffle(pool)

    # Pick top artists/queries from pool to query iTunes
    selected_queries = pool[:4]

    tracks_per_query = max(10, (count // len(selected_queries)) + 6)
    seen_track_keys = set()
    aggregated_tracks = []

    for query in selected_queries:
        url = "https://itunes.apple.com/search"
        params = {
            "term": query,
            "entity": "song",
            "limit": tracks_per_query,
        }
        try:
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code != 200:
                continue
            data = resp.json()
        except requests.RequestException:
            continue

        for item in data.get("results", []):
            title = item.get("trackName", "").strip()
            artist = item.get("artistName", "").strip()
            if not title or not artist:
                continue

            # Normalized deduplication key
            dedup_key = f"{title.lower()}__{artist.lower()}"
            track_id = item.get("trackId")
            if dedup_key in seen_track_keys or track_id in seen_track_keys:
                continue

            seen_track_keys.add(dedup_key)
            if track_id:
                seen_track_keys.add(track_id)

            # High-res artwork (replace 100x100 with 600x600 for retina displays)
            raw_art = item.get("artworkUrl100", "")
            hi_res_art = raw_art.replace("100x100bb.jpg", "600x600bb.jpg").replace("100x100", "600x600")

            duration = format_duration(item.get("trackTimeMillis"))
            release_year = item.get("releaseDate", "")[:4] if item.get("releaseDate") else ""

            aggregated_tracks.append({
                "id": track_id or dedup_key,
                "title": title,
                "artist": artist,
                "album": item.get("collectionName", "Single / EP"),
                "preview": item.get("previewUrl"),
                "link": item.get("trackViewUrl"),
                "artwork": hi_res_art,
                "duration": duration,
                "year": release_year,
                "genre": item.get("primaryGenreName", genre),
                "matched_query": query,
            })

            if len(aggregated_tracks) >= count * 2:
                break

    # Fallback to general genre/hits query if specific pool searches yielded no tracks
    if not aggregated_tracks:
        backup_query = f"{genre} hits"
        try:
            resp = requests.get(
                "https://itunes.apple.com/search",
                params={"term": backup_query, "entity": "song", "limit": count},
                timeout=5,
            )
            if resp.status_code == 200:
                for item in resp.json().get("results", []):
                    title = item.get("trackName", "").strip()
                    artist = item.get("artistName", "").strip()
                    if not title or not artist:
                        continue
                    raw_art = item.get("artworkUrl100", "")
                    hi_res_art = raw_art.replace("100x100bb.jpg", "600x600bb.jpg").replace("100x100", "600x600")
                    aggregated_tracks.append({
                        "id": item.get("trackId") or f"{title}__{artist}",
                        "title": title,
                        "artist": artist,
                        "album": item.get("collectionName", "Single / EP"),
                        "preview": item.get("previewUrl"),
                        "link": item.get("trackViewUrl"),
                        "artwork": hi_res_art,
                        "duration": format_duration(item.get("trackTimeMillis")),
                        "year": item.get("releaseDate", "")[:4] if item.get("releaseDate") else "",
                        "genre": item.get("primaryGenreName", genre),
                        "matched_query": backup_query,
                    })
        except Exception:
            pass

    # Prioritize tracks with audio previews first, while keeping track diversity
    with_preview = [t for t in aggregated_tracks if t["preview"]]
    without_preview = [t for t in aggregated_tracks if not t["preview"]]

    # Interleave / combine to ensure high quality
    combined = with_preview + without_preview
    final_tracks = combined[:count]

    return final_tracks


# --- Backward Compatibility Helpers ------------------------------------

def map_weather_to_music(weather_info, genre="Pop"):
    """Legacy helper returning a single search keyword."""
    mood_key = get_weather_mood_key(weather_info)
    genre_data = GENRE_WEATHER_CATALOG.get(genre, GENRE_WEATHER_CATALOG["Pop"])
    pool = genre_data.get(mood_key, ["Taylor Swift"])
    return pool[0] if pool else "Taylor Swift"


def get_itunes_tracks(search_query, limit=10):
    """Legacy helper returning track list for a single query."""
    if not search_query:
        return []
    url = "https://itunes.apple.com/search"
    params = {"term": search_query, "entity": "song", "limit": limit}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return []

    data = response.json()
    songs = []
    seen = set()
    for track in data.get("results", []):
        t_name = track.get("trackName", "Unknown")
        a_name = track.get("artistName", "Unknown")
        key = f"{t_name.lower()}__{a_name.lower()}"
        if key in seen:
            continue
        seen.add(key)
        artwork = track.get("artworkUrl100", "").replace("100x100", "500x500")
        songs.append({
            "title": t_name,
            "artist": a_name,
            "album": track.get("collectionName", "Unknown"),
            "preview": track.get("previewUrl"),
            "link": track.get("trackViewUrl"),
            "artwork": artwork,
        })
    return songs


if __name__ == "__main__":
    city = input("Enter your city: ")
    weather_data = get_weather_and_time(city)
    if weather_data:
        print(f"Weather in {weather_data['city']}: {weather_data['temperature']}°C, {weather_data['condition']} ({weather_data['time_of_day']})")
        recs = get_dynamic_music_recommendations(weather_data, "Pop", count=15)
        print(f"\n🎵 Found {len(recs)} unique dynamic tracks:\n")
        for i, s in enumerate(recs, 1):
            print(f"{i}. {s['title']} — {s['artist']} ({s['duration']}) [Preview: {'Yes' if s['preview'] else 'No'}]")
    else:
        print("❌ Could not fetch weather.")