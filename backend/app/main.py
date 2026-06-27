import asyncio
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .auth import require_api_token
from .config import settings
from .downloader import analyze_url
from .jobs import job_store
from .models import AnalyzeRequest, AnalyzeResponse, JobCreateRequest, JobCreateResponse, JobResponse

app = FastAPI(title="YS Video Downloader API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def start_cleanup_loop() -> None:
    async def cleanup_loop() -> None:
        while True:
            job_store.cleanup_expired()
            await asyncio.sleep(900)

    asyncio.create_task(cleanup_loop())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse, dependencies=[Depends(require_api_token)])
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        result = analyze_url(str(request.url))
        return AnalyzeResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/jobs", response_model=JobCreateResponse, dependencies=[Depends(require_api_token)])
def create_job(request: JobCreateRequest) -> JobCreateResponse:
    job_id = job_store.create(request)
    return JobCreateResponse(jobId=job_id)


@app.get("/api/jobs/{job_id}", response_model=JobResponse, dependencies=[Depends(require_api_token)])
def get_job(job_id: str) -> JobResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_store.response(job)


@app.post("/api/jobs/{job_id}/cancel", dependencies=[Depends(require_api_token)])
def cancel_job(job_id: str) -> dict[str, bool]:
    if not job_store.cancel(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return {"ok": True}


@app.get("/api/files/{job_id}/{file_path:path}", dependencies=[Depends(require_api_token)])
def download_file(job_id: str, file_path: str) -> FileResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    requested = (job.folder / file_path).resolve()
    try:
        requested.relative_to(job.folder.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid file path") from exc

    if not requested.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(Path(requested), filename=requested.name)
