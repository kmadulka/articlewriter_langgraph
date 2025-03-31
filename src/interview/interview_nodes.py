from src.base import InterviewState, SearchQuery, NodeName
from ..llm_config import llm
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.document_loaders import WikipediaLoader
from langchain_core.messages import get_buffer_string
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchResults
from ..utils import scrape_url
import os
from langgraph.types import interrupt, Command
from ..prompts import search_instructions, question_instructions, answer_instructions, section_writer_instructions
from tavily import TavilyClient
api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key)

# inteview nodes
def generate_question(state: InterviewState):
    analyst = state.analyst
    messages = state.messages

    sys_msg = question_instructions.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=sys_msg)]+messages)

    state.messages = question

    return state

def search_web(state: InterviewState):
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=search_instructions)]+state.messages)
    # Invalid input type <class 'langchain_core.prompts.chat.ChatPromptTemplate'>. Must be a PromptValue, str, or list of BaseMessages.

    tavily_search = TavilySearchResults(max_results=3)
    search_docs = tavily_search.invoke(search_query.search_query)

    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return Command(update={"context":formatted_search_docs}) #state

def search_wikipedia(state: InterviewState):
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=search_instructions)]+state.messages)

    search_docs = WikipediaLoader(query=search_query.search_query, load_max_docs=2).load()

    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return Command(update={"context":formatted_search_docs}) #state


def search_duckduckgo(state: InterviewState):
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([SystemMessage(content=search_instructions)]+state.messages)

    search = DuckDuckGoSearchResults(source="news") #backend="news"

    results = search.invoke(search_query.search_query)
    urls = [entry.split("link: ")[1].split(",")[0] for entry in results.split("title:") if "link:" in entry]
    scraped_data = [scrape_url(url) for url in urls]

    # Print the scraped results
    for data in scraped_data:
        search_docs = f"Title: {data.get('title')}\nURL: {data['url']}\nContent:\n{data.get('content', 'No content extracted.')}\n{'-'*80}"

    return Command(update={"context": search_docs})


def generate_answer(state: InterviewState):
    """answer question from analyst"""
    analyst = state.analyst
    messages= state.messages
    context = state.context

    sys_msg = answer_instructions.format(goals=analyst.persona, context=context)
    answer = llm.invoke([SystemMessage(content=sys_msg)]+messages)

    answer.name = "expert"

    return Command(update={"messages":[answer]})

def save_interview(state: InterviewState):
    """save the interview between analyst and expert"""
    print(f"saving inteview with {state.analyst}")
    
    messages = state.messages

    interview=get_buffer_string(messages)

    return Command(update={"interview":interview}) 

def route_messages(state: InterviewState):
    messages = state.messages
    name = "expert"

    num_responses = len([m for m in messages if isinstance(m, AIMessage) and m.name==name])

    if num_responses >= state.max_num_turns:
        return NodeName.SAVE_INTERVIEW

    last_question = messages[-2]

    if "Thank you for your help" in last_question.content:
        return NodeName.SAVE_INTERVIEW
    else:
        return NodeName.GENERATE_QUESTION
    
def write_section(state: InterviewState):

    """ Node to answer a question """
    # Get state
    interview = state.interview
    context = state.context
    analyst = state.analyst
   
    # Write section using either the gathered source docs from interview (context) or the interview itself (interview)
    system_message = section_writer_instructions.format(focus=analyst.description)
    section = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Use this source to write your section: {context}")]) 
                
    # Append it to state
    state.sections = section.content
    return state