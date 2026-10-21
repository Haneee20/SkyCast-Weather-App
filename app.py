
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/suggest")
def suggest():
    query = request.args.get("q", "").strip()

    if len(query) < 2:
        return jsonify([])

    try:
        response = requests.get(
            GEO_URL,
            params={
                "name": query,
                "count": 10,
                "language": "en",
                "format": "json"
            },
            timeout=15
        )
        response.raise_for_status()

        places = response.json().get("results", [])

        results = []

        for place in places:
            results.append({
                "name": place.get("name", ""),
                "country": place.get("country", ""),
                "region": place.get("admin1", ""),
                "latitude": place["latitude"],
                "longitude": place["longitude"]
            })

        return jsonify(results)

    except requests.RequestException:
        return jsonify({"error": "Location search failed"}), 502


@app.route("/weather")
def weather():
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")

    if not latitude or not longitude:
        return jsonify({"error": "Choose a location first"}), 400

    try:
        response = requests.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "wind_speed_10m"
                ),
                "timezone": "auto"
            },
            timeout=15
        )
        response.raise_for_status()

        data = response.json()
        current = data.get("current", {})

        return jsonify({
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind": current.get("wind_speed_10m")
        })

    except requests.RequestException:
        return jsonify({"error": "Could not load weather data"}), 502


if __name__ == "__main__":
    app.run(debug=True)
