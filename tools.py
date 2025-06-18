from langchain_community.tools.tavily_search import TavilySearchResults

def web_search(query: str) -> str:
    """Search Tavily for a query and return maximum 3 results."""
    search_tool = TavilySearchResults(max_results=3)
    results = search_tool.invoke(query)  # 回傳的是 list of dict

    formatted_results = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.get("url", "")}"/>\n{doc.get("content", "")}\n</Document>'
            for doc in results
        ]
    )
    return {"web_results": formatted_results}
