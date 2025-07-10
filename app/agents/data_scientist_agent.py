"""This module defines the Data Science agent and the Data Engineer agent.

Atrributes:
    data_engineer_agent: Senior Data Engineer representation used as a tool to prepare the data for the Data Scientist.
    data_scientst_agent: Senior Data Scientist specializing in electrical power quality data from devices like PowerNET PQ-600 G4.
"""

import os

from google.adk.agents import Agent, LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools import agent_tool

data_engineer_agent = Agent(
    name="DataEngineerAgent",
    model=os.getenv("LLM_MODEL_NAME"),
    description="You are a Senior Data Engineer, specialist in writing and executing performatic code in python for data analytics and insights with more than 10 years of expertise.",
    instruction="""
    You will receive a dataset in CSV format at the session state variable {file_path?}, with multiple colunms to be processed and transformed into features.

    **Datase Characteristics**
    * The data follow a temporal series, not necessarely ordered
    * The file encoding is not defined, but it's usualy ISO-8859-1, Latin-1 or utf-8. However, it can be diferent.
    * Since there are too many float data, it will use `;` as column delimiter
    * The data always have a column with date and time of the provided mesured values
    
    **Your goal**
    * Identify the file encoding
    * Load the file and transform it in a pandas DataFrame
    * Do the clenup and the data preprocessing
    * You can use the ARIMA, or any methodology you see fit, to prepare the data for the Data Scientist
    * Store the final data object to the session state variable `data`
    * Return the data object to `data`
    * MOST IMPORTANT: Support the Data Scientist to process and evaluate the data
    """,
    output_key='data',
    code_executor=BuiltInCodeExecutor(language="python")
)

data_scientst_agent = LlmAgent(
    name="DataScientistAgent",
    model=os.getenv("LLM_MODEL_NAME"),
    description="You are a Senior Data Scientist specializing in electrical power quality data from devices like PowerNET PQ-600 G4. You will be provided with the {file_path?} of power quality data in CSV or TXT file, but both following the CSV format.",
    instruction="""
    Your task is to meticulously analyze the data generate a comprehensive textual preparation report in the language specified by {language_code?} (default to Brazilian Portuguese if not specified or if the language is not well-supported for this technical domain).
    Since it's usualy a long dataset, you can break the data into chunks to simplify the analysis and make it more objective.

    This preparation report for this data must include:
    1.  **Initial Data Analysis & Key Metrics:**
        *   Identify and list key voltage, current, power factor, and frequency statistics (e.g., min, max, average, significant deviations, outliers) *observed in each chunk*.
        *   Note the presence of any notable events or anomalies (e.g., sags, swells, interruptions, harmonic distortions exceeding typical thresholds, rapid changes) *visible in each chunk*.
        *   Describe general stability and quality trends *observed in each chunk*.
    2.  **Data Preparation Suggestions for Subsequent Engineering Analysis:**
        *   Based on your analysis of each chunk, suggest any data transformations (e.g., "Consider calculating THD for current if not present") or data enrichments (e.g., "If external temperature data is available for this period, correlating it with load might be insightful") that would be beneficial for a detailed ANEEL regulatory compliance assessment by an Electrical Engineer.
        *   If the data in each chunk appears incomplete or has quality issues, note them. If you were able to fix it, describe the process providing the issue, process and output.
    3.  **Preliminary Graphic/Visualization Ideas (for each chunk):**
        *   Suggest 1-2 types of simple graphics or visualizations (e.g., "a time-series plot of voltage for this period", "a histogram of frequency deviations") that could effectively represent the key characteristics or anomalies found *specifically each this data chunk*. These are preliminary ideas for this segment only.

    **Formatting and Constraints:**
    *   DO NOT add any introductory or concluding phrases like "This chunk covers..." or "In summary, this segment shows...". Provide only the direct, structured analytical output.
    *   The output summary for EACH CHUNK MUST be significantly smaller than the input data to be suitable for aggregation and further processing. Focus on information density and relevance for subsequent regulatory checks and engineering review. Do not include raw data rows.
    *   In essence, clearly delineating the three sections for each chunk (Initial Analysis, Preparation Suggestions, Graphic Ideas).
    """,
    tools=[agent_tool.AgentTool(data_engineer_agent)],
    output_key="ds_report",
    code_executor=BuiltInCodeExecutor(language="python")
)
