import os
import re
import abc
from typing import Any, Dict

from app.utils.config_handler import ConfigHandler
from app.utils.logger import Logger

class BaseAgent:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.logger.info(f"Initializing {self.__class__.__name__}")
        self.config = ConfigHandler()
        self._define_agent_config()

        self.prompt = self._define_prompt()
        self.llm = self._define_llm()
        self.chain = self._create_chain()

    @abc.abstractmethod
    def _define_agent_config(self):
        """Abstract method to define the agent's configuration."""
        pass


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

    def _build_config_path(self, file_name: str) -> str:
        """
        Builds the relative path to a configuration file within the agent's directory.

        Args:
            file_name: The name of the configuration file.

        Returns:
            The relative path to the configuration file.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        agent_dir_name = re.sub(r'([a-z])([A-Z])', r'\1_\2', self.__class__.__name__).lower()
        return os.path.join(current_dir, agent_dir_name.replace("_agent", ""), file_name)
