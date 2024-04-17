FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
RUN mkdir -p /app/data

# Install necessary packages including utilities for font management
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fontconfig \
 && rm -rf /var/lib/apt/lists/*

# Copy the requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and media files
COPY ./app /app/app
COPY ./assets /app/assets
COPY ./docker-compose.yml /app/
COPY ./Dockerfile /app/
COPY ./.env-docker /app/

# Copy font files
COPY ./assets/Poppins-SemiBold.ttf /usr/share/fonts/
COPY ./assets/Mont-HeavyDEMO.otf /usr/share/fonts/

# Update font cache
RUN fc-cache -fv

EXPOSE 80

CMD ["python", "-m", "app.webapp"]
