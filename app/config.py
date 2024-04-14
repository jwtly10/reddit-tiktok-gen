import os
from dotenv import load_dotenv

from app.utils.logger import log


def load_config():
    load_dotenv()

    required_vars = [
        "ELEVENLABS_API_KEY",
        "ENV",
        "GENTLE_ALIGNER_URL",
        "OPENAI_API_KEY",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing environment var(s) {', '.join(missing_vars)}")

    log.info(f"Running in {os.getenv("ENV")}")


load_config()
