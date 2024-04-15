from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio

from app.service.database import init_db

from app.utils.logger import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up... Initializing database.")
    await init_db()
    log.info("Database initialized.")
    yield

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
async def post_root():
    # try:
    #     raise Exception("This is a placeholder error")
    # except Exception as e:
    #     return jsonify({"success": False, "error": str(e)})
    await asyncio.sleep(3)
    result = "This is a placeholder result"
    return JSONResponse(content={"output_path": result, "success": True})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")

