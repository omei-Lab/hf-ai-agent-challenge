from typing import TypedDict, List, Dict, Any, Optional
from typing import Optional

class QAState(TypedDict):

    # The question that user asks
    question: str

    # The question type (reverse, logic)
    type: str
    
	# The extracted keywords
    keywords: Optional[str] = None

	# The context fetched from web
    context: Optional[str] = None

    # The final answer
    answer: Optional[str] = None