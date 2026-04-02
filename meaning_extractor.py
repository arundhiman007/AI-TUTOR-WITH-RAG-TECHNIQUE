# meaning_extractor.py
from embedder import embed_texts
import numpy as np

# If a chunk's relevance score is below this, we assume the source 
# didn't have the info and we DO NOT show that section.
MIN_REL_SCORE = 0.22 

def chunk_text(text: str, words_per_chunk=300):
    words = text.split()
    chunks = []
    # Reduced overlap to minimize repetition risk
    step = 300 
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i+words_per_chunk])
        if len(chunk) > 80:
            chunks.append(chunk)
    return chunks

def _get_unique_chunk(all_chunks: list[str], query: str, used_indices: set):
    """
    Finds the best chunk that has NOT been used yet.
    Returns: (text, score, index)
    """
    available_indices = [i for i in range(len(all_chunks)) if i not in used_indices]
    
    if not available_indices:
        return None, 0.0, -1

    candidate_chunks = [all_chunks[i] for i in available_indices]
    
    emb_chunks = embed_texts(candidate_chunks)
    emb_query = embed_texts([query])[0]

    norm_chunks = np.linalg.norm(emb_chunks, axis=1)
    norm_query = np.linalg.norm(emb_query)
    norm_chunks[norm_chunks == 0] = 1e-10
    
    # Cosine Similarity
    sims = np.dot(emb_chunks, emb_query) / (norm_chunks * norm_query)
    
    # Find best match
    best_local_idx = np.argmax(sims)
    best_score = sims[best_local_idx]
    
    real_idx = available_indices[best_local_idx]
    
    return all_chunks[real_idx], best_score, real_idx

def extract_tutor_content(query: str, docs: list[str], intent: str):
    """
    1. Gets Definition.
    2. If intent is SIMPLE, stops there.
    3. If intent is COMPLEX, tries to find Examples/Analysis.
    4. Uses Thresholding to ensure quality.
    """
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_text(doc))
    
    # Dedup list while keeping order
    seen = set()
    unique_chunks = []
    for c in all_chunks:
        h = c[:50]
        if h not in seen:
            unique_chunks.append(c)
            seen.add(h)
    all_chunks = unique_chunks[:50] # Limit processing

    used_indices = set()
    results = {"definition": None, "applications": None, "analysis": None}

    # --- PASS 1: DEFINITION (Always Required) ---
    def_text, score, idx = _get_unique_chunk(all_chunks, f"{query} definition summary answer", used_indices)
    if def_text:
        results["definition"] = [def_text]
        used_indices.add(idx)

    # --- CHECKPOINT: Is this a simple fact? ---
    # If user asked "When was India independent", we STOP here.
    if intent in ["fact", "history", "date", "person"]:
        return results

    # --- PASS 2: APPLICATIONS (Strict Threshold) ---
    # We look for keywords like "example", "use case"
    app_text, score, idx = _get_unique_chunk(all_chunks, f"examples applications real world use cases of {query}", used_indices)
    
    # STRICT RULE: Only add if score is high enough (meaning it actually talks about examples)
    if app_text and score > MIN_REL_SCORE:
        results["applications"] = [app_text]
        used_indices.add(idx)
    else:
        results["applications"] = None # Don't show card

    # --- PASS 3: ANALYSIS (Strict Threshold) ---
    # We look for keywords like "importance", "advantages"
    anl_text, score, idx = _get_unique_chunk(all_chunks, f"importance advantages key features analysis of {query}", used_indices)
    
    if anl_text and score > MIN_REL_SCORE:
        results["analysis"] = [anl_text]
        used_indices.add(idx)
    else:
        results["analysis"] = None # Don't show card

    return results