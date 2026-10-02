"""Google Maps Geocoding & Places (New) function tools for Family-Friendly Travel Concierge.

Reads API key from GOOGLE_MAPS_API_KEY environment variable.
"""

import os
import json
import urllib.parse
import urllib.request


def geocode_address(address: str) -> str:
    """Turn a street address or location name into geographic coordinates (latitude and longitude).

    Args:
        address: The address or location name to geocode (e.g. 'Balboa Park, San Diego, CA' or '1600 Amphitheatre Pkwy').

    Returns:
        Formatted summary with key fields: formatted address and location coordinates (latitude, longitude).
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    encoded_address = urllib.parse.quote(address.strip())
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FamilyTravelConcierge/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

        results = data.get("results", [])
        if not results:
            return f"No geocoding results found for address '{address}'."

        first_result = results[0]
        formatted_address = first_result.get("formatted_address", "")
        location = first_result.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        return (
            f"Geocoding Results for '{address}':\n"
            f"- Address: {formatted_address}\n"
            f"- Location: latitude {lat}, longitude {lng}"
        )
    except Exception as e:
        return f"Error calling Geocoding API for '{address}': {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "tourist_attraction",
    radius_meters: float = 5000.0,
) -> str:
    """Find nearby places of a given type around a geographic location using Places API (New).

    Args:
        latitude: Latitude coordinate of the search center.
        longitude: Longitude coordinate of the search center.
        place_type: Type of place to search for (e.g., 'tourist_attraction', 'zoo', 'museum', 'park', 'amusement_park', 'restaurant').
        radius_meters: Search radius in meters (default 5000.0).

    Returns:
        Formatted summary of nearby places with key fields (name, address, location coordinates).
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    places_url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        "User-Agent": "FamilyTravelConcierge/1.0",
    }

    body_data = {
        "includedTypes": [place_type.strip().lower()],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        req = urllib.request.Request(
            places_url,
            data=json.dumps(body_data).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode())

        places = res_data.get("places", [])
        if not places:
            return f"No nearby places of type '{place_type}' found within {radius_meters}m of ({latitude}, {longitude})."

        formatted = [f"Found {len(places)} nearby '{place_type}' place(s):"]
        for p in places:
            display_name = p.get("displayName", {}).get("text", "Unknown")
            fmt_address = p.get("formattedAddress", "N/A")
            loc = p.get("location", {})
            plat = loc.get("latitude")
            plng = loc.get("longitude")

            formatted.append(
                f"- Name: {display_name}\n"
                f"  Address: {fmt_address}\n"
                f"  Location: lat {plat}, lng {plng}"
            )

        return "\n\n".join(formatted)

    except Exception as e:
        return f"Error calling Places API (New) for location ({latitude}, {longitude}): {str(e)}"
