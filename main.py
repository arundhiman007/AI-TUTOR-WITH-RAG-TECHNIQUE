# main.py
import streamlit as st
import time
from retriever import search_prioritized
from web_scraper import scrape_website
from intent_classifier import classify_intent
from meaning_extractor import extract_tutor_content
from summarizer import generate_tutor_response
from query_expander import expand_query

# Custom CSS for Card Design
def apply_custom_css():
    st.markdown("""
        <style>
        .stApp { background-color: #15162e; }
        .tutor-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 15px;
            border-left: 5px solid #4F8BF9;
        }
        .tutor-header {
            color: #2c3e50;
            font-weight: 700;
            font-size: 1.1rem;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .tutor-text { color: #4a5568; line-height: 1.6; font-size: 1rem; }
        .source-box { font-size: 0.8rem; color: #666; }
        </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_ai():
    from embedder import _get_model
    from summarizer import load_summarizer
    _get_model()
    load_summarizer()
    return True

st.set_page_config(page_title="EduTutor AI", layout="wide", page_icon="🎓")
apply_custom_css()

with st.spinner("Initializing System..."):
    load_ai()

st.title("EduTutor 🎓")
st.markdown("A smart tutor that distinguishes between **Simple Facts** and **Complex Lessons**.")

# Input
col1, col2 = st.columns([5, 1])
with col1:
    query = st.text_input("Enter your question:", placeholder="e.g. When was India independent? OR Explain Machine Learning")
with col2:
    st.write("")
    st.write("")
    start_btn = st.button("Search", type="primary", use_container_width=True)

if query:
    
    with st.status("Analyzing Request...", expanded=True) as status:
        # 1. Classify
        intent = classify_intent(query)
        status.write(f"Detected Intent: **{intent.upper()}**")
        
        # 2. Search
        q_exp = expand_query(query, intent)
        status.write("Searching verified sources...")
        hits = search_prioritized(q_exp, top_sites=3)
        
        if not hits:
            st.error("No reliable sources found.")
            st.stop()
            
        # 3. Scrape
        docs = []
        fallback = ""
        for h in hits:
            txt = scrape_website(h["url"])
            if txt: docs.append(txt)
            fallback += h["snippet"] + " "
        
        if not docs: docs = [fallback]

        # 4. Extract (Smart Filter)
        status.write("Extracting relevant sections...")
        # This function now enforces Strict Thresholds & Index Exclusion
        tutor_data = extract_tutor_content(q_exp, docs, intent)
        
        # 5. Summarize
        status.write("Structuring answer...")
        lesson = generate_tutor_response(tutor_data)
        
        status.update(label="Complete", state="complete", expanded=False)

    st.markdown("---")

    # --- RENDER CARDS CONDITIONALLY ---

    # Card 1: Definition/Answer (Always shown if found)
    if lesson['definition']:
        st.markdown(f"""
            <div class="tutor-card">
                <div class="tutor-header">📖 Direct Answer / Definition</div>
                <div class="tutor-text">{lesson['definition']}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("I read the sources but couldn't generate a clear summary. Please check the links below.")

    # Card 2: Applications (ONLY if extracted successfully)
    if lesson['applications']:
        st.markdown(f"""
            <div class="tutor-card" style="border-left-color: #00C853;">
                <div class="tutor-header">💡 Real-World Examples</div>
                <div class="tutor-text">{lesson['applications']}</div>
            </div>
        """, unsafe_allow_html=True)

    # Card 3: Analysis (ONLY if extracted successfully)
    if lesson['analysis']:
        st.markdown(f"""
            <div class="tutor-card" style="border-left-color: #FFAB00;">
                <div class="tutor-header">⚖️ Key Analysis & Importance</div>
                <div class="tutor-text">{lesson['analysis']}</div>
            </div>
        """, unsafe_allow_html=True)

    # Sources
    with st.expander("📚 View References"):
        for h in hits:
            st.markdown(f"**{h['title']}**")
            st.caption(h['url'])
            st.write(h['snippet'])
            st.divider()