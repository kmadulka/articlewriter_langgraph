import requests
from bs4 import BeautifulSoup

def scrape_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No Title"
        paragraphs = soup.find_all("p")  # Extract paragraphs
        content = "\n".join(p.text for p in paragraphs[:5])  # Limit to first 5 paragraphs

        return {"url": url, "title": title, "content": content}
    
    except Exception as e:
        return {"url": url, "error": str(e)}