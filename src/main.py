from .article_writer_graph import article_writer_graph_builder
from time import sleep
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from IPython.display import Markdown, display

def main(topic, thread_id, max_analysts = 3):
    builder = article_writer_graph_builder()
    memory = MemorySaver()
    final_graph = builder.compile(checkpointer=memory).with_config(run_name="Write Report")
    thread = {"configurable": {"thread_id": thread_id}}

    final_graph.invoke({"topic": topic},
            thread,
            stream_mode="updates"
        )

    while final_graph.get_state(thread).next: #need while loop if there is feedback
            graph_state = final_graph.get_state(thread)
            interrupt_value = graph_state.tasks[0].interrupts[0].value

            # Occasionally, the previous print statement is not visible in the console.
            sleep(0.5)

            human_feedback_text = input(interrupt_value) #input stored here
            print(f"\nAgent Response: {human_feedback_text}\n\n")
            final_graph.invoke(Command(resume=human_feedback_text), config=thread)

            display(Markdown(final_graph.get_state(thread).values['final_report']))


if __name__ == "__main__":
    main()