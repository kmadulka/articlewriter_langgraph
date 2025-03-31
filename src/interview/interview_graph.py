from src.base import NodeName, InterviewState
from .interview_nodes import generate_answer, generate_question, search_duckduckgo, search_web, search_wikipedia, save_interview, write_section, route_messages
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

def interview_graph_builder():
    # Add nodes and edges 
    interview_builder = StateGraph(InterviewState)
    interview_builder.add_node(NodeName.GENERATE_QUESTION, generate_question)
    interview_builder.add_node("search_web", search_web)
    interview_builder.add_node("search_wikipedia", search_wikipedia) 
    interview_builder.add_node("search_duckduckgo", search_duckduckgo)
    interview_builder.add_node("answer_question", generate_answer)
    interview_builder.add_node("save_interview", save_interview)
    interview_builder.add_node("write_section", write_section)

    # Flow
    interview_builder.add_edge(NodeName.START, NodeName.GENERATE_QUESTION)
    interview_builder.add_edge(NodeName.GENERATE_QUESTION, "search_web")
    interview_builder.add_edge(NodeName.GENERATE_QUESTION, "search_wikipedia")
    interview_builder.add_edge(NodeName.GENERATE_QUESTION, "search_duckduckgo")
    interview_builder.add_edge("search_web", "answer_question")
    interview_builder.add_edge("search_wikipedia", "answer_question")
    interview_builder.add_edge("search_duckduckgo", "answer_question")
    interview_builder.add_conditional_edges(
            "answer_question", route_messages,
            [NodeName.GENERATE_QUESTION, 'save_interview']
        )
    # interview_builder.add_conditional_edges("answer_question", route_messages,[NodeName.GENERATE_QUESTION,'save_interview'])
    interview_builder.add_edge("save_interview", "write_section")
    interview_builder.add_edge("write_section", NodeName.END)

    # Interview 
    memory = MemorySaver()
    interview_graph = interview_builder.compile(checkpointer=memory).with_config(run_name="Conduct Interviews")
    return interview_builder #interview_graph
