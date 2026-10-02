"""Image generation tools for Family-Friendly Travel Concierge.

Uses gemini-3.1-flash-lite-image in location='global'.
Saves the generated image as an artifact using tool_context.save_artifact,
and uploads the image bytes directly to GCS returning its public https URL.
"""

import time
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded bucket name string as requested
PUBLIC_BUCKET_NAME = "family-travel-media-qwiklabs-gcp-02-81e69cac24de"


async def generate_family_postcard(
    prompt: str,
    tool_context: ToolContext,
) -> str:
    """Generate a custom family travel souvenir postcard art image using AI.

    Args:
        prompt: Detailed description of the postcard art to generate (e.g. 'A vibrant watercolor family souvenir postcard of San Diego Zoo with giraffes and palm trees').
        tool_context: Injected ADK ToolContext used to save artifacts.

    Returns:
        The public HTTPS URL (https://storage.googleapis.com/<bucket>/<object>) of the generated image.
    """
    # 1. Generate image using gemini-3.1-flash-lite-image in global region
    client = genai.Client(vertexai=True, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"]
        ),
    )

    image_bytes = None
    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                break

    if not image_bytes:
        return "Error: Failed to generate image bytes from model."

    timestamp = int(time.time())
    filename = f"postcard_{timestamp}.png"

    # (1) Save with tool_context.save_artifact so it shows up in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
    )

    # (2) Upload same image bytes to public Cloud Storage bucket without local file writes
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(PUBLIC_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/png")

    public_url = f"https://storage.googleapis.com/{PUBLIC_BUCKET_NAME}/{filename}"
    return public_url
