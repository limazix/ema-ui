import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage

### Define the Agent State ###
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]