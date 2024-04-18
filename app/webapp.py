import os
import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.service.task import generate_video
from app.service.database import init_db, get_db_session
from app.utils.logger import log
from app.repository.job_repository import add_job, get_jobs

import app.config


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up... Initializing database.")
    await init_db()
    log.info("Database initialized.")
    yield


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

os.makedirs("tmp", exist_ok=True)
app.mount("/tmp", StaticFiles(directory="tmp"), name="tmp")


@app.get("/tools/json_generator")
async def json_generator(request: Request):
    return templates.TemplateResponse("json_generator.html", {"request": request})


@app.get("/")
async def read_root(request: Request, db: AsyncSession = Depends(get_db_session)):
    completed_jobs = await get_jobs(db)
    return templates.TemplateResponse(
        "index.html", {"request": request, "jobs": completed_jobs}
    )


def run_async(func, *args, **kwargs):
    """Helper function to run a function asynchronously"""
    asyncio.create_task(func(*args, **kwargs))


@app.post("/")
async def post_root(
    post_title: str = Form(...),
    post_content: str = Form(...),
    background_video: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
):
    log.info("Received a video generation request")
    log.debug(f"Title: {post_title}")
    log.debug(f"Content: {post_content}")
    log.debug(f"Background Video: {background_video}")

    if len(post_title) > 125:
        log.error("Title is too long. Max 124 Characters.")
        return JSONResponse(
            content={"error": "Title is too long. Max 124 Characters."}, status_code=400
        )

    try:
        job = await add_job(db, post_title, post_content, background_video)
        log.info(f"Job created with ID: {job.id}")

        output_dir = os.path.join("tmp", str(job.id))
        os.makedirs(output_dir, exist_ok=True)

        background_video = os.path.join("assets", "minecraft_background_video_1.mp4")

        generate_video.delay(
            job.id, post_title, post_content, background_video, output_dir
        )

        return JSONResponse(
            content={"video_id": job.id, "message": "Video generation request queued"}
        )
    except Exception as e:
        log.error(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    port = os.getenv("SERVER_PORT", 80)
    uvicorn.run(app, host="0.0.0.0", port=int(port), log_level="debug")
