import shutil
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import settings
from .downloader import DownloadCancelled, cleanup_part_files, run_download
from .models import FileLink, JobCreateRequest, JobResponse, JobStatus


@dataclass
class DownloadJob:
    id: str
    request: JobCreateRequest
    folder: Path
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: JobStatus = JobStatus.queued
    progress: float = 0
    phase: str = "queued"
    logs: list[str] = field(default_factory=list)
    error: str | None = None
    files: list[Path] = field(default_factory=list)
    cancel_requested: bool = False


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, DownloadJob] = {}
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=max(1, settings.max_concurrent_jobs))

    def create(self, request: JobCreateRequest) -> str:
        job_id = uuid.uuid4().hex
        folder = settings.download_dir / job_id
        folder.mkdir(parents=True, exist_ok=True)
        job = DownloadJob(id=job_id, request=request, folder=folder)
        self._append_log(job, "Job queued")
        with self._lock:
            self._jobs[job_id] = job
        self._executor.submit(self._run, job_id)
        return job_id

    def get(self, job_id: str) -> DownloadJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            if job.status in {JobStatus.completed, JobStatus.failed, JobStatus.cancelled}:
                return True
            job.cancel_requested = True
            job.phase = "cancelling"
            self._append_log(job, "Cancellation requested")
            return True

    def response(self, job: DownloadJob) -> JobResponse:
        with self._lock:
            files = [self._file_link(job, file) for file in job.files if file.exists()]
            return JobResponse(
                jobId=job.id,
                status=job.status,
                progress=job.progress,
                phase=job.phase,
                logs=job.logs[-200:],
                error=job.error,
                files=files,
            )

    def cleanup_expired(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.file_ttl_hours)
        with self._lock:
            expired = [
                job_id
                for job_id, job in self._jobs.items()
                if job.created_at < cutoff
                and job.status in {JobStatus.completed, JobStatus.failed, JobStatus.cancelled}
            ]
            for job_id in expired:
                job = self._jobs.pop(job_id)
                shutil.rmtree(job.folder, ignore_errors=True)

    def _run(self, job_id: str) -> None:
        job = self.get(job_id)
        if not job:
            return

        with self._lock:
            job.status = JobStatus.running
            job.phase = "starting"
            self._append_log(job, "Download started")

        try:
            files = run_download(
                url=str(job.request.url),
                folder=job.folder,
                kind=job.request.kind,
                quality=job.request.quality,
                playlist=job.request.playlist,
                convert_to_h264_requested=job.request.convertToH264,
                update_progress=lambda value: self._update_progress(job, value),
                set_phase=lambda phase: self._set_phase(job, phase),
                log=lambda message: self._append_log(job, message),
                is_cancelled=lambda: job.cancel_requested,
            )
            with self._lock:
                job.files = files
                job.progress = 100
                job.phase = "completed"
                job.status = JobStatus.completed
                self._append_log(job, "Job completed")
        except DownloadCancelled:
            cleanup_part_files(job.folder)
            with self._lock:
                job.status = JobStatus.cancelled
                job.progress = 0
                job.phase = "cancelled"
                self._append_log(job, "Job cancelled")
        except Exception as exc:
            cleanup_part_files(job.folder)
            with self._lock:
                job.status = JobStatus.failed
                job.phase = "failed"
                job.error = str(exc)
                self._append_log(job, f"Error: {exc}")

    def _file_link(self, job: DownloadJob, file: Path) -> FileLink:
        relative = file.relative_to(job.folder).as_posix()
        base = settings.public_base_url
        url = f"{base}/api/files/{job.id}/{relative}" if base else f"/api/files/{job.id}/{relative}"
        return FileLink(name=relative, url=url, size=file.stat().st_size)

    def _append_log(self, job: DownloadJob, message: str) -> None:
        job.logs.append(f"{datetime.now().strftime('%H:%M:%S')} {message}")

    def _update_progress(self, job: DownloadJob, value: float) -> None:
        with self._lock:
            job.progress = max(0, min(100, value))

    def _set_phase(self, job: DownloadJob, phase: str) -> None:
        with self._lock:
            job.phase = phase


job_store = JobStore()
