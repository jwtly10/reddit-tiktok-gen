from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import os

from app.model.models import Job


async def add_job(
    session: AsyncSession, reddit_title: str, reddit_post: str, background_video: str
) -> Job:
    new_job = Job(
        reddit_title=reddit_title,
        reddit_post=reddit_post,
        background_video=background_video,
    )
    async with session.begin():
        session.add(new_job)
        await session.commit()
    await session.refresh(new_job)
    await session.commit()
    return new_job


async def update_job_step(
    session: AsyncSession, job_id: int, step: str, final_video_path=""
) -> Job:
    async with session.begin():
        stmt = select(Job).filter_by(id=job_id)
        result = await session.execute(stmt)
        job = result.scalar_one()
        # update job to processing if previously pending
        if job.status == "pending":
            job.status = "processing"

        # if we 'complete a job' we set the status to completed, but dont change the step
        if step == "completed":
            job.status = "completed"
        else:
            job.step = step

        if final_video_path:
            job.final_video_path = final_video_path
            file_size = os.path.getsize(final_video_path)
            job.size = f"{file_size / 1024 / 1024:.2f} MB"
        await session.commit()
    return job


async def fail_job(session: AsyncSession, job_id: int, error_msg: str) -> Job:
    async with session.begin():
        stmt = select(Job).filter_by(id=job_id)
        result = await session.execute(stmt)
        job = result.scalar_one()
        job.status = "failed"
        job.error_msg = error_msg
        await session.commit()
    return job


async def get_jobs(session: AsyncSession) -> list[Job]:
    async with session.begin():
        stmt = select(Job).order_by(Job.id.desc())
        result = await session.execute(stmt)
        jobs = result.scalars().all()
    return jobs
