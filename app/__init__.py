"""This package provides the user interface for the Electric Magnitudes Analyzer toll.

Modules:
    - app.__version__: Defines the version of the application.
    - app.__init__: Initializes the application.
    - app.chat: Defines the main entry point for the application.
    - app.utils.logger: Defines the logger for the application.
    - app.agents.coordinator: Defines the coordinator agent.
    - app.agents.tools: Defines the tools for the coordinator agent.
    - app.agents.sub_agents: Defines the sub agents for the coordinator agent.

Functions:
    - lifespan: Method use to initialize the application.
    - health_check: Health check endpoint.
    - agent_info: Agent info endpoint.

Variables:
    - BASE_DIR: Base directory of the application.
    - AGENTS_BASE_DIR: Agents base directory of the application.
    - logger: Logger instance.
    - api: FastAPI application.
    - mount_chainlit: Mounts the Chainlit application.
    - get_fast_api_app: Gets the FastAPI application.
    - InMemorySessionService: In-memory session service.
"""
import os
from contextlib import asynccontextmanager

from chainlit.utils import mount_chainlit
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.sessions import InMemorySessionService

from .agents import coordinator
from .utils.logger import Logger

logger = Logger(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
AGENTS_BASE_DIR = os.path.abspath(os.path.join(BASE_DIR, 'agents'))

@asynccontextmanager
async def lifespan(api: FastAPI):
    """Method use to initialize the application.

    Args:
        api (FastAPI): The FastAPI application.
    """
    logger.info("Initializing application...")
    try:
        api.state.session_service = InMemorySessionService()
        logger.info("Database session service initialized successfully.")
    except Exception as e:
        logger.error(f"Database session service initialized failed: {e}")
    
    yield
    logger.info("Application shutting down...")
    await api.state.session_service.close()
    logger.info("Database session service closed successfully.")
    logger.info("Application shut down successfully.")

api: FastAPI = get_fast_api_app(
    agents_dir=AGENTS_BASE_DIR, 
    allow_origins=["*"],
    lifespan=lifespan,
    trace_to_cloud=True,
    web=False
)

@api.get('/healthcheck')
async def health_check():
    """Health check endpoint."""
    return {'status': 'ok'}

@api.get('/agent-info')
async def agent_info():
    """Agent info endpoint.
    
    Returns:
        dict: The agent information.
    """
    return {
        "name": coordinator.name,
        "description": coordinator.description,
        "model": coordinator.model,
        "tools": [tool.__name__ for tool in coordinator.tools]
    }

mount_chainlit(app=api, target="app/chat.py", path="/")
