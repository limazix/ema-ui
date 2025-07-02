from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.utils.logger import Logger
from app.agents.base_agent import BaseAgent
from app.agents.agent_state import AgentState

from .data_analyst_agent_models import DataAnalystInput, DataAnalystOutput


class DataAnalystAgent(BaseAgent):

    def _define_agent_config(self):
        """Define the agent's configuration."""
        config_path = self._build_config_path("data_analyst_agent.yaml")
        self.config.load_config("data_analyst_agent", config_path)

    def _define_prompt(self) -> ChatPromptTemplate:
        """Define the specific prompt for the Data Analyst agent."""
        # self.logger.info(self.config._configs.keys())
        system_message_content = self.config.get_config("data_analyst_agent", key="prompt")
        human_message_content = self.config.get_config("data_analyst_agent", key="output")

        # Add a check here to see what system_message_content is
        # self.logger.info(f"System Messa/ge Content: {system_message_content}")
        self.logger.info(f"Human Message Content: {human_message_content}")

        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_message_content),
                HumanMessage(content=human_message_content),
            ]
        ).partial()

    def _define_llm(self):
        """Define the specific LLM model for the Data Analyst agent."""
        # Placeholder LLM - replace with actual LLM instance
        return ChatGoogleGenerativeAI(
            model=self.config.get_config("data_analyst_agent", 'model', 'gemini-1.5-flash-latest'),
            temperature=self.config.get_config("data_analyst_agent", 'temperature', 0)
        )

    def _define_input_schema(self):
        """Define the input schema for the Data Analyst agent."""
        return DataAnalystInput

    def _define_output_schema(self):
        """Define the output schema for the Data Analyst agent."""
        return DataAnalystOutput

    def _create_chain(self):
        """Create the Langchain runnable chain for the Data Analyst agent."""
        # Placeholder chain - replace with actual chain implementation
        return (
            # The input to the chain is a dictionary with 'powerQualityDataCsv' and 'languageCode'
            RunnablePassthrough()
            | self.prompt
            | self.llm
            | RunnablePassthrough.assign(preparationReport=lambda x: x.content) # Assuming LLM output is in .content and is the report string
        )
    
    def process(self, input_data: DataAnalystInput) -> DataAnalystOutput:
        """Process the input data using the Data Analyst agent's chain."""
        self.logger.log(f"Processing data with DataAnalystAgent: {input_data}", level=Logger.INFO)
        
        # Create and invoke the chain with the input data
        chain = self._create_chain()
        # Pass the input data fields directly to the chain's invoke method
        output = chain.invoke({"powerQualityDataCsv": input_data.powerQualityDataCsv, "languageCode": input_data.languageCode})
        
        return DataAnalystOutput(dataSummary=output.content)

    def invoke(self, state: AgentState) -> AgentState:
        """Invoke the Data Analyst agent to process the data."""
        self.logger.log(f"Invoking DataAnalystAgent with state: {state}", level=Logger.INFO)

        # Extract necessary input data from the state
        input_data = DataAnalystInput(powerQualityDataCsv=state.get("powerQualityDataCsv"), languageCode=state.get("languageCode"))

        # Process the data using the process method
        agent_output = self.process(input_data)

        return {"dataAnalysisReport": agent_output.dataSummary}

