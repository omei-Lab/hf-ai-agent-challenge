from state import QAState
from langgraph.graph import StateGraph, START, END
from func import read_question, classify_question_type, answer_question, reverse_sentence, analyze_logic_node, route_by_type
from func import search_web, answer_with_context, extract_keywords, extract_final_answer

def build_graph():
    builder = StateGraph(QAState)

    # add nodes
    builder.add_node("read", read_question)
    builder.add_node("classify_type", classify_question_type)
    builder.add_node("answering", answer_question)
    builder.add_node("reverse", reverse_sentence)
    builder.add_node("logic_table", analyze_logic_node)
    builder.add_node("web", search_web)
    builder.add_node("answer_with_context", answer_with_context)
    builder.add_node("keyword", extract_keywords)
    builder.add_node("final", extract_final_answer)

    # edges
    builder.add_edge(START, "read")
    builder.add_edge("read", "classify_type")
    builder.add_edge("reverse", "answering")
    builder.add_edge("keyword", "web")
    builder.add_edge("web", "answer_with_context")
    builder.add_edge("answer_with_context", "final")
    builder.add_edge("answering", END)
    builder.add_edge("logic_table", END)
    builder.add_edge("final", END)

    # branching
    builder.add_conditional_edges(
        "classify_type",
        route_by_type,
        {
            "reverse": "reverse",
            "logic": "logic_table",
            "web": "keyword",
            "others": "answering"
        }
    )

    # Compile graph
    graph = builder.compile()
    return graph