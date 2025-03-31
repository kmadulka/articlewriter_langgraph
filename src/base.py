from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from langchain_core.messages import AnyMessage
from langgraph.graph import START, END
import operator
from langgraph.graph.message import add_messages
from typing_extensions import Annotated
import openai
import os
from langchain_openai import ChatOpenAI



# create analysts subgraph
class Analyst(BaseModel):
    name: str = Field(..., description="name of analyst")
    role: str = Field(..., description = "role of the analyst in the context of the topic")
    description: str = Field(..., description="description of the analyst focus, concerns, motives")

    @property
    def persona(self)-> str:
        return f"Name {self.name}\nRole: {self.role}\n Description: {self.description}"

class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(..., description="list of analysts and their roles and descriptions")

class GenerateAnalystsState(BaseModel):
    topic: str
    max_analysts: int = 3
    human_analyst_feedback: Optional[str] = None
    analysts: Optional[Perspectives] = None



class InterviewState(BaseModel):
    max_num_turns: int = 10
    context: Annotated[list[AnyMessage], add_messages] = []
    analyst: Analyst
    interview: str = ""
    sections: Annotated[list[AnyMessage], add_messages] = []
    messages: Annotated[list[AnyMessage], add_messages] = []

class SearchQuery(BaseModel):
    search_query: str = Field(..., description="search query for retrieval")


# Overall graph
class ResearchGraphState(BaseModel):
    topic: str
    max_analysts: int = 3
    human_analyst_feedback: Optional[str] = None
    analysts: Optional[Perspectives] = None #List[Analysts]
    sections: Annotated[list, operator.add] = []
    introduction: str = ""
    content: str = ""
    conclusion: str = ""
    final_report: str = ""

# enum for nodenames
class NodeName(str, Enum):
    END= END
    CREATE_ANALYSTS = "create_analysts"
    HUMAN_FEEDBACK = "human_feedback"
    START = START
    SAVE_INTERVIEW = "save_interview"
    GENERATE_QUESTION = "generate_question"
    CONDUCT_INTERVIEW = "conduct_interview"
    WRITE_REPORT = "write_report"
    WRITE_INTRODUCTION = "write_introduction"
    WRITE_CONCLUSION = "write_conclusion"
    FINALIZE_REPORT = "finalize_report"
    SEARCH_WEB = "search_web"
    SEARCH_WIKIPEDIA = "search_wikipedia"
    ANSWER_QUESTION = "answer_question"
    WRITE_SECTION = "write_section"


    