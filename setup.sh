#!/bin/bash
# Some basic cmds to init ssh machine

# Clone the repo
git clone https://github.com/jwtly10/reddit-tiktok-gen.git

# Create a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install the requirements
pip install -r requirements.txt

