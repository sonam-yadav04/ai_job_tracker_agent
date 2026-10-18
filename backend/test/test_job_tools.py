
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from job_tools import (
    jobs,
    check_duplicate,
    save_job,
    get_application_count
)


def test_job_tools():
    # Start with clean test data.
    jobs.clear()

    # 1. Test saving a new job.
    result = save_job(
        company="ABC Technologies",
        role="Python Developer",
        salary="4-6 LPA",
        requirements=["Python", "FastAPI", "SQL"]
    )

    assert result["saved"] is True
    assert len(jobs) == 1

    # 2. Test duplicate checking (case-insensitive).
    assert check_duplicate(
        "abc technologies",
        "python developer"
    ) is True

    # 3. Try saving the same job again.
    duplicate_result = save_job(
        company="ABC Technologies",
        role="Python Developer"
    )

    assert duplicate_result["saved"] is False
    assert len(jobs) == 1

    # 4. Add a second job with a different status.
    second_result = save_job(
        company="XYZ Ltd",
        role="Backend Engineer",
        status="applied"
    )

    assert second_result["saved"] is True

    # 5. Test application counts.
    assert get_application_count("saved") == 1
    assert get_application_count("applied") == 1
    assert get_application_count("all") == 2

    print("All job_tools tests passed!")


if __name__ == "__main__":
    test_job_tools()
