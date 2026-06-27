import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Callable

import yt_dlp

MP3_QUALITY = "192"
VIDEO_CRF = "23"
FFMPEG_PRESET = "fast"
CONCURRENT_DOWNLOADS = 1
SLEEP_INTERVAL = 1
MAX_SLEEP_INTERVAL = 3
MAX_RETRIES = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class DownloadCancelled(Exception):
    pass


class CancelAwareLogger:
    def __init__(self, is_cancelled: Callable[[], bool]):
        self.is_cancelled = is_cancelled

    def _check(self) -> None:
        if self.is_cancelled():
            raise DownloadCancelled("Download cancelled")

    def debug(self, msg: str) -> None:
        self._check()

    def info(self, msg: str) -> None:
        self._check()

    def warning(self, msg: str) -> None:
        self._check()

    def error(self, msg: str) -> None:
        self._check()


def ffmpeg_path() -> str | None:
    return shutil.which("ffmpeg")


def analyze_url(url: str) -> dict:
    is_playlist = False
    playlist_count = None

    check_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "playlist_items": "1",
        "socket_timeout": 5,
        "user_agent": USER_AGENT,
        "http_headers": {"Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"},
    }
    with yt_dlp.YoutubeDL(check_opts) as ydl:
        info = ydl.extract_info(url, download=False, process=False)
        if "entries" in info or info.get("_type") == "playlist":
            is_playlist = True
            playlist_count = info.get("playlist_count") or info.get("n_entries")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 10,
        "user_agent": USER_AGENT,
    }
    ffmpeg = ffmpeg_path()
    if ffmpeg:
        ydl_opts["ffmpeg_location"] = ffmpeg

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        metadata = ydl.extract_info(url, download=False)

    formats = metadata.get("formats", [])
    resolutions = sorted({f.get("height") for f in formats if f.get("height")})
    has_4k_h264 = any(
        f.get("height") == 2160 and str(f.get("vcodec", "")).startswith("avc1")
        for f in formats
    )

    return {
        "title": metadata.get("title") or "Untitled",
        "isPlaylist": is_playlist,
        "playlistCount": playlist_count,
        "resolutions": resolutions,
        "has4kH264": has_4k_h264,
    }


def cleanup_part_files(folder: Path) -> None:
    for part_file in folder.rglob("*.part"):
        try:
            part_file.unlink()
        except OSError:
            pass


def collect_output_files(folder: Path) -> list[Path]:
    ignored_suffixes = {".part", ".ytdl", ".tmp"}
    files: list[Path] = []
    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in ignored_suffixes:
            continue
        if path.name.endswith(".backup"):
            continue
        files.append(path)
    return sorted(files, key=lambda p: str(p.relative_to(folder)).lower())


def create_zip(folder: Path, files: list[Path]) -> Path | None:
    media_files = [file for file in files if file.suffix.lower() != ".zip"]
    if len(media_files) < 2:
        return None

    archive = folder / "playlist-download.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in media_files:
            zf.write(file, arcname=str(file.relative_to(folder)))
    return archive


def convert_to_h264(file_path: Path, log: Callable[[str], None], is_cancelled: Callable[[], bool]) -> None:
    ffmpeg = ffmpeg_path()
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for H.264 conversion")

    if is_cancelled():
        raise DownloadCancelled("Download cancelled")

    log("Converting VP9 video to MP4/H.264")
    converted = file_path.with_name(f"CONVERTED_{file_path.name}")
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(file_path),
        "-c:v",
        "libx264",
        "-preset",
        FFMPEG_PRESET,
        "-crf",
        VIDEO_CRF,
        "-c:a",
        "copy",
        str(converted),
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace")[-1200:])

    backup = file_path.with_suffix(file_path.suffix + ".backup")
    if file_path.exists():
        file_path.rename(backup)
    converted.rename(file_path)
    if backup.exists():
        backup.unlink()
    log("H.264 conversion completed")


def run_download(
    *,
    url: str,
    folder: Path,
    kind: str,
    quality: str,
    playlist: bool,
    convert_to_h264_requested: bool,
    update_progress: Callable[[float], None],
    set_phase: Callable[[str], None],
    log: Callable[[str], None],
    is_cancelled: Callable[[], bool],
) -> list[Path]:
    ffmpeg = ffmpeg_path()
    if kind == "mp3" and not ffmpeg:
        raise RuntimeError("ffmpeg is required for MP3 conversion")
    if kind == "video" and not ffmpeg:
        raise RuntimeError("ffmpeg is required for MP4 video merging")
    if convert_to_h264_requested and not ffmpeg:
        raise RuntimeError("ffmpeg is required for H.264 conversion")

    downloaded_file: Path | None = None

    def progress_hook(data: dict) -> None:
        nonlocal downloaded_file
        if is_cancelled():
            raise DownloadCancelled("Download cancelled")

        status = data.get("status")
        if status == "downloading":
            percent = data.get("_percent_str", "0").replace("%", "").strip()
            try:
                update_progress(float(percent))
            except ValueError:
                pass
            set_phase("downloading")
        elif status == "finished":
            filename = data.get("filename")
            if filename:
                downloaded_file = Path(filename)
                log(f"Downloaded {downloaded_file.name}")
            set_phase("processing")

    def postprocessor_hook(data: dict) -> None:
        if is_cancelled():
            raise DownloadCancelled("Download cancelled")
        postprocessor = str(data.get("postprocessor", ""))
        if data.get("status") == "started" and ("Audio" in postprocessor or "Extract" in postprocessor):
            set_phase("converting")
            log("Converting audio to MP3")
        elif data.get("status") == "finished" and ("Audio" in postprocessor or "Extract" in postprocessor):
            log("MP3 conversion completed")

    outtmpl = str(folder / "%(title)s.%(ext)s")
    if playlist:
        outtmpl = str(folder / "%(uploader|playlist_uploader|playlist_title)s" / "%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": outtmpl,
        "noplaylist": not playlist,
        "progress_hooks": [progress_hook],
        "postprocessor_hooks": [postprocessor_hook],
        "quiet": False,
        "no_warnings": True,
        "ignoreerrors": True,
        "noprogress": True,
        "keepvideo": False,
        "abort_on_error": False,
        "logger": CancelAwareLogger(is_cancelled),
        "concurrent_fragment_downloads": CONCURRENT_DOWNLOADS,
        "sleep_interval": SLEEP_INTERVAL,
        "max_sleep_interval": MAX_SLEEP_INTERVAL,
        "retries": MAX_RETRIES,
        "user_agent": USER_AGENT,
    }
    if ffmpeg:
        ydl_opts["ffmpeg_location"] = ffmpeg

    if kind == "mp3":
        log("Mode: MP3 audio")
        ydl_opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": MP3_QUALITY,
                    }
                ],
            }
        )
    else:
        log(f"Mode: MP4 video up to {quality}p")
        if quality == "2160":
            format_str = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
        else:
            format_str = f"bestvideo[height<={quality}][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        ydl_opts.update({"format": format_str, "merge_output_format": "mp4"})

    set_phase("downloading")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if is_cancelled():
        raise DownloadCancelled("Download cancelled")

    if convert_to_h264_requested and downloaded_file and downloaded_file.exists():
        set_phase("converting")
        convert_to_h264(downloaded_file, log, is_cancelled)

    update_progress(100)
    set_phase("completed")
    files = collect_output_files(folder)
    archive = create_zip(folder, files) if playlist else None
    if archive:
        files.append(archive)
    return collect_output_files(folder)
