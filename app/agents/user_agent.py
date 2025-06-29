# app/agents/user_agent.py
from .base_agent import BaseAgent
from ..models.user import UserInput, UserOutput

class UserAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        # Initialize UserAgent specific attributes here
        pass

    def process(self, data: UserInput) -> UserOutput:
        # Implement processing logic for UserAgent
        processed_data = f"Processed user input: {data.name}"
        return UserOutput(result=processed_data)

    @staticmethod
    def create_agent(config):
        return UserAgent(config)

# app/models/user.py
from pydantic import BaseModel

class UserInput(BaseModel):
    name: str
    email: str

class UserOutput(BaseModel):
    result: str