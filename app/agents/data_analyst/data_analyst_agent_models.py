# app/agents/data_analyst_agent_models.py

from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# Define the input schema for the Data Analyst Agent
class DataAnalystInput(BaseModel):
    """
    Input schema for the Data Analyst Agent, accepting a CSV data chunk and language code.
    """
    powerQualityDataCsv: str
    languageCode: str

# Define the output schema for the Data Analyst Agent
class DataAnalystOutput(BaseModel):
    """
    Output schema for the Data Analyst Agent, returning a textual preparation report.
    """
    preparationReport: str