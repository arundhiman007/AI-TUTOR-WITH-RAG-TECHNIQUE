# web_scraper.py
import requests
import trafilatura
from bs4 import BeautifulSoup
import os, hashlib, json

CACHE_DIR = "scrape_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def scrape_website(url: str):
    # Check Cache
    h = hashlib.sha256(url.encode()).hexdigest()
    path = os.path.join(CACHE_DIR, f"{h}.json")
    
    if os.path.exists(path):
        try:
            with open(path, "r") as f: return json.load(f)["text"]
        except: pass

    # Real Request
    try:
        # Headers are crucial to avoid 403 Errors
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code != 200: return ""
        
        # Extract
        text = trafilatura.extract(r.text)
        if not text:
            soup = BeautifulSoup(r.text, "html.parser")
            for x in soup(["script", "style", "nav", "footer"]): x.decompose()
            text = " ".join(soup.get_text().split())

        if len(text) < 100: return "" # Too short

        # Save Cache
        with open(path, "w") as f: json.dump({"url":url, "text":text}, f)
        
        return text
    except:
        return ""