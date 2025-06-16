from typing import TypedDict, List, Dict, Any, Optional
from typing import Optional

class QAState(TypedDict):

    # The question that user asks
    question: str

    # The question type (reverse, logic)
    type: str

    # The final answer
    answer: Optional[str] = None