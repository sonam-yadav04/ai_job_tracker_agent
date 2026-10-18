import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scrapper import scrape_job_url

def test_scrape():
    url="https://eyglobal.yello.co/jobs/Lub9aSC4oyYsFtDv8fVcAQ?job_board_id=c1riT--B2O-KySgYWsZO1Q"
    text = scrape_job_url(url)
    print("\n=== Raw Scraped Text (first 500 chars) ===")
    print(text[:20000])

    assert isinstance(text, str)
    assert text.strip(), "No content scraped"
    print("\n scraper Test Passed")

if __name__ == '__main__':
    test_scrape()