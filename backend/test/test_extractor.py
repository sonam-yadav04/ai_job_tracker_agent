
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from extractor import extract_job_details

def test_extract_job():
    raw_test = """
        company: ABC technology
        role :  python developer
        salary: not disclosed
        requirements:
              - python
              - django/fastapi 
              - RestAPI
              
        """
    result = extract_job_details(raw_test)
    print(result)
    assert isinstance(result,dict)
    assert "company" in result
    assert "role" in result
    assert "salary" in result
    assert "requirements" in result

    print("\nTest passed!")

if __name__ == "__main__":
    test_extract_job()
    
    