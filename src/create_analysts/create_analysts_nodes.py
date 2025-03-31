from src.base import GenerateAnalystsState, Perspectives
from ..llm_config import llm
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import interrupt, Command
from langgraph.graph import END
from .prompts import analyst_instructions


def create_analysts(state: GenerateAnalystsState):
    """Generate the analysts personas"""

    topic = state.topic
    max_analysts = state.max_analysts
    human_analyst_feedback = state.human_analyst_feedback

    structured_llm = llm.with_structured_output(Perspectives)
    system_msg = analyst_instructions.format(topic=topic, human_analyst_feedback= human_analyst_feedback, max_analysts=max_analysts)

    analysts = structured_llm.invoke([
        SystemMessage(content=system_msg),
    ]+ [HumanMessage(content='Generate the set of analysts')])

    print(analysts)

    state.analysts = analysts

    return state

    

def human_feedback(state: GenerateAnalystsState):
    """ask for human feedback for analysts"""

    human_feedback = interrupt("Please input any feedback for the analysts: ")
    print(f"human feedback: {human_feedback}")

    state.human_analyst_feedback = human_feedback

    if human_feedback:
        return Command(update={"human_analyst_feedback": human_feedback}, goto="create_analysts")
    else:
        return Command(update={"human_analyst_feedback": None}, goto=END)

    