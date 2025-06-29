import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph
# Define the Agent State
from app.agents.compliance.compliance_agent import ComplianceAgent
from app.agents.data_analyst.data_analyst_agent import DataAnalystAgent
from app.agents.agent_state import AgentState

# Initialize a StateGraph with the defined AgentState.
workflow = StateGraph(AgentState)

# --- Define Agent Nodes ---
# Instantiate your agents and add them as nodes to the workflow, e.g.:
data_analyst_agent_instance = DataAnalystAgent()
workflow.add_node("data_analyst", data_analyst_agent_instance.invoke)

compliance_agent_instance = ComplianceAgent()
workflow.add_node("compliance_report", compliance_agent_instance.invoke)


# --- Define Graph Entry Point ---
# Set the initial entry point of the graph, e.g.:
workflow.set_entry_point("data_analyst")

# Define the edges between nodes to specify the flow of execution, e.g.:
workflow.add_edge("data_analyst", "compliance_report")

# Set the point(s) where the graph execution should finish, e.g.:
workflow.set_finish_point("compliance_report") # type: ignore