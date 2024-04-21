import os
from dotenv import load_dotenv
import matplotlib.font_manager as font_manager
from app.utils.logger import log

import subprocess

def check_ffmpeg_installed():
    try:
        output = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def check_process_running(process_name):
    try:
        output = subprocess.run(["pgrep", "-af", process_name], capture_output=True, text=True)
        return process_name in output.stdout
    except subprocess.CalledProcessError:
        return False


def check_fonts_installed(font_names):
    fonts = set(f.fname for f in font_manager.fontManager.ttflist)
    installed_fonts = {font: any(font in f for f in fonts) for font in font_names}
    return installed_fonts


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

    # Check all dependencies
    if not check_ffmpeg_installed():
        raise EnvironmentError("ffmpeg is not installed")
    if not check_process_running("gentle"):
        raise EnvironmentError("gentle aligner is not running")

    # Check required fonts
    font_names = ["Poppins-SemiBold.tff", "Mont"]
    installed_fonts = check_fonts_installed(font_names)
    for font, installed in installed_fonts.items():
        if not installed:
            pass
            # raise EnvironmentError(f"Font {font} is not installed")

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
        "capture_stderr": False,
        "global_args": ["-loglevel", "info"],
    },
    "low_quality": {
        "preset": "ultrafast",
        "crf": 28,
    },
}


load_env()
