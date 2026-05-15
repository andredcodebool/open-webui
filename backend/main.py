import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# App metadata
APP_NAME = "Open WebUI"
APP_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    log.info(f"Starting {APP_NAME} v{APP_VERSION}")
    # Startup: initialize resources, DB connections, etc.
    yield
    # Shutdown: cleanup resources
    log.info(f"Shutting down {APP_NAME}")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Open WebUI — a user-friendly interface for interacting with LLMs.",
    lifespan=lifespan,
)

# CORS configuration
# Default to localhost only for personal use instead of wildcard
origins = os.environ.get("CORS_ALLOW_ORIGIN", "http://localhost:3000,http://localhost:8080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["utility"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "version": APP_VERSION}


@app.get("/api/version", tags=["utility"])
async def get_version():
    """Return the current application version."""
    return {"version": APP_VERSION}


# Serve the built frontend if it exists
FRONTEND_BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "build")
if os.path.exists(FRONTEND_BUILD_DIR):
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_BUILD_DIR, html=True),
        name="static",
    )
    log.info(f"Serving frontend from: {FRONTEND_BUILD_DIR}")
else:
    log.warning(
        "Frontend build directory not found. "
        "Run `npm run build` to generate the frontend assets."
    )


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("HOST", "127.0.0.1")  # Personal use: bind to localhost by default instead of 0.0.0.0
    port = int(os.environ.get("PORT", 8080))

    # Use DEBUG log level in dev mode so it's easier to trace issues locally
    log_level = "debug" if os.environ.get("ENV", "prod") == "dev" else "info"

    log.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.environ.get("ENV", "prod") == "dev",
        forwarded_allow_ips="*",
        log_level=log_level,
    )
