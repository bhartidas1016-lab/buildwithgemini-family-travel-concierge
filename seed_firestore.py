"""Seed script for Family-Friendly Travel Concierge Firestore collection.

Seeds sample family activities into the 'family_activities' collection.
"""

from google.cloud import firestore

# Hardcoded Project ID string as required for Agent Platform compatibility
PROJECT_ID = "qwiklabs-gcp-02-81e69cac24de"
COLLECTION_NAME = "family_activities"

SAMPLE_ACTIVITIES = [
    {
        "activity_id": "act_sd_zoo",
        "title": "San Diego Zoo & Wildlife Safari",
        "destination": "San Diego",
        "description": "World-famous zoo with guided bus tours, kangaroo express buses, and dedicated splash pads for toddlers.",
        "min_age": 0,
        "stroller_accessible": True,
        "kid_rating": 4.9,
        "category": "Zoo & Wildlife",
        "price_per_child": 55.0,
        "price_per_adult": 67.0,
    },
    {
        "activity_id": "act_sd_carousel",
        "title": "Balboa Park Mini Train & Carousel",
        "destination": "San Diego",
        "description": "Vintage 1910 carousel and a mini train ride through 1/2 mile of parklands, perfect for quick toddler breaks.",
        "min_age": 1,
        "stroller_accessible": True,
        "kid_rating": 4.7,
        "category": "Park & Rides",
        "price_per_child": 3.0,
        "price_per_adult": 3.0,
    },
    {
        "activity_id": "act_orl_science",
        "title": "Orlando Science Center KidsTown",
        "destination": "Orlando",
        "description": "Interactive water play, orange grove harvesting simulation, and toddler play zone across 11,000 sq ft.",
        "min_age": 0,
        "stroller_accessible": True,
        "kid_rating": 4.8,
        "category": "Museum",
        "price_per_child": 22.0,
        "price_per_adult": 29.0,
    },
    {
        "activity_id": "act_ny_central_park",
        "title": "Central Park Children's Zoo & Marionette Theater",
        "destination": "New York",
        "description": "Gentle petting zoo, climbing rainforest structures, and live marionette puppet theater for young children.",
        "min_age": 2,
        "stroller_accessible": True,
        "kid_rating": 4.6,
        "category": "Nature & Theater",
        "price_per_child": 15.0,
        "price_per_adult": 20.0,
    },
    {
        "activity_id": "act_tokyo_toy",
        "title": "Tokyo Toy Museum & Wooden Playrooms",
        "destination": "Tokyo",
        "description": "Housed in a former elementary school, featuring thousands of touchable wooden toys, cedar wood toy baths, and craft workshops.",
        "min_age": 1,
        "stroller_accessible": True,
        "kid_rating": 4.9,
        "category": "Museum",
        "price_per_child": 8.0,
        "price_per_adult": 11.0,
    },
]


def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    print(f"Seeding Firestore collection '{COLLECTION_NAME}' in project '{PROJECT_ID}'...")
    for act in SAMPLE_ACTIVITIES:
        doc_ref = collection_ref.document(act["activity_id"])
        doc_ref.set(act)
        print(f"  ✓ Seeded activity: {act['title']} ({act['destination']})")

    print("Firestore seeding complete! 🎉")


if __name__ == "__main__":
    seed_database()
