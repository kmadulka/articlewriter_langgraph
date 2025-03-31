from .base import ResearchGraphState, NodeName
from .llm_config import llm
from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from .prompts import report_writer_instructions, intro_conclusion_instructions
from langgraph.constants import Send

def initiate_all_interviews(state: ResearchGraphState):
    print("initializing interviews")
    analyst_list = [analyst for analyst in state.analysts][0][1]
    print(analyst_list)
    return [Send("conduct_interview", {"analyst": analyst,
                                           "messages": [HumanMessage(
                                               content=f"So you said you were writing an article on {state.topic}?"
                                           )
                                                       ]}) for analyst in analyst_list]

def write_report(state: ResearchGraphState):
    sections = state.sections
    topic = state.topic
    print('writing the article body...')
    # Concat all sections together
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    system_message = report_writer_instructions.format(topic=topic, context=formatted_str_sections)
    report = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Write a report based upon these memos.")])

    return Command(update={'content':report.content}, goto=NodeName.WRITE_INTRODUCTION)

def write_introduction(state: ResearchGraphState):
    content = state.content
    topic = state.topic

    system_message = intro_conclusion_instructions.format(topic=topic, content=content)
    introduction = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Write the report introduction.")])
    
    return Command(update={'introduction':introduction}, goto=NodeName.WRITE_CONCLUSION)

def write_conclusion(state: ResearchGraphState):
    content = state.content
    topic = state.topic
    system_message = intro_conclusion_instructions.format(topic=topic, content=content)
    conclusion = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Write the report conclusion.")])
    
    return Command(update={'conclusion':conclusion}, goto=NodeName.FINALIZE_REPORT)

def finalize_report(state: ResearchGraphState):
    content = state.content
    introduction = state.introduction
    conclusion = state.conclusion
    print('finalizing article...')

    if content.startswith("## Insights"):
        content = content.strip("## Insights")
    if "## Sources" in content:
        try:
            content, sources = content.split("## Sources")
        except:
            sources = None
    final_report = introduction.content + "\n\n---\n\n" + content + "\n\n---\n\n" + conclusion.content
    if sources is not None:
        final_report += "\n\n## Sources\n" + sources
    return Command(update={"final_report": final_report}, goto=NodeName.END)
