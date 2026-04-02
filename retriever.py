# retriever.py
from ddgs import DDGS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

# 1. THE BLOCKLIST: Never read these sites
BLOCKED_DOMAINS = [
    "dictionary.com", "merriam-webster.com", "cambridge.org", 
    "collinsdictionary.com", "thesaurus.com", "oxfordlearnersdictionaries.com",
    
]

_rerank_model = None
def _get_reranker():
    global _rerank_model
    if _rerank_model is None:
        _rerank_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _rerank_model

def is_blocked(url):
    for bad in BLOCKED_DOMAINS:
        if bad in url:
            return True
    return False

def search_prioritized(query: str, top_sites: int = 3, max_fetch: int = 12):
    results = []
    seen_urls = set()
    
    try:
        with DDGS() as ddgs:
            # Fetch more results to allow for filtering
            ddg_gen = ddgs.text(query, max_results=max_fetch)
            for r in ddg_gen:
                url = r.get("href", "")
                
                # CRITICAL FIX: Skip blocked domains
                if is_blocked(url):
                    continue
                    
                if url in seen_urls: continue
                seen_urls.add(url)
                
                results.append({
                    "title": r.get("title", ""),
                    "url": url,
                    "snippet": r.get("body", ""),
                    "score": 0.0
                })
    except Exception as e:
        print(f"Search error: {e}")
        return []

    if not results: return []

    # AI Reranking
    model = _get_reranker()
    docs = [f"{r['title']} {r['snippet']}" for r in results]
    q_vec = model.encode([query])
    d_vecs = model.encode(docs)
    scores = cosine_similarity(q_vec, d_vecs)[0]

    final_results = []
    for i, r in enumerate(results):
        r['score'] = scores[i]
        final_results.append(r)

    # Sort by relevance
    final_results.sort(key=lambda x: x['score'], reverse=True)
    return final_results[:top_sites]