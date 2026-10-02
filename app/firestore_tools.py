"""Firestore function tools for Family-Friendly Travel Concierge.

All tools hardcode the GCP Project ID string to avoid project number issues on Agent Platform.
"""

from typing import Optional
from google.cloud import firestore

# Hardcoded Project ID string as required for Agent Platform compatibility
PROJECT_ID = "qwiklabs-gcp-02-81e69cac24de"
COLLECTION_NAME = "family_activities"


def _get_firestore_client() -> firestore.Client:
    """Helper to initialize the Firestore client with the hardcoded project ID string."""
    return firestore.Client(project=PROJECT_ID)


def search_family_activities(
    destination: str = "",
    category: str = "",
    stroller_accessible_only: bool = False,
) -> str:
    """Search for family-friendly activities from the Firestore database.

    Args:
        destination: City or destination name to filter by (e.g., 'San Diego', 'Orlando', 'New York', 'Tokyo'). Case-insensitive partial match.
        category: Optional category filter (e.g., 'Zoo & Wildlife', 'Museum', 'Park & Rides', 'Nature & Theater').
        stroller_accessible_only: If True, returns only stroller accessible activities.

    Returns:
        Formatted string listing the matching family activities and their details.
    """
    db = _get_firestore_client()
    query_ref = db.collection(COLLECTION_NAME)

    docs = query_ref.stream()
    results = []

    for doc in docs:
        data = doc.to_dict()
        
        # Filter destination if provided
        if destination and destination.lower() not in data.get("destination", "").lower():
            continue
            
        # Filter category if provided
        if category and category.lower() not in data.get("category", "").lower():
            continue
            
        # Filter stroller accessibility if requested
        if stroller_accessible_only and not data.get("stroller_accessible", False):
            continue

        results.append(data)

    if not results:
        return f"No family activities found matching criteria (destination='{destination}', category='{category}', stroller_accessible_only={stroller_accessible_only})."

    formatted = [f"Found {len(results)} family activity/activities:"]
    for item in results:
        stroller_str = "Yes" if item.get("stroller_accessible") else "No"
        formatted.append(
            f"- [{item.get('activity_id')}] {item.get('title')} ({item.get('destination')})\n"
            f"  Category: {item.get('category')} | Min Age: {item.get('min_age')}+ | Rating: {item.get('kid_rating')}/5.0\n"
            f"  Stroller Accessible: {stroller_str} | Price: ${item.get('price_per_child')}/child, ${item.get('price_per_adult')}/adult\n"
            f"  Description: {item.get('description')}"
        )

    return "\n\n".join(formatted)


def add_family_activity(
    title: str,
    destination: str,
    description: str,
    min_age: int = 0,
    stroller_accessible: bool = True,
    kid_rating: float = 5.0,
    category: str = "General",
    price_per_child: float = 0.0,
    price_per_adult: float = 0.0,
) -> str:
    """Add a new family-friendly activity to the Firestore database.

    Args:
        title: Name of the activity or attraction.
        destination: City or location (e.g., 'San Diego', 'Orlando', 'Paris').
        description: Short summary suitable for families with kids.
        min_age: Minimum recommended age for children (default 0).
        stroller_accessible: Whether the venue is stroller friendly (default True).
        kid_rating: Rating out of 5.0 (default 5.0).
        category: Activity category (e.g. 'Theme Park', 'Museum', 'Zoo', 'Beach').
        price_per_child: Ticket price for children in USD.
        price_per_adult: Ticket price for adults in USD.

    Returns:
        Confirmation message with the created activity ID.
    """
    db = _get_firestore_client()
    
    # Generate clean ID
    slug_title = "".join(c.lower() if c.isalnum() else "_" for c in title)[:20].strip("_")
    slug_dest = "".join(c.lower() if c.isalnum() else "_" for c in destination)[:10].strip("_")
    activity_id = f"act_{slug_dest}_{slug_title}"

    activity_data = {
        "activity_id": activity_id,
        "title": title,
        "destination": destination,
        "description": description,
        "min_age": min_age,
        "stroller_accessible": stroller_accessible,
        "kid_rating": kid_rating,
        "category": category,
        "price_per_child": price_per_child,
        "price_per_adult": price_per_adult,
    }

    db.collection(COLLECTION_NAME).document(activity_id).set(activity_data)

    return f"Successfully added new family activity '{title}' ({destination}) with ID '{activity_id}' to Firestore database."


def get_family_activity_details(activity_id: str) -> str:
    """Fetch full details for a specific family activity by ID from Firestore.

    Args:
        activity_id: The unique ID of the activity (e.g. 'act_sd_zoo').

    Returns:
        Formatted details of the requested activity.
    """
    db = _get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(activity_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Activity with ID '{activity_id}' was not found in Firestore."

    data = doc.to_dict()
    stroller_str = "Yes" if data.get("stroller_accessible") else "No"
    return (
        f"Activity Details for '{data.get('title')}':\n"
        f"  ID: {data.get('activity_id')}\n"
        f"  Destination: {data.get('destination')}\n"
        f"  Category: {data.get('category')}\n"
        f"  Description: {data.get('description')}\n"
        f"  Minimum Age: {data.get('min_age')}+\n"
        f"  Stroller Accessible: {stroller_str}\n"
        f"  Kid Rating: {data.get('kid_rating')}/5.0\n"
        f"  Price: ${data.get('price_per_child')}/child, ${data.get('price_per_adult')}/adult"
    )
