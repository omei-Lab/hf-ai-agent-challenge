from graph import build_graph

class QAgent:
    def __init__(self):
        print("QAgent initialized")
        self.graph = build_graph()
        
    def __call__(self, question: str) -> str:
        state = self.graph.invoke({"question": question})
        print(f"Agent returning answer: {state['answer']}\n")
        return state['answer']
