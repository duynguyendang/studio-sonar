import os
import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as main_router
from src.api.tracking_routes import router as tracking_router
from src.api.messaging_webhooks import router as messaging_router
from src.core.config import settings

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def _seed_registry_on_startup():
    """Seeds the canonical sample surveillance registry into BigQuery at startup (idempotent)."""
    try:
        from src.core.config import settings as s
        from google.cloud import bigquery
        from src.data.registry_seeder import ensure_registry_seeded
        client = bigquery.Client(project=s.gcp_project_id)
        result = ensure_registry_seeded(client, s.gcp_project_id, s.bigquery_dataset)
        logging.getLogger("studiosonar.main").info(
            f"Startup BigQuery registry seed -> channels inserted: {result['inserted_channels']}, videos inserted: {result['inserted_videos']}"
        )
    except Exception as e:
        logging.getLogger("studiosonar.main").warning(f"Startup BigQuery registry seed skipped: {e}")


app = FastAPI(
    title="StudioSonar Taskmaster API & Dashboard",
    description="Autonomous Media Intelligence & Real-time Action Agent for Google Cloud",
    version="1.0.0"
)

_seed_registry_on_startup()

# CORS middleware for local debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def serve_dashboard_ui():
    """Serves the interactive StudioSonar Asset Tracking Command Center web interface with strict zero-cache headers."""
    template_path = "src/templates/dashboard.html"
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        resp = HTMLResponse(content=content)
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp
@app.get("/healthz")
def healthcheck():
    return {
        "status": "healthy",
        "service": "studiosonar-taskmaster",
        "architecture": "Google ADK Multi-Agent Team",
        "agents": ["AnomalyDetectorAgent", "PRCrisisStrategistAgent", "ViralContentCreatorAgent", "ChannelSentinelAgent"],
        "model": "gemini-3.7-flash"
    }

app.include_router(main_router)
app.include_router(tracking_router)
app.include_router(messaging_router)





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host=settings.host, port=settings.port, reload=True)
