# Reddit-Tiktok-Gen

### Dependencies:
- Python 3.12 - (https://www.python.org/downloads/)
- ffmpeg - (https://ffmpeg.org/download.html)
- Redis  - (docker run --name redis -d -p 6379:6379 redis)
- Gentle Aligner - (docker run -p 8765:8765 lowerquality/gentle)
- Docker - (https://docs.docker.com/get-docker/)

Fortunately, docker-compose will take care of all of these dependencies for you if you intend to just run the app, you only need to have docker installed. 

## How it works

This application is essentially an automation of a series of steps to go from a Reddit Post to a TikTok-Ready video.

Steps: 
1. Detemine gender, improve the language in the post, and generate audio for the video.
2. Generate SRT (subtitiles) for the video.
3. Generate a title image for the video.
4. Loop/Generate a background video
5. Stitch all of the above together to create a final video.

While efforts have been made to reduce storage usage, the app still requires a few GB of storage to run. There are a few temp files that are generated and deleted during the process, before creating a final video which may be a few 100MBs in size, depending on optimizations.


### Demos:

(Video quality of these examples were reduced for the sake of the demo, the actual output is much better. Videos have also been trimmed for a better experience.)

Here is a click of the output of the application, a TikTok-Ready video generated from a Reddit Post:

[Compressed Example Output](https://github.com/jwtly10/reddit-tiktok-gen/assets/39057715/dc6ff29f-2245-4701-8dec-51e89d3a9f75)

Here is a demo of the starting and usage of the web app that is used to interact with the generator:

[Web App Demo](https://github.com/jwtly10/reddit-tiktok-gen/assets/39057715/10f6f4b6-d0e1-4b14-ab9b-97beb28c3585)

#### Scripts
There are also some scripts in `./scripts` that expose some of the functionality of the app.

[./scripts/generate_videos_from_json.py](https://github.com/jwtly10/reddit-tiktok-gen/blob/main/scripts/quick_generate.py)
Exposes the functionality of the app to generate videos from a JSON file, for example:
```sh
python -m scripts.generate_videos_from_json path/to/json/videos.json path/to/output/directory
```

With the following JSON file

```json
{
    "videos": [
        {
            "title": "AITA for ignoring my husband during our flight when he expressed anxiety over flying?",
            "content": "Post Body"
        },
        {
            "title": "AITA for not offering to pay after my niece accidentally ruined my sister’s wedding dress at my barbecue?",
            "content": "Post Body"
        },
        {
            "title": "AITA for getting upset when a \"family day\" was entirely centered around my sister?",
            "content": "Post Body"
        },
        {
            "title": "AITA for telling my wife that she should have included my daughter in her \"mother/daughter\" trip?",
            "content": "Post Body"
        },
        {
            "title": "AITA for not taking the day off to watch my step kid?",
            "content": "Post Body"
        }
    ]
}
```

Will generate 5 videos with random backgrounds automatically. A utility tool is available at `http://localhost/tools/json_generator`, to generate the JSON for you with valid json formatting.

<img width="2048" alt="Screenshot 2024-04-18 at 20 14 55" src="https://github.com/jwtly10/reddit-tiktok-gen/assets/39057715/a91e9f3d-7713-44c3-bc44-87d6549c86f2">

This is useful for setting up automations or batch processing of videos.


### Environment Variables
There are some required environment variables that need to be set in order for the application to work. You can find the example files in the root directory of the project. 

Here are some of the supported/required vars:
```properties
*ENV=prod
SERVER_PORT=80
ELEVENLABS_API_KEY=
*GENTLE_ALIGNER_URL=http://gentle-aligner:8765
*OPENAI_API_KEY=
REDIS_URL=redis
REDIS_PORT=6379
REDIS_DB=0
DATABASE_URL=sqlite+aiosqlite:////data/video_jobs.db
```
Properties marked with * are required for the application to work, the values above work for the docker-compose file.

Duplicate this file under `project-root/.env-docker` for running the app in docker - [docker_example_file](https://github.com/jwtly10/reddit-tiktok-gen/blob/a6b5d315740eec2070cde5632b6e723409cf5582/.env-docker.example).

Duplicate this fileunder `project-root/.env` for local development - [local_example_file](https://github.com/jwtly10/reddit-tiktok-gen/blob/a6b5d315740eec2070cde5632b6e723409cf5582/.env.example).

## Installation

This prescript is required to download media files for video generation. It downloads some copyright-free background videos that are used in the final video. 

``` sh
wget -O /assets/background_videos/1.mp4 www.myserver.com/1.mp4 
wget -O /assets/background_videos/2.mp4 www.myserver.com/2.mp4
wget -O /assets/background_videos/3.mp4 www.myserver.com/3.mp4
```

You can then clone the repo and build the docker image, dependencies and start the container.
```sh
git clone https://github.com/jwtly10/reddit-tiktok-gen.git &&
cd reddit-tiktok-gen &&
docker-compose up --build
```

You can also change the title template username by cloning this template: 
https://www.canva.com/design/DAF5rWrG-H8/zYOAKN_LO8plXZbOTihu-g/view

## Tech Stack
- Python 3.12
- Celery on top of Redis
- SQLite
- FastAPI
- Docker
- SSR (Server Side Rendering)

## Contributing

Bug reports and pull requests are welcome!

## License

Reddit-Tiktok-Gen is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).