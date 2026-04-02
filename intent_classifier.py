# intent_classifier.py
import re

# These demand a simple, direct answer. No "Examples" or "Analysis" cards.
SIMPLE_INTENTS = ["fact", "history", "date", "person", "definition_simple"]

INTENT_PATTERNS = {
    "fact": [
        r"\bwhen\b", r"\bwhat year\b", r"\bwhich date\b", r"\btime of\b",
        r"\bhow many\b", r"\bpopulation\b", r"\bheight\b", r"\bcurrency\b",
        r"\bcapital\b", r"\bwho is\b", r"\bwho was\b", r"\bceo of\b"
    ],
    "history": [
        r"\bhistory of\b", r"\borigin\b", r"\binvented by\b", r"\bbackground\b"
    ],
    "steps": [
        r"\bhow to\b", r"\bsteps\b", r"\bprocedure\b", r"\bguide\b", 
        r"\binstall\b", r"\bway to\b", r"\bmethod\b"
    ],
    "importance": [
        r"\bimportance\b", r"\badvantage\b", r"\bbenefit\b", r"\bwhy use\b", 
        r"\bpros and cons\b"
    ],
    "explanation": [
        r"\bhow does\b", r"\bexplain\b", r"\bworking of\b", r"\bmechanism\b", 
        r"\bconcept of\b",r"\bwhat is\b", r"\bdefine\b"
    ]
}

def classify_intent(query: str) -> str:
    q = query.lower().strip()
    
    # 1. Check patterns
    for intent, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, q):
                return intent

    # 2. Length Heuristic
    # Very short queries (e.g., "Python") are usually "Concept Learning" (Complex)
    # Short questions (e.g., "Is python free?") are Facts (Simple)
    if len(q.split()) < 4:
        return "explanation" # Default to full lesson for short topics
        
    return "fact" # Default to simple answer for sentences