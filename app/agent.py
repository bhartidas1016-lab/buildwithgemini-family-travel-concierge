# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

import json
from pathlib import Path

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.firestore_tools import (
    search_family_activities,
    add_family_activity,
    get_family_activity_details,
)
from app.budget_tools import calculate_family_budget
from app.external_tools import get_live_weather
from app.maps_tools import geocode_address, find_nearby_places
from app.image_tools import generate_family_postcard
from app.video_tools import generate_destination_video


# Read agent_engine_resource_name from deployment_metadata.json if available
_deployment_metadata_file = Path(__file__).parent.parent / "deployment_metadata.json"
_agent_engine_resource_name = None
if _deployment_metadata_file.exists():
    try:
        with open(_deployment_metadata_file, "r") as _f:
            _metadata = json.load(_f)
            _agent_engine_resource_name = _metadata.get("remote_agent_runtime_id")
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=_agent_engine_resource_name
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are the Family-Friendly Travel Concierge. You help families plan kid-approved trips, "
        "find stroller-accessible attractions, calculate budgets, and discover activities. "
        "You pay special attention to and remember all user dietary restrictions, health requirements, and allergies "
        "(e.g. peanut allergy, gluten sensitivity, dairy allergy, seafood allergy) across sessions, "
        "and actively apply these remembered preferences and allergies to all food, restaurant, activity, and itinerary recommendations. "
        "Use your Firestore tools (`search_family_activities`, `add_family_activity`, `get_family_activity_details`), "
        "budget tools (`calculate_family_budget`), live weather tool (`get_live_weather`), Google Maps tools "
        "(`geocode_address`, `find_nearby_places`), image tool (`generate_family_postcard`), "
        "video tool (`generate_destination_video`), "
        "and code execution sandbox to assist families."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback triggered after agent execution to extract and store durable memories."""
    try:
        await callback_context.add_session_to_memory()
    except (ValueError, Exception):
        pass
    return None


def memory_service_builder():
    """Builds VertexAiMemoryBankService for deployed agent runtime."""
    return VertexAiMemoryBankService(
        project="qwiklabs-gcp-02-81e69cac24de",
        location="us-east1",
        agent_engine_id="335308165518196736",
    )


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        get_live_weather,
        get_current_time,
        search_family_activities,
        add_family_activity,
        get_family_activity_details,
        calculate_family_budget,
        geocode_address,
        find_nearby_places,
        generate_family_postcard,
        generate_destination_video,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

