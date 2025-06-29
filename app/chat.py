#!/usr/bin/env python3

"""This is the main entry point for the Chainlit application."""

import chainlit as cl
from typing import List

# Assuming this import path is correct after previous steps
from agents import workflow

@cl.on_message
async def on_message(msg: cl.Message):
    """This function is called when a message is received from the client.

    It sends a response back to the client with the received message content.

    Args:
        msg (cl.Message): The message received from the client.

    Returns:
        None
    """
    if not files:
        await cl.Message(content="No file uploaded.").send()
        return

    uploaded_file = files[0]  # Assuming only one file upload at a time
    file_name = uploaded_file.name

    # In a real application, you would parse the CSV and extract:
    # powerQualityDataSummary, identifiedRegulations, and languageCode
    # For this example, we'll use placeholder values.
    # You would also need to handle potential errors during file processing.

    await cl.Message(content=f"Processing file: {file_name}...").send()

    # Prepare the initial state for the LangGraph workflow
    # Replace with actual data extraction logic
    initial_state: StateDict = {
        "fileName": file_name,
        "powerQualityDataSummary": "Placeholder summary of power quality data from CSV.",
        "identifiedRegulations": ["Resolução Normativa nº 956/2021", "PRODIST Módulo 8"],
        "languageCode": "pt-BR", # Default language
        "report": None # Report will be populated by the agent
    }

    msg = cl.Message(content="")
    await msg.send()

    # Invoke the LangGraph workflow and stream the output
    async for chunk in workflow.astream(initial_state):
        # The structure of chunk depends on your LangGraph definition
        # You'll need to adapt this based on how your agent yields output
        # For example, if your agent yields a dictionary with a 'report' key:
        if "report" in chunk and chunk["report"] is not None:
            # Assuming the report is the final JSON output
            report_json = chunk["report"]
            # You might want to format this JSON for better display
            formatted_report = json.dumps(report_json, indent=2, ensure_ascii=False)
            await msg.stream_token(f"{formatted_report}")
    await cl.Message(content=f"Received: {message.content}").send()
