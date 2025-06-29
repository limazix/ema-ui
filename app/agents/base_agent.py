import abc
from typing import Any, Dict

from app.utils.config_handler import ConfigHandler
from app.utils.logger import Logger

class BaseAgent:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.config = ConfigHandler()
        self.logger = Logger(self.__class__.__name__)
        self.logger.info(f"Initializing {self.__class__.__name__}")
        self.prompt = self._define_prompt()
        self.llm = self._define_llm()
        self.input_schema = self._define_input_schema()
        self.output_schema = self._define_output_schema()
        self.chain = self._create_chain()

    @abc.abstractmethod
    def _define_prompt(self):
        """Abstract method to define the agent's prompt template."""
        pass

    @abc.abstractmethod
    def _define_llm(self):
        """Abstract method to define the LLM model to be used."""
        pass

    @abc.abstractmethod
    def _define_input_schema(self):
        """Abstract method to define the input schema for the agent."""
        pass

    @abc.abstractmethod
    def _define_output_schema(self):
        """Abstract method to define the output schema for the agent."""
        pass

    @abc.abstractmethod
    def _create_chain(self):
        """Abstract method to create the Langchain runnable chain for the agent."""
        pass

    @abc.abstractmethod
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abstract method to invoke the agent's chain with the current state.
        Subclasses must implement this.
        """
        pass