from .base import NodeName, ResearchGraphState
from .create_analysts.create_analysts_nodes import create_analysts, human_feedback
from .writer_nodes import write_conclusion, write_introduction, write_report, finalize_report, initiate_all_interviews
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from .interview.interview_graph import interview_graph_builder

interview_builder = interview_graph_builder()

def article_writer_graph_builder():
    # Add nodes and edges 
    builder = StateGraph(ResearchGraphState)
    builder.add_node(NodeName.CREATE_ANALYSTS, create_analysts)
    builder.add_node(NodeName.HUMAN_FEEDBACK, human_feedback)
    builder.add_node(NodeName.CONDUCT_INTERVIEW, interview_builder.compile())
    builder.add_node(NodeName.WRITE_REPORT,write_report)
    builder.add_node(NodeName.WRITE_INTRODUCTION,write_introduction)
    builder.add_node(NodeName.WRITE_CONCLUSION,write_conclusion)
    builder.add_node(NodeName.FINALIZE_REPORT,finalize_report)


    builder.add_edge(NodeName.START, NodeName.CREATE_ANALYSTS)
    builder.add_edge(NodeName.CREATE_ANALYSTS, NodeName.HUMAN_FEEDBACK)
    builder.add_conditional_edges(
            NodeName.HUMAN_FEEDBACK,
            initiate_all_interviews,
            [NodeName.CREATE_ANALYSTS, NodeName.CONDUCT_INTERVIEW]
        )
    builder.add_edge(NodeName.CONDUCT_INTERVIEW, NodeName.WRITE_REPORT)
    builder.add_edge(NodeName.WRITE_REPORT, NodeName.WRITE_INTRODUCTION)
    builder.add_edge(NodeName.WRITE_REPORT, NodeName.WRITE_CONCLUSION)
    builder.add_edge([NodeName.WRITE_INTRODUCTION, NodeName.WRITE_CONCLUSION], NodeName.FINALIZE_REPORT)
    builder.add_edge(NodeName.FINALIZE_REPORT, NodeName.END)

    # Interview 
    # memory = MemorySaver()
    # final_graph = builder.compile(checkpointer=memory).with_config(run_name="Write Report")
    return builder