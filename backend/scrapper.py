import httpx
from bs4 import BeautifulSoup
"""httpx to fetch the page and BeautifulSoup to parse its HTML into readable text. These libraries are designed for HTTP requests and HTML parsing respectively."""
def scrape_job_url(url:str) -> str:
    try:
        resp = httpx.get(
            url,
            follow_redirects =True,
            timeout = 15,
            headers={
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text,"html.parser")
        unwanted = [
            "script",
            "style",
            "nav",
            "footer",
            "aside",
            "noscript",
            "svg",
            "form",
            "button",
            "[role='navigation']",
        ]

        # Remove elements that usually aren't part of the job description.
        for selector in unwanted:
            for element in soup.select(selector):
                element.decompose()
                
        # Prefer the article or main content over the entire webpage. 
        content =(
              soup.find("article")
              or soup.find("main")
              or soup.find("div", attrs={"role":"main"})
              or soup.find("div",class_ = "content")  
              or soup.body
              or soup
        )
         # Extract readable text and remove empty lines.
        lines=[
            line.strip()
            for line in content.get_text(separator= "\n").splitlines()
            if line.strip()
        ]       
      
        text = "\n".join(lines)
        # Keep the input manageable for the LLM in this exercise.
        return text[:15000]
    except Exception as e:
        return f"Failed to scrape {url}: {e}"
      

      

