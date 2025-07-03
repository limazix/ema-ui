import os

from typing import Dict, Any, Annotated, Sequence, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.agent_state import AgentState
from app.agents.base_agent import BaseAgent

from .compliance_agent_models import ComplianceReportInput, AnalyzeComplianceReportOutput


class ComplianceAgent(BaseAgent):

    def _define_agent_config(self):
        self.config.load_config("compliance_agent", self._build_config_path("compliance_agent.yaml")) # Example loading

    def _define_prompt(self) -> ChatPromptTemplate:
        """Define the specific prompt for the Compliance Agent."""
        # Migrated prompt content from original app/agents.py
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=self.config.get_config("compliance_agent", "prompt")),
                HumanMessage(content="{input}"),
            ]
        )

    def _define_llm(self) -> ChatGoogleGenerativeAI:
        """Define the LLM for the Compliance Agent."""
        return ChatGoogleGenerativeAI(
            model=self.config.get_config("compliance_agent", 'model', 'gemini-1.5-flash-latest'),
            temperature=self.config.get_config("compliance_agent", 'temperature', 0),
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def _create_chain(self):
        """Create the LangChain chain for the Compliance Agent."""
        return (
            # The RunnablePassthrough is likely not needed if processing structured data directly
            self.llm
            # You might need a structured output parser here instead of JsonOutputParser
            | JsonOutputParser() 
        )

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data to generate a compliance report."""
        # Assuming input data is already in the format of ComplianceReportInput
        self.logger.info("Running Compliance Agent")

        try:
            chain = self._create_chain()
            compliance_report_content = chain.invoke(data)
            return {"report": compliance_report_content} # Return as dictionary

        except Exception as e:
            self.logger.error(f"Error running Compliance Agent: {e}")
            # You might want to define a specific error output model or structure
            return {"report": {"error": f"Failed to generate compliance report: {e}"}} # Return error as dictionary

    def _define_input_schema(self) -> type:
        """Define the input schema for the Compliance Agent."""
        return ComplianceReportInput

    def _define_output_schema(self) -> type:
        """Define the output schema for the Compliance Agent."""
        return AnalyzeComplianceReportOutput

    def invoke(self, state: AgentState) -> Dict[str, Any]:
        """Invokes the Data Analyst Agent to process power quality data."""
        self.logger.info("Invoking Compliance Agent")
        try:
            data_analysis_report = state.get('dataAnalysisReport')
            language_code = state.get('languageCode', 'en') # Default to English if not provided

            result = self.process({"input": data_analysis_report, "languageCode": language_code})

            return {"complianceReport": result.get("report")}
        except Exception as e:
            self.logger.error(f"Error invoking Compliance Agent: {e}")
            return {"complianceReport": {"error": f"Failed to invoke Compliance Agent: {e}"}}
