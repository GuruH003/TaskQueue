from fastapi import FastAPI
from app.routes import job_routes
from app.workers.worker import worker_loop
import asyncio

app = FastAPI(title="Task Queue System")
app.include_router(job_routes.router, prefix="/jobs", tags=["Jobs"])


@app.on_event("startup")
async def start_worker():
    asyncio.create_task(worker_loop())