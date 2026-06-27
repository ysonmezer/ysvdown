from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class AnalyzeRequest(BaseModel):
    url: HttpUrl


class AnalyzeResponse(BaseModel):
    title: str
    isPlaylist: bool
    playlistCount: int | None = None
    resolutions: list[int]
    has4kH264: bool


class JobCreateRequest(BaseModel):
    url: HttpUrl
    kind: Literal["video", "mp3"] = "video"
    quality: Literal["720", "1080", "2160"] = "1080"
    playlist: bool = False
    convertToH264: bool = False


class JobCreateResponse(BaseModel):
    jobId: str


class FileLink(BaseModel):
    name: str
    url: str
    size: int


class JobResponse(BaseModel):
    jobId: str
    status: JobStatus
    progress: float = Field(ge=0, le=100)
    phase: str
    logs: list[str]
    error: str | None = None
    files: list[FileLink]
