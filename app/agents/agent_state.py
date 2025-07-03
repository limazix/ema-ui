import operator
from typing import Annotated, Sequence, TypedDict, Optional

from langchain_core.messages import BaseMessage

### Define the Agent State ###
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    powerQualityDataCsv: Optional[str]