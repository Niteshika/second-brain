import uuid
from typing import Any

jobs: dict[str, dict[str,Any]] = {}

def create_job() -> str:
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running",
                    "result": None,
                    "error": None}
    return job_id

def mark_done(job_id: str, result: Any) -> None:
    jobs[job_id] = {"status": "done",
                    "result": result,
                    "error": None}

def mark_error(job_id: str, error_message: str) -> None:
    jobs[job_id] = {"status": "error",
                    "result": None,
                    "error": error_message}

def get_job(job_id: str) -> dict[str, Any] | None:
    return jobs.get(job_id)

