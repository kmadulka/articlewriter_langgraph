from src.base import GenerateAnalystsState, NodeName
from .create_analysts_nodes import create_analysts, human_feedback
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver


def create_analysts_graph_builder():
    builder = StateGraph(GenerateAnalystsState)
    builder.add_node(NodeName.CREATE_ANALYSTS, create_analysts)
    builder.add_node(NodeName.HUMAN_FEEDBACK, human_feedback)

    builder.add_edge(NodeName.START, NodeName.CREATE_ANALYSTS)
    builder.add_edge(NodeName.CREATE_ANALYSTS, NodeName.HUMAN_FEEDBACK)
    builder.add_conditional_edges(
            NodeName.HUMAN_FEEDBACK,
            lambda state: NodeName.CREATE_ANALYSTS if (state.human_analyst_feedback is not None) else NodeName.END,
            [NodeName.CREATE_ANALYSTS, NodeName.END]
        )

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    return graph
