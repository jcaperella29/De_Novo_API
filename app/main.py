# app/main.py
from fastapi import FastAPI, BackgroundTasks
import os
import shutil
from .database import init_db, SessionLocal, AssemblyJob
from .trinity_ops import run_trinity_job, get_trinity_stats, estimate_assembly_time
from .config import DATA_DIR, RESULTS_DIR, DEFAULT_MAX_MEMORY, DEFAULT_CPU

init_db()

app = FastAPI()

from pydantic import BaseModel

class AssemblyInput(BaseModel):
    left_read: str
    right_read: str
    max_memory: str = DEFAULT_MAX_MEMORY
    cpu: int = DEFAULT_CPU

@app.post("/assemble")
async def assemble_reads(input: AssemblyInput, background_tasks: BackgroundTasks):
    # Validate files exist
    if not os.path.exists(input.left_read) or not os.path.exists(input.right_read):
        return {"error": "One or both input files not found."}

    output_dir = os.path.join(RESULTS_DIR, f"job_{int(os.times()[4])}")

    db = SessionLocal()
    new_job = AssemblyJob(
        left_read=input.left_read,
        right_read=input.right_read,
        output_dir=output_dir,
        status="pending"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    est_minutes = estimate_assembly_time(input.left_read, input.right_read, input.cpu)
    background_tasks.add_task(run_trinity_job, new_job.id, input.left_read, input.right_read, output_dir, input.max_memory, input.cpu)

    db.close()
    return {
        "job_id": new_job.id,
        "status": "queued",
        "estimated_completion_minutes": est_minutes
    }

@app.get("/stats/{job_id}")
async def get_stats(job_id: int):
    db = SessionLocal()
    job = db.query(AssemblyJob).filter(AssemblyJob.id == job_id).first()
    db.close()

    if not job:
        return {"error": "Job not found"}

    if job.status != "completed":
        return {"status": job.status}

    stats = get_trinity_stats(job.output_dir)
    return {"stats": stats}

@app.get("/jobs")
async def list_jobs():
    db = SessionLocal()
    jobs = db.query(AssemblyJob).all()
    db.close()
    return [{"id": job.id, "status": job.status, "start_time": job.start_time, "end_time": job.end_time} for job in jobs]

@app.get("/jobs/{job_id}")
async def get_job_detail(job_id: int):
    db = SessionLocal()
    job = db.query(AssemblyJob).filter(AssemblyJob.id == job_id).first()
    db.close()
    if not job:
        return {"error": "Job not found"}
    return {
        "id": job.id,
        "status": job.status,
        "output_dir": job.output_dir,
        "log": job.log
    }

@app.get("/result/{job_id}")
async def get_result(job_id: int):
    db = SessionLocal()
    job = db.query(AssemblyJob).filter(AssemblyJob.id == job_id).first()
    db.close()
    if not job:
        return {"error": "Job not found"}
    fasta_path = os.path.join(job.output_dir, "Trinity.fasta")
    if not os.path.exists(fasta_path):
        return {"error": "Result file not found"}
    return {"path": fasta_path}
