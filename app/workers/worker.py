import asyncio
import logging
from uuid import UUID
from datetime import datetime
from sqlalchemy.future import select
from app.db import AsyncSessionLocal
from app.models.job import Job, JobStatus
from sqlalchemy.ext.asyncio import AsyncSession

MAX_CONCURRENT_JOBS = 5

logging.basicConfig(level=logging.INFO)

async def process_job(job: Job, db: AsyncSession):
    logging.info(f"Processing job: {job.id} (type={job.type})")
    job.status = JobStatus.running
    await db.commit()

    try:
        #job work with async sleep
        await asyncio.sleep(3)
        job.status = JobStatus.completed
        job.updated_at = datetime.utcnow()
        logging.info(f"Completed job: {job.id}")
    except Exception as e:
        job.status = JobStatus.failed
        logging.error(f"Job failed: {job.id}, reason: {str(e)}")
    finally:
        await db.commit()

async def worker_loop():
    while True:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Job)
                .where(Job.status == JobStatus.pending)
                .order_by(Job.priority.desc(), Job.created_at)
                .limit(MAX_CONCURRENT_JOBS)
            )
            jobs = result.scalars().all()

            if not jobs:
                await asyncio.sleep(2)
                continue

            tasks = []
            for job in jobs:
                # tasks.append(process_job(job, db))
                if await dependencies_met(job, db):
                    job.status = JobStatus.running
                    await db.commit()
                    tasks.append(process_job(job, db))
                else:
                    job.status = JobStatus.blocked
                    await db.commit()

            await asyncio.gather(*tasks)

async def dependencies_met(job: Job, db: AsyncSession) -> bool:
    if not job.depends_on:
        return True

    for dep_id in job.depends_on:
        result = await db.execute(select(Job).where(Job.id == UUID(dep_id)))
        dep_job = result.scalar_one_or_none()

        if not dep_job or dep_job.status != JobStatus.completed:
            return False

    return True

