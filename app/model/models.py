from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import Enum

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reddit_title = Column(String, nullable=False)
    reddit_post = Column(String, nullable=False)
    background_video = Column(String, nullable=False)
    final_video_path = Column(String, nullable=True)
    size = Column(String, nullable=True)
    step = Column(
        Enum(
            "new",
            "generating_audio",
            "generating_srt",
            "generating_title_image",
            "generating_background_video",
            "generating_final_video",
            name="step_types",
        ),
        default="new",
    )
    status = Column(
        Enum("pending", "processing", "completed", "failed", name="status_types"),
        default="pending",
    )
    error_msg = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
