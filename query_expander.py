# query_expander.py

def expand_query(query: str, intent: str) -> str:
    q = query.lower()

    # If asking for a definition, force "Concept" to avoid Dictionaries
    if intent == "definition" or intent == "fact":
        # e.g. "Deep Learning" -> "Deep Learning computer science concept explanation"
        return f"{query} technical concept explanation detailed meaning"

    if intent == "explanation":
        return f"{query} how it works underlying mechanism detailed explanation"
        
    if intent == "importance":
        return f"importance benefits advantages why use {query}"
        
    if intent == "steps":
        return f"how to steps procedure tutorial {query}"
        
    return f"{query} detailed concept"