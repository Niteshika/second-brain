from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
 
from app.core.security import get_current_user
from app.core.jobs import create_job, mark_done, mark_error, get_job
from app.core.knowledge_gap import run_knowledge_gap_analysis
from app.models.knowledge_gap import JobStartResponse, JobStatusResponse 

router = APIRouter()

def run_analysis_task(job_id: str):
    results,error = run_knowledge_gap_analysis()
    if error is not None :
        mark_error(job_id= job_id, error_message=error)
        return
    mark_done(job_id=job_id,result=results)


@router.post("/run", response_model= JobStartResponse)
def start_analysis(background_tasks: BackgroundTasks, current_user=Depends(get_current_user)):
    job_id = create_job()
    background_tasks.add_task(run_analysis_task, job_id)
    return {"job_id": job_id}


@router.get("/status/{job_id}", response_model=JobStatusResponse)
def check_status(job_id: str, current_user=Depends(get_current_user)):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(404, "Job not found")

    return job