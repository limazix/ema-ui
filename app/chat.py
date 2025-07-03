#!/usr/bin/env python3

"""This is the main entry point for the Chainlit application."""

import asyncio
import chainlit as cl
from langchain.schema.runnable.config import RunnableConfig
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage

from app.utils.file_uploader import handle_uploaded_file
from app.agents.data_analyst.data_analyst_agent_models import DataAnalystInput
from app.agent_workflow import graph
from app.agents.compliance.compliance_agent_models import ComplianceReportInput, AnalyzeComplianceReportOutput
from app.utils.logger import Logger

logger = Logger(__name__)

    # Use cl.TaskList() to create an empty TaskList
@cl.step(name="Ask user to upload CSV")
async def ask_upload():
    files = None

    while files is None:
        uploaded_files = await cl.AskFileMessage(
        content="Please upload the file you want to use for the report.",
        max_files=1,
        max_size_mb=50,
        accept=["text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"],
        ).send()
        if uploaded_files:
            return uploaded_files[0]

@cl.step(name="Loading file")
async def load_and_split_file(file_text):
    file_content_raw = await handle_uploaded_file(file_text)
    if file_content_raw is None:
        await cl.Message(content=f"Error: Could not process file {file_text.name}. Please try again with a different file or format.").send()
        return None
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_text(file_content_raw)

@cl.step(name="Processing data")
async def process_data(data_analyst_input: DataAnalystInput, config, cb):
    """Processes the data analyst results using the data analyst agent."""
    workflow_stream = graph.stream(
        {"messages": [data_analyst_input]},
        stream_mode="messages",
        config=RunnableConfig(callbacks=[cb], **config)
    )
    chunk_result = ""
    for msg, metadata in workflow_stream:
        if (
            msg.content
            and not isinstance(msg, HumanMessage)
            and metadata["langgraph_node"] == "data_analyst"
        ):
            chunk_result += msg.content
    return chunk_result

@cl.step(name="Checking compliance")
async def check_compliance(compliance_input: ComplianceReportInput, config, cb) -> AnalyzeComplianceReportOutput:
    """Processes the combined data analyst results using the compliance agent."""
    # Assuming your graph can handle ComplianceReportInput and route it to the compliance agent.
    # You might need to adjust your graph definition.
    workflow_stream = graph.stream({"messages": [compliance_input]}, stream_mode="messages", config=RunnableConfig(callbacks=[cb], **config))
    compliance_output = None
    for msg, metadata in workflow_stream:
        if msg.content and not isinstance(msg, HumanMessage) and metadata["langgraph_node"] == "compliance":
            # Assuming the compliance agent directly returns the AnalyzeComplianceReportOutput object or its dict representation
           compliance_output = AnalyzeComplianceReportOutput.model_validate_json(msg.content) # Adjust this based on actual output format if not JSON
    return compliance_output


@cl.step(name="Generating final report")
async def generate_report(final_report_content: str):
    """Generates the final report based on the compliance agent's output."""
    final_answer = cl.Message(content="")
    await final_answer.stream_token(final_report_content)
    await final_answer.send()


@cl.on_chat_start
async def start():

    file_text = await ask_upload()
    file_content_chunks = await load_and_split_file(file_text)

    if file_content_chunks:
        await cl.Message(content="File loaded and split into chunks. Ready to process.").send()

    cl.user_session.set("file_content_chunks", file_content_chunks)

@cl.on_message
async def on_message(msg: cl.Message):
    """
    This function is called when a message is received from the client.
    It processes the file chunks using the data analyst and compliance agents.
    """

    file_content_chunks = cl.user_session.get("file_content_chunks") # Assuming chunks are stored in session
    if not file_content_chunks:
         await cl.Message(content="No file chunks found. Please upload a file first.").send()
         return

    # Process each chunk individually
    data_analyst_results = []
    chunk_count = len(file_content_chunks)
    config = {"configurable": {"thread_id": cl.context.session.id}}
    cb = cl.LangchainCallbackHandler()

    # Process with Data Analyst Agent
    await cl.Message(content="Processing data with Data Analyst agent...").send()
    for i, chunk in enumerate(file_content_chunks):
        # Create DataAnalystInput from the chunk
        data_analyst_input = DataAnalystInput(powerQualityDataCsv=chunk, languageCode="pt-BR")
        await cl.Message(content=f"Analyzing data chunk: {i}/{chunk_count}...").send() # Display a snippet
        data_analyst_chunk_result = await process_data(data_analyst_input, config, cb)
        data_analyst_results.append(data_analyst_chunk_result)

    # Process with Compliance Agent
    # Create a single ComplianceReportInput from all data analyst results
    # Assuming data_analyst_results is a list of strings, each being the output summary for a chunk.
    # Concatenate these summaries for the compliance agent input. You might need a more sophisticated summarization method.
    power_quality_summary = "\\n".join(data_analyst_results)

    # Construct the ComplianceReportInput object
    compliance_input = ComplianceReportInput(
        fileName="uploaded_file.csv",  # Replace with actual file name
        powerQualityDataSummary=power_quality_summary, # Summarize or combine data_analyst_results
        identifiedRegulations=["ANEEL Resolução Normativa nº 414/2010", "ANEEL PRODIST Módulo 8"], # Add relevant regulations
        languageCode="pt-BR" # Or dynamic based on user preference
    )

    compliance_report_output = await check_compliance(compliance_input, config, cb)

    # Assuming the compliance agent's output object contains the final report content in Markdown.
    # Adjust this based on the actual structure of AnalyzeComplianceReportOutput.
    final_report_content = f"# Compliance Report\\n\\n{compliance_report_output.reportMetadata.title}\\n\\n{compliance_report_output.introduction['content']}\\n\\n## Analysis Sections\\n\\n" + "\\n\\n".join([f"### {section.title}\\n{section.content}\\n" for section in compliance_report_output.analysisSections]) + f"\\n\\n## Final Considerations\\n\\n{compliance_report_output.finalConsiderations}\\n\\n## Bibliography\\n\\n" + "\\n".join([f"- {item.text}" for item in compliance_report_output.bibliography])

    # Process with Compliance Agent
    await cl.Message(content="Checking compliance...").send()
    compliance_report_output = await check_compliance(compliance_input, config, cb)

    # Generate Final Report
    await cl.Message(content="Generating final report...").send()
    await generate_report(final_report_content)