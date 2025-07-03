import chainlit as cl
from typing import List
import pandas as pd
import chardet

from .logger import Logger

logger = Logger(__name__)

async def handle_uploaded_file(uploaded_file: cl.File) -> dict:
    """
    Handles uploaded files by reading their content for CSV and Excel files.

    Args:
        files: A list of Chainlit File objects.

    Returns:
        A string witth the file content if the file is processed successfully, None otherwise.
    """
    file_content = None

    try:
        encoding = await detect_encoding(uploaded_file.path)
        logger.info(f"Detected encoding: {encoding}")
        with open(uploaded_file.path, 'r', encoding=encoding) as f:
            file_content = f.read()
    except Exception as e:
        logger.error(f"Error processing file {uploaded_file.name}: {e}")
    
    return file_content

async def detect_encoding(file_path: str) -> str:
    """Detects the encoding of a file."""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000)) # Read first 10000 bytes
    return result['encoding'] if result and result['encoding'] else 'utf-8'
