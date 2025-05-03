#!/usr/bin/env python3

"""This is the main entry point for the Chainlit application."""

import chainlit as cl


@cl.on_message
async def on_message(message: cl.Message):
    """This function is called when a message is received from the client.

    It sends a response back to the client with the received message content.

    Args:
        message (cl.Message): The message received from the client.

    Returns:
        None
    1. The function is decorated with `@cl.on_message`, which registers it as a message handler.
    2. The function takes a single argument, `message`, which is an instance of `cl.Message`.
    3. The function sends a response back to the client using `cl.Message.send()`.
    4. The response contains the content of the received message.
    5. The function is asynchronous, allowing it to handle multiple messages concurrently.
    6. The function does not return any value.
    """
    await cl.Message(content=f"Received: {message.content}").send()
