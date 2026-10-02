# Family-Friendly Travel Concierge 🧳🏖️

An intelligent, multi-tool ADK (Agent Development Kit) agent designed to help families plan kid-approved vacations, find stroller-accessible attractions, manage travel budgets, generate souvenir postcards & destination videos, and remember dietary restrictions across sessions.

![Family Travel Concierge Demo](agent_demo.gif)

---

## ✨ Features & Implemented Services

### 🧠 1. Cross-Session Long-Term Memory (Vertex AI Memory Bank)
- **Persistent Preferences**: Remembers family dietary restrictions, health requirements, and allergies across sessions via `VertexAiMemoryBankService` and `PreloadMemoryTool`.
- **Automatic Preference Recall**: Automatically applies remembered preferences (e.g., peanut allergy, gluten sensitivity) to all activity, dining, and itinerary recommendations.

### 🗄️ 2. Family Activities Database (Google Cloud Firestore)
- **Database Tools**:
  - `search_family_activities`: Filter attractions by city, category, stroller accessibility, and maximum cost.
  - `add_family_activity`: Add new kid-approved destinations to the community database.
  - `get_family_activity_details`: Retrieve full details for specific activities.

### 🖼️ 3. AI Souvenir Postcard Generation (Vertex AI Imagen / Gemini)
- **Tool**: `generate_family_postcard`
- **Model**: `gemini-3.1-flash-lite-image` in `global` location.
- **Dual Export**: Saves high-res souvenir images to the ADK Playground Artifacts panel (`tool_context.save_artifact`) and uploads directly to Google Cloud Storage for public HTTPS embedding.

### 🎬 4. Destination Video Preview Generation (Google Omni Model)
- **Tool**: `generate_destination_video`
- **Model**: `gemini-omni-flash-preview` in `global` location via Vertex AI Interactions API.
- **Dual Export**: Saves generated 3-second MP4 video previews to the Artifacts panel and uploads to Cloud Storage for public URL sharing.

### ☁️ 5. Cloud Media Storage (Google Cloud Storage)
- Direct byte stream uploads (`upload_from_string`) to a public GCS bucket (`family-travel-media-qwiklabs-gcp-02-81e69cac24de`).

### 🗺️ 6. Location & Navigation (Google Maps Platform)
- **Tools**:
  - `geocode_address`: Converts addresses to precise geographic coordinates.
  - `find_nearby_places`: Discovers kid-friendly points of interest near specific locations.

### 🌤️ 7. Live Weather Integration (External Weather API)
- **Tool**: `get_live_weather`: Queries real-time weather forecasts to ensure ideal outdoor activity conditions.

### 💰 8. Family Budget Calculator
- **Tool**: `calculate_family_budget`: Computes total trip costs (food, lodging, activities, contingency reserves) with broken-down per-person metrics.

### ⚡ 9. Code Execution Sandbox
- Executes dynamic Python code calculations in a isolated `AgentEngineSandboxCodeExecutor` environment.

### 🎨 10. Rich Generative UI (A2UI Framework)
- Formats agent responses into structured, mobile-friendly cards, columns, rows, text, and images using `A2uiSchemaManager` (v0.8).

---

## 🛠️ Project Structure

```
.
├── app/
│   ├── agent.py            # Main ADK Agent setup, instructions, and tool bindings
│   ├── a2ui_utils.py       # A2UI callback schema manager and renderer
│   ├── db_tools.py         # Firestore database tools for family activities
│   ├── image_tools.py      # Vertex AI Image generation & GCS upload tool
│   ├── video_tools.py      # Google Omni video generation & GCS upload tool
│   ├── maps_tools.py       # Google Maps geocoding and places discovery tools
│   ├── external_tools.py   # Live weather lookup tool
│   └── budget_tools.py     # Family budget calculation tool
├── frontend/
│   ├── main.py             # FastAPI proxy connecting browser to agent via A2A protocol
│   ├── requirements.txt    # Python dependencies for the web frontend
│   └── static/
│       └── index.html      # Responsive chat interface with interactive category chips
├── agents-cli-manifest.yaml# ADK agent configuration manifest
└── agent_demo.gif          # Looping demo recording of the web interface
```

---

## 🚀 Local Setup & Running Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ (for Playwright / frontend testing)
- Google Cloud SDK (`gcloud`) authenticated with access to Vertex AI, Firestore, and Cloud Storage.

### 1. Install Agent Dependencies & Set Environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure GCP Credentials
```bash
gcloud auth login
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
```

### 3. Run the FastAPI Frontend Proxy Locally
```bash
cd frontend
pip install -r requirements.txt

# Set environment pointing to your deployed Agent Engine resource or local runner
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-id>/locations/<location>/reasoningEngines/<id>"
export AGENT_DIRECTORY="app"

python main.py
```

Open a web browser to the local port displayed by FastAPI (typically port 8080) to interact with the Family-Friendly Travel Concierge!
