import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

PAPERS_FILE = "papers.json"

def load_existing():
    if os.path.exists(PAPERS_FILE):
        try:
            with open(PAPERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_all(papers):
    with open(PAPERS_FILE, "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

def fetch_rajasthan_papers():
    """RSMSSB राजस्थान पोर्टल से क्वेश्चन पेपर्स फेच करना"""
    url = "https://rsmssb.rajasthan.gov.in/page?MenuKey=WpGg9MfvEGE="
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a"):
                href = a.get("href", "")
                text = a.text.strip()
                if ".pdf" in href.lower() and len(text) > 4:
                    full_url = href if href.startswith("http") else "https://rsmssb.rajasthan.gov.in/" + href.lstrip("/")
                    items.append({
                        "title": text,
                        "category": "RAJASTHAN",
                        "exam": "RSMSSB",
                        "year": datetime.now().year,
                        "type": "Question Paper",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "pdfUrl": full_url
                    })
    except Exception as e:
        print("Rajasthan Fetch Error:", e)
    return items

def fetch_banking_papers():
    """IBPS और बैंकिंग पोर्टल्स से हैंडआउट्स/सैंपल पेपर्स फेच करना"""
    url = "https://www.ibps.in"
    headers = {"User-Agent": "Mozilla/5.0"}
    items = []
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a"):
                href = a.get("href", "")
                text = a.text.strip()
                if ".pdf" in href.lower() and any(k in text.lower() for k in ["handout", "sample", "paper", "exam"]):
                    full_url = href if href.startswith("http") else "https://www.ibps.in/" + href.lstrip("/")
                    items.append({
                        "title": f"IBPS: {text}",
                        "category": "BANK_INSURANCE",
                        "exam": "IBPS",
                        "year": datetime.now().year,
                        "type": "Sample Paper",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "pdfUrl": full_url
                    })
    except Exception as e:
        print("Banking Fetch Error:", e)
    return items

def main():
    existing = load_existing()
    existing_urls = {p.get("pdfUrl") for p in existing}
    
    new_raj = fetch_rajasthan_papers()
    new_bank = fetch_banking_papers()
    
    added_count = 0
    for paper in (new_raj + new_bank):
        if paper["pdfUrl"] not in existing_urls:
            paper["id"] = len(existing) + 1
            existing.insert(0, paper)
            existing_urls.add(paper["pdfUrl"])
            added_count += 1
            
    save_all(existing)
    print(f"Total {added_count} new papers added.")

if __name__ == "__main__":
    main()
