# summarizer.py
from transformers import pipeline
import textwrap

SUMMARIZER_PIPELINE = None

def load_summarizer():
    global SUMMARIZER_PIPELINE
    if SUMMARIZER_PIPELINE is None:
        SUMMARIZER_PIPELINE = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    return SUMMARIZER_PIPELINE

def _summarize_section(text, max_l=150, min_l=60):
    pipe = load_summarizer()
    try:
        # Dynamic length adjustment
        input_len = len(text.split())
        if input_len < 50: return text # Return raw if too short
        
        out = pipe(
            text[:3000], 
            max_length=max_l, 
            min_length=min_l, 
            do_sample=False,
            repetition_penalty=1.2
        )
        return out[0]["summary_text"].replace(" .", ".")
    except:
        return textwrap.shorten(text, width=400)

def generate_tutor_response(tutor_data: dict):
    """
    Takes the dictionary from extractor and generates 3 distinct summaries.
    """
    response = {}
    
    # 1. Definition Section
    if tutor_data["definition"]:
        raw = " ".join(tutor_data["definition"])
        response["definition"] = _summarize_section(raw, max_l=180, min_l=80)
    else:
        response["definition"] = "Information not available."

    # 2. Application Section
    if tutor_data["applications"]:
        raw = " ".join(tutor_data["applications"])
        response["applications"] = _summarize_section(raw, max_l=200, min_l=80)
    else:
        response["applications"] = None

    # 3. Analysis Section
    if tutor_data["analysis"]:
        raw = " ".join(tutor_data["analysis"])
        response["analysis"] = _summarize_section(raw, max_l=200, min_l=80)
    else:
        response["analysis"] = None

    return response