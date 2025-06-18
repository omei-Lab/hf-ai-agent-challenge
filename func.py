from state import QAState
from tools import web_search
from langchain_community.llms import Ollama

llm = Ollama(model="qwen:14b", temperature=0)

def read_question(state: QAState):
	print(f"Read question: \n{state['question']}")

	return {}

def answer_question(state: QAState):
    prompt = f"""
    Answer this question clearly and concisely. No explanation.

    Question: {state['question']}
    """
    response = llm.invoke(prompt)
    return {
        "answer": response
	}

def classify_question_type(state: QAState) -> QAState:
    prompt = f"""
	Read the following question carefully and classify it into exactly one of the following categories:

	- 'reverse': The question is written backwards or involves reading text in reverse.
	- 'logic': The question involves logical reasoning, abstract thinking, or puzzles (e.g., tables, sets, conditions).
	- 'web': The question asks about real-world entities (such as people, shows, dates, locations) that typically require external lookup or search.
	- 'others': The question is simple or doesn't fit the above types.

	Examples:

	Q: "If you write the word 'left' backwards, can you read this sentence?"
	A: reverse

	Q: "Given a set and an operation table, find counterexamples to commutativity."
	A: logic

	Q: "Who played the role of X in the Polish version of Y?"
	A: web

	Q: "How old is Alice?"
	A: others

	Important instructions:
	- Only answer with one lowercase word: reverse, logic, web, or others.
	- Avoid overthinking. If any real-world entity (person, media, place, date) is mentioned, it’s most likely 'web'.

	Now classify the following question:

	Question: {state['question']}
	"""

    response = llm.invoke(prompt).strip().lower()
    print(f"The type is likely to be '{response}'")
    return {
        "type": response
    }


def route_by_type(state: QAState) -> str:
    return state['type']

def reverse_sentence(state: QAState) -> QAState:
    return {
        "question": state['question'][::-1]
	}

def analyze_logic_node(state: dict):
    
	def extract_markdown_table(question: str) -> str:
		lines = question.strip().splitlines()
		table_lines = [line for line in lines if "|" in line]
		return "\n".join(table_lines)
    
	def parse_table_markdown(markdown_table: str) -> dict[tuple[str, str], str]:
		lines = markdown_table.strip().splitlines()
		headers = lines[0].split("|")[1:]  # skip first empty column
		table = {}
		for row in lines[2:]:  # skip header + --- line
			cells = row.split("|")[1:]
			row_label = cells[0].strip()
			for col_label, val in zip(headers[1:], cells[1:]):
				table[(row_label.strip(), col_label.strip())] = val.strip()
		return table
	
	def find_commutativity_violations(table: dict[tuple[str, str], str]) -> set[str]:
		elements = {a for a, _ in table.keys()}
		violating = set()
		for a in elements:
			for b in elements:
				if table[(a, b)] != table[(b, a)]:
					violating.update([a, b])
		return sorted(violating)

	table_md = extract_markdown_table(state["question"])
	parsed_table = parse_table_markdown(table_md)
	violating = find_commutativity_violations(parsed_table)

	return {
		"answer": ", ".join(violating) if violating else "None"
	}

def search_web(state: dict) -> dict:
    question = state["question"]
    result = web_search(question) 
    # print(result)
    return {
        "context": result  
    }

def answer_with_context(state: QAState):
    context = state['context']
    question = state["question"]

    prompt = f"""
    You are given a question and an optional Wikipedia context. 
    If context is useful, base your answer on it. 
	If there's a date mentioned in the question, please make sure your answer is reasonable.
    
	Extract only the final answer to the original question, in the shortest possible form. 
    For example, if the question is "How many albums...", 
    only return the number (e.g., "3") without extra explanation or any other words.

	Here is an example:
	Q: What is the capital of France?
	A: Paris
	Do not return the answer such as "The capital of France is Paris." instead of the final answer.

    Context:
    {context}

    Question:
    {question}
    """

    response = llm.invoke(prompt)
    return {
		"answer": response
	}

def extract_keywords(state: QAState) -> QAState:
    prompt = f"""
	Extract the most important keywords from the following question for searching the wiki.
    Focus on named entities (people, titles, shows, events, country, language) or proper nouns and numbers relevant to identifying the correct answer.
	Preserve disambiguating information like nationality, language, or version (e.g., "Polish actor" or "Japanese version").
    Keep it short and relevant. Only a string that seperate the keywords by commas.

	Here provides an example.
	Question: Who played Naruto in the Japanese version of the anime?
	Answer: Naruto, Japanese version, anime

    Question: {state['question']}
    Keywords:
    """
    response = llm.invoke(prompt)
    print("Keywords: ", response)
    return {
		"keywords": response.strip() 
	}

def extract_final_answer(full_answer: str) -> str:
    prompt = f"""
    Here is an answer from an agent:
    ---
    {full_answer}
    ---
    Extract only the final answer to the original question, in the shortest possible form. 
    For example, if the question is "How many albums..." and the answer includes the list, 
    only return the number (e.g., "3") without extra explanation.

	For example,
	full_answer: "The capital of France is Paris." --> "Paris"
	full_answer: "The final answer is 50." --> "50"
	full_answer: "So there are 512 birds." --> "512"
    """
    response = llm.invoke(prompt).strip()
    return {
		"answer": response
	}
