# app/agents/data_analyst_agent_models.py

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

# Define the input schema for the Data Analyst Agent
class DataAnalystInput(BaseModel):
    """
    Input schema for the Data Analyst Agent, accepting a CSV data chunk and language code.
    """
    powerQualityDataCsv: str = Field(
        description="A CHUNK of power quality data in CSV format. This is one segment of a potentially larger dataset."
    )
    languageCode: Optional[str] = Field(
        default='pt-BR',
        description='The BCP-47 language code for the desired output language (e.g., "en-US", "pt-BR"). Defaults to "pt-BR" if not provided.'
    )

# Define the output schema for the Data Analyst Agent
class DataAnalystOutput(BaseModel):
    """
    Output schema for the Data Analyst Agent, returning a comprehensive textual analysis summary.
    """
    dataSummary: str = Field(
        description='A comprehensive textual analysis of THIS SPECIFIC power quality data CHUNK, acting as a Senior Data Analyst. This output should be in the specified language and include: 1. Key metrics, statistics (min, max, avg), and significant anomalies/deviations. 2. Suggestions for data transformations or enrichments that would aid a detailed regulatory compliance review by an electrical engineer. 3. Preliminary ideas for graphics/visualizations based on this chunk. The summary must be factual, significantly smaller than the input, and ready for aggregation and further processing by specialized engineering agents.'
    )