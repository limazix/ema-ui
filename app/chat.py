#!/usr/bin/env python3

"""This is the main entry point for the Chainlit application."""

from typing import Optional

import chainlit as cl
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.coordinator_agent import coordinator
from app.utils.logger import Logger

logger = Logger(__name__)

@cl.oauth_callback
async def oauth_callback(
        provider_id: str,
        token: str,
        raw_user_data: dict[str, str],
        default_user: cl.User,
    ) -> Optional[cl.User]:
        """Method use to handle the OAuth callback."""
        return default_user

@cl.on_chat_start
async def on_chat_start():
    """Method use to start the Chainlit application."""
    user = cl.user_session.get('user')
    sessio_service = InMemorySessionService()
    agent_session = await sessio_service.create_session(
        session_id=cl.context.session.id,
        user_id=user.id,
        app_name=cl.__name__
    )
    agent_runner = Runner(
        app_name=cl.__name__,
        agent=coordinator,
        session_service=sessio_service
    )

    cl.context.agent_session = agent_session
    cl.context.agent_runner = agent_runner

@cl.on_message
async def on_message(message: cl.Message):
    """Method use to handle the message from the user.

    Args:
        message (cl.Message): The message from the user.
    """
    user = cl.user_session.get('user')
    content = types.Content(role="user", parts=[types.Part(text=message.content)])

    async for event in cl.context.agent_runner.run_assync(user_id=user.id, new_message=content, session_id=cl.context.session.id):
        if event.is_final_response() and event.content:
            await cl.Message(content=event.content).send()
        elif event.is_error():
            logger.error(f"Error: {event.error_details}")
            await cl.Message(content=f"Error: {event.error_details}").send()