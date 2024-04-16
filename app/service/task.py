from app.service.celery_app import celery_app
from app.service.generate import generate_video_from_content
from app.service.database import AsyncSessionLocal
import asyncio


@celery_app.task(name="app.service.task.generate_video")
def generate_video(
    job_id: int, title: str, content: str, base_background_video: str, output_dir: str
):
    async def run_task():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            async with AsyncSessionLocal() as db:
                await generate_video_from_content(
                    job_id, title, content, base_background_video, output_dir, db
                )
        finally:
            loop.close()

    asyncio.run(run_task())
