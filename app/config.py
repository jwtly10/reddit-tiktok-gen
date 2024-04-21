import os
from dotenv import load_dotenv

from app.utils.logger import log


def load_env():
    load_dotenv()

    required_vars = [
        "ENV",
        "GENTLE_ALIGNER_URL",
        "OPENAI_API_KEY",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing environment var(s) {', '.join(missing_vars)}")

    log.info(f"Running in {os.getenv("ENV")}")


ffmpeg_config = {
    "default": {
        "preset": "medium",
        "crf": 23,
        "capture_stdout": True,
        "capture_stderr": True,
        "global_args": ["-loglevel", "error"],
    },
    "medium_debug": {
        "preset": "medium",
        "crf": 23,
        "capture_stdout": False,
        "capture_stderr": True,
        "global_args": [],
    },
    "test": {
        "preset": "ultrafast",
        "crf": 35,
        "capture_stdout": False,
        "capture_stderr": True,
        "global_args": [],
    },
    "production_ssh": {
        "preset": "slow",
        "crf": 18,
        "capture_stdout": False,
        "capture_stderr": True,
        "global_args": [],
    },
    "low_quality": {
        "preset": "ultrafast",
        "crf": 28,
    },
}


load_env()
