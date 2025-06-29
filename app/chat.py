#!/usr/bin/env python3

"""This is the main entry point for the Chainlit application."""

import chainlit as cl
from typing import List, Dict, Any
import json

# Import the compiled workflow from the new location
from app.agent_workflow import workflow

@cl.on_message
async def on_message(msg: cl.Message):
    """
    This function is called when a message is received from the client.
    It processes the user message using the LangGraph workflow.

    Returns:
        None
    """
    if not files:
        await cl.Message(content="No file uploaded.").send()
        return

    uploaded_file = files[0]  # Assuming only one file upload at a time
    file_name = uploaded_file.name

    await cl.Message(content=f"Processing file: {file_name}...").send()

    # Prepare the initial state for the LangGraph workflow
    # Replace with actual data extraction logic
    # Note: The LangGraph AgentState expects a 'messages' key.
    # We'll pass the file-related data within the initial message content for now,
    # as a simplified way to get data into the graph.
    # In a real application, the initial state structure might be different
    # to better accommodate structured data.
    initial_state: Dict[str, Any] = {
        "messages": [("user", json.dumps({
            "fileName": file_name,
            "content": msg.content # Include user message content
        }))],
        "report": None # Report will be populated by the agent
    }

    msg = cl.Message(content="")
    await msg.send()

    # Invoke the LangGraph workflow and stream the output
    async for chunk in workflow.astream(initial_state):
        # The structure of the chunk depends on how your agents update the state.
        # If your agents add messages to the 'messages' list in the state,
        # you can process them here.
        if "messages" in chunk:
            for message in chunk["messages"]:
                # Check if the message is from the assistant and contains the report
                if isinstance(message, tuple) and message[0] == "assistant" and isinstance(message[1], dict) and "report" in message[1]:
                    formatted_report = json.dumps(message[1]["report"], indent=2, ensure_ascii=False)
                    await msg.stream_token(f"{formatted_report}")
                elif isinstance(message, tuple) and message[0] == "assistant":
                    await msg.stream_token(f"{message[1]}")
