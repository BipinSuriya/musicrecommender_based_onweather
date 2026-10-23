# 🌦️ Weather Beats — Weather-Driven Music Recommender

A modern Python & Streamlit application that algorithmically curates rich, non-repeating music playlists tailored in real-time to your local sky conditions, temperature, and daylight cycle.

---

## ✨ Features

- 🌦️ **Live Atmospheric Sync:** Real-time temperature, "feels like" temp, humidity, wind speed, weather condition, and day/night cycle via OpenWeatherMap.
- 🎨 **Glassmorphism UI:** Premium modern design system with dynamic mood banners, Google Fonts (`Outfit` & `Plus Jakarta Sans`), and responsive music cards.
- 🎵 **Dynamic Multi-Artist Repertoire:** Diverse catalog mapped across 8 genres (Pop, Rock, Lo-fi, Hip-Hop, Romantic, Tamil, Indie/Acoustic, Electronic/Chill) and 8 weather states (Clear Day, Clear Night, Rain Day, Rain Night, Clouds, Snow, Thunderstorm, Mist/Fog).
- 🔁 **Zero Repeat Guarantee:** Intelligent de-duplication across song title and artist identifiers ensuring clean, unique playlists.
- 🔢 **Custom Playlist Sizing:** Recommend between **10 to 40+ unique songs** at once with a real-time slider.
- 🎲 **Shuffle & Discovery Mode:** One-click re-mix feature to discover fresh tracks for the same weather condition without retyping.
- 🔍 **In-Playlist Search Filter:** Instantly filter songs by track name, artist, or album.
- 🖼️ **Retina-Crisp Artwork:** Upgrades album covers to high-resolution (600x600).
- ▶️ **Audio Previews:** Built-in 30-second audio preview playback.
- 🎧 **Streaming Links:** Instant buttons to listen on **Apple Music** or search on **Spotify**.
- 📍 **Smart Location:** 1-click GPS detection with reverse geocoding + quick-access world city presets.

---

## 🛠️ Tech Stack

- **Frontend & App Framework:** Streamlit, Custom CSS (Glassmorphism & Micro-animations)
- **APIs:** OpenWeatherMap API, Apple Music / iTunes Search API
- **Location:** OpenWeatherMap Reverse Geocoding, `streamlit-geolocation`
- **Language:** Python 3.12+

---

## 📂 Project Structure

```text
c:\Weather\
├── app.py              # Streamlit Web Application & UI/UX interface
├── main.py             # Recommendation engine, weather API & iTunes search
├── README.md           # Documentation
└── requirements.txt    # Project dependencies
```

---

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```      

3. Open `http://localhost:8501` in your browser.
