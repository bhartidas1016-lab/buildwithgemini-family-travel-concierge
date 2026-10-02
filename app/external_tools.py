"""External API tools for Family-Friendly Travel Concierge.

Integrates real-time public APIs from public-apis (Open-Meteo live weather & geocoding).
"""

import os
import urllib.parse
import urllib.request
import json


# Map WMO weather codes to human-readable family friendly descriptions
WEATHER_CODES = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    45: "Foggy 🌫️",
    48: "Depositing rime fog 🌫️",
    51: "Light drizzle 🌦️",
    53: "Moderate drizzle 🌦️",
    55: "Dense drizzle 🌧️",
    61: "Slight rain 🌧️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain 🌧️",
    71: "Slight snow ❄️",
    73: "Moderate snow ❄️",
    75: "Heavy snow ❄️",
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌧️",
    82: "Violent rain showers ⛈️",
    95: "Thunderstorm 🌩️",
}


def get_live_weather(city: str) -> str:
    """Fetch live real-time weather information for a destination city using the free Open-Meteo public API.

    Args:
        city: Name of the destination city (e.g., 'San Diego', 'Tokyo', 'Orlando', 'Paris', 'New York').

    Returns:
        Formatted string containing current live temperature (°C and °F), wind speed, and weather conditions.
    """
    # Check for optional API key in environment variable as requested
    api_key = os.getenv("WEATHER_API_KEY", os.getenv("OPEN_METEO_API_KEY", ""))

    headers = {"User-Agent": "FamilyTravelConciergeAgent/1.0"}

    try:
        # Step 1: Geocode city name to lat/long
        encoded_city = urllib.parse.quote(city.strip())
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1"
        if api_key:
            geo_url += f"&apikey={api_key}"

        geo_req = urllib.request.Request(geo_url, headers=headers)
        with urllib.request.urlopen(geo_req, timeout=5) as response:
            geo_data = json.loads(response.read().decode())

        results = geo_data.get("results")
        if not results:
            return f"Could not find coordinates for city '{city}'."

        location = results[0]
        name = location.get("name", city)
        country = location.get("country", "")
        lat = location.get("latitude")
        lon = location.get("longitude")

        # Step 2: Fetch current weather for coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        if api_key:
            weather_url += f"&apikey={api_key}"

        weather_req = urllib.request.Request(weather_url, headers=headers)
        with urllib.request.urlopen(weather_req, timeout=5) as response:
            weather_data = json.loads(response.read().decode())

        current = weather_data.get("current_weather", {})
        temp_c = current.get("temperature", 0.0)
        temp_f = (temp_c * 9 / 5) + 32
        wind_speed = current.get("windspeed", 0.0)
        code = current.get("weathercode", 0)
        condition = WEATHER_CODES.get(code, "Clear")

        location_str = f"{name}, {country}" if country else name
        return (
            f"Live Weather for {location_str}:\n"
            f"- Condition: {condition}\n"
            f"- Temperature: {temp_f:.1f}°F ({temp_c:.1f}°C)\n"
            f"- Wind Speed: {wind_speed} km/h"
        )

    except Exception as e:
        return f"Error fetching live weather for '{city}': {str(e)}"
