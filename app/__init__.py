"""This package provides the user interface for the Electric Magnitudes Analyzer toll.

Modules:
    - src.__version__: Defines the version of the application.
    - src.app: Contains the main application logic and entry point.
"""
from fastapi import FastAPI
from chainlit.utils import mount_chainlit

api = FastAPI()

mount_chainlit(app=api, target="app/chat.py", path="/")