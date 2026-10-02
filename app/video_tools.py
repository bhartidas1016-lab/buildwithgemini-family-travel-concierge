"""Video generation tool for Family-Friendly Travel Concierge.

Uses Google's Omni model (gemini-omni-flash-preview) in location='global'.
Saves the generated video as an artifact using tool_context.save_artifact,
and uploads the video bytes directly to GCS returning its public https URL.
"""

import base64
import time
import google.auth
import google.auth.transport.requests
import httpx
from google.cloud import storage
from google.adk.tools import ToolContext
from google.genai import types

PUBLIC_BUCKET_NAME = "family-travel-media-qwiklabs-gcp-02-81e69cac24de"
PROJECT_ID = "qwiklabs-gcp-02-81e69cac24de"


async def generate_destination_video(
    prompt: str,
    tool_context: ToolContext,
) -> str:
    """Generate a short video preview of a family travel destination or attraction using Google's Omni model.

    Args:
        prompt: Detailed description of the destination video to generate (e.g. 'A short video preview of a stroller-friendly path and splash pad at San Diego Zoo').
        tool_context: Injected ADK ToolContext used to save artifacts.

    Returns:
        The public HTTPS URL (https://storage.googleapis.com/<bucket>/<object>) of the generated video.
    """
    credentials, _ = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)

    url = f"https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/global/interactions"
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "gemini-omni-flash-preview",
        "input": [
            {"type": "text", "text": prompt}
        ],
        "response_format": [
            {
                "type": "video",
                "aspect_ratio": "16:9",
                "duration": "3s"
            }
        ],
        "generation_config": {
            "video_config": {
                "task": "text_to_video"
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body, timeout=180.0)

    if response.status_code != 200:
        return f"Error generating video: HTTP {response.status_code} - {response.text[:300]}"

    data = response.json()
    video_bytes = None
    for step in data.get("steps", []):
        if step.get("type") == "model_output":
            for content in step.get("content", []):
                if content.get("type") == "video" and "data" in content:
                    video_bytes = base64.b64decode(content["data"])
                    break

    if not video_bytes:
        return "Error: Failed to extract video bytes from gemini-omni-flash-preview response."

    timestamp = int(time.time())
    filename = f"video_{timestamp}.mp4"

    # (1) Save video bytes as artifact so it appears in Playground Artifacts panel
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
    )

    # (2) Upload video bytes directly to public Cloud Storage bucket without local file writes
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(PUBLIC_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    public_url = f"https://storage.googleapis.com/{PUBLIC_BUCKET_NAME}/{filename}"
    return public_url
