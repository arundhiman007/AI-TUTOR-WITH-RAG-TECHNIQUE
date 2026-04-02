# 🤖 AI Tutor using RAG (Retrieval-Augmented Generation)

## 📌 Overview
This project is a Generative AI-based tutor system that answers user queries using LLM + RAG architecture. It retrieves relevant documents and generates context-aware responses.

## 🚀 Features
- LLM-powered question answering
- Retrieval-Augmented Generation (RAG)
- Semantic search using FAISS
- Context-aware response generation
- Reduced hallucination using retrieved knowledge

## 🛠 Tech Stack
- Python
- NLP
- FAISS (Vector Database)
- Transformers / LLM
- FastAPI / Streamlit 

## ⚙️ How It Works
1. Input query from user
2. Convert query into embeddings
3. Retrieve relevant documents using FAISS
4. Pass context + query to LLM
5. Generate accurate response

## ▶️ How to Run

```bash
git clone https://github.com/yourusername/ai-tutor-rag
cd ai-tutor-rag
pip install -r requirements.txt
python app.py
