#!/usr/bin/env python3

"""This is the main entry point for the Chainlit application.

Functions:
    - on_message: Handles the message from the user.
    - create_session: Creates a new session.
    - get_agent_session: Gets the agent session.
    - get_agent_runner: Gets the agent runner.
    - logger: Logger instance.

Variables:
    - default_user_id: The default user id.
    - logger: Logger instance.
    - app: Chainlit app instance.
    - coordinator: Coordinator agent instance.
    - session_service: Session service instance.
    - agent_runner: Agent runner instance.
    - agent_session: Agent session instance.
    - content: Content instance.
    - event: Event instance.
    - user: User instance.
    - user_id: User id.
"""
import os
from typing import Optional

import chainlit as cl
from chainlit.server import app
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents import coordinator
from app.utils.logger import Logger

logger = Logger(__name__)

async def create_session(user_id: str):
    """Method use to create a new session.

    Args:
        user_id (str): The user id.
    
    Returns:
        Session: The new session.

    Raises:
        Exception: If the session cannot be created.
    """
    try:
        session_service: InMemorySessionService = app.state.session_service
        logger.info(f"Session created: {cl.context.session.id}")
        return await session_service.create_session(user_id=user_id, session_id=cl.context.session.id)
    except Exception as e:
        logger.error(f"Error creating session: {e}")

async def get_agent_session(user_id: str, session_id: str):
    """Method use to get the agent session.

    Args:
        user_id (str): The user id.
        session_id (str): The session id.
    
    Returns:
        Session: The agent session.
    """
    current_session = None
    try:
        session_service: InMemorySessionService = app.state.session_service
        current_session = await session_service.get_session(user_id=user_id, session_id=session_id)
    except AttributeError:
        logger.error("Session service not initialized.")
        
    if not current_session:
        return await create_session(user_id=user_id)

async def get_agent_runner(user_id: str):
    """Method use to get the agent runner.

    Args:
        user_id (str): The user id.
    
    Returns:
        Runner: The agent runner.
    """
    session_service = app.state.session_service
    agent_session = await get_agent_session(
        user_id=user_id,
        session_id=cl.context.session.id
    )

    agent_runner = Runner(
        app_name=os.getenv("APP_NAME"),
        agent=coordinator,
        session_service=session_service,
        session=agent_session
    )

    return agent_runner

@cl.oauth_callback
def oauth_callback(
        provider_id: str,
        token: str,
        raw_user_data: dict[str, str],
        default_user: cl.User,
    ) -> Optional[cl.User]:
    """Method use to handle the oauth callback.

    Args:
        provider_id (str): The provider id.
        token (str): The token.
        raw_user_data (dict[str, str]): The raw user data.
        default_user (cl.User): The default user.
    
    Returns:
        Optional[cl.User]: The user.
    """
    return default_user

@cl.on_message
async def on_message(message: cl.Message):
    """Method use to handle the message from the user.

    Args:
        message (cl.Message): The message from the user.
    """
    user = cl.user_session.get('user')
    user_id = user.identifier

    if message.elements:
        message.content += f"\n arquivo anexado: {message.elements[0]}"
        logger.info(f"Arquivo anexado: {message.elements[0]}")

    content = types.Content(role="user", parts=[types.Part(text=message.content)])
    
    agent_runner = await get_agent_runner(user_id=user_id)

    async for event in agent_runner.run_async(user_id=user_id, new_message=content, session_id=cl.context.session.id):
        if event.is_final_response() and event.content:
            await cl.Message(content=event.content.parts[0].text).send()
        elif event.is_error():
            logger.error(f"Error: {event.error_details}")
            await cl.Message(content=f"Error: {event.error_details}").send()