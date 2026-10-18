jobs = []

def check_duplicate(company:str, role:str)->bool:
     """Check whether this company and role already exist."""
     company = company.strip().casefold()
     role = role.strip().casefold()
     if not company or not role:
        return False
     return any(j["company"].casefold() == company 
                and j["role"].casefold() == role 
                for j in jobs)
     
  
def save_job(company:str,
             role:str,
             salary:str | None = None,
             requirements:list[str] | None = None,
             status:str="saved"
)->dict:
    if not company.strip() or not role.strip():
        return {
            "saved": False,
            "reason": "Company and role are required."
        }

    # Prevent duplicates even if the agent skips the duplicate check.
    if check_duplicate(company, role):
        return {
            "saved": False,
            "reason": "Duplicate job already exists.",
            "company": company,
            "role": role
        }
    job ={
        "company": company.strip(),
        "role": role.strip(),
        "salary": salary,
        "requirements": requirements or [],
        "status": status.strip().casefold()
    }
    jobs.append(job)
    print(f"Saved job: {job}")
    return {
        "saved":True,
        "job":job
    }
  

def get_application_count(status:str="all")->int:
    status = status.strip().casefold() 
    if status == "all":
        return len(jobs)
    return sum(1 for j in jobs if j.get("status") == status)

    