from uuid import UUID
from app.db import get_db
from typing import Optional
from sqlalchemy.future import select
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job, JobPriority, JobStatus
from fastapi import APIRouter, Depends, HTTPException, Query


router = APIRouter()

class ResourceRequirements(BaseModel):
    cpu_units: int = Field(default=1, ge=1)
    memory_mb: int = Field(default=128, ge=64)

class JobCreate(BaseModel):
    type: str
    priority: JobPriority
    payload: dict
    resource_requirements: ResourceRequirements
    depends_on: list[UUID] = []
    timeout_seconds: int = 60

@router.post("/", status_code=201)
async def submit_job(job: JobCreate, db: AsyncSession = Depends(get_db)):
    new_job = Job(
        type=job.type,
        priority=job.priority,
        payload=job.payload,
        resource_cpu=job.resource_requirements.cpu_units,
        resource_memory=job.resource_requirements.memory_mb,
        depends_on=job.depends_on,
        timeout_seconds=job.timeout_seconds
    )
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    payload = {
        "message": "Job submitted successfully",
        "job_id": str(new_job.id),
        "status": new_job.status,
        "created_at": new_job.created_at,
        "priority": new_job.priority,
        "position_in_queue": None
    }
    return payload


@router.get("/{job_id}")
async def get_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    payload = {
        "message": "Job fetched successfully",
        "job_id": str(job.id),
        "status": job.status,
        "type": job.type,
        "priority": job.priority,
        "created_at": job.created_at,
        "resource_cpu": job.resource_cpu,
        "resource_memory": job.resource_memory,
        "depends_on": job.depends_on,
        "timeout_seconds": job.timeout_seconds,
        "payload": job.payload
    }
    return payload
    

@router.get("/")
async def list_jobs(status: Optional[JobStatus] = Query(None),priority: Optional[JobPriority] = Query(None),type: Optional[str] = Query(None),db: AsyncSession = Depends(get_db)):
    stmt = select(Job)

    if status:
        stmt = stmt.where(Job.status == status)
    if priority:
        stmt = stmt.where(Job.priority == priority)
    if type:
        stmt = stmt.where(Job.type == type)

    result = await db.execute(stmt)
    jobs = result.scalars().all()

    job_list = []
    for job in jobs:
        job_list.append({
            "job_id": str(job.id),
            "type": job.type,
            "status": job.status,
            "priority": job.priority,
            "created_at": job.created_at,
        })
    return job_list
    
@router.patch("/{job_id}/cancel")
async def cancel_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in ["pending", "blocked"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel a job in status: {job.status}")

    job.status = "cancelled"
    await db.commit()
    await db.refresh(job)

    payoad = {
        "message": "Job cancelled successfully",
        "job_id": str(job.id),
        "status": job.status,
    }
    return payoad
    
    