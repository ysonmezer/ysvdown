import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { Download, Link2, Loader2, Music, Square, Video } from "lucide-react";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_TOKEN = import.meta.env.VITE_API_TOKEN || "";

function authHeaders(extra = {}) {
  return {
    ...extra,
    Authorization: `Bearer ${API_TOKEN}`,
  };
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: authHeaders({
      "Content-Type": "application/json",
      ...(options.headers || {}),
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

function App() {
  const [url, setUrl] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [kind, setKind] = useState("video");
  const [quality, setQuality] = useState("1080");
  const [playlist, setPlaylist] = useState(false);
  const [convertToH264, setConvertToH264] = useState(false);
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const pollRef = useRef(null);

  const isActive = job && ["queued", "running"].includes(job.status);
  const canStart = useMemo(() => url.trim() && analysis && !isActive, [url, analysis, isActive]);

  useEffect(() => {
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, []);

  async function analyze() {
    setError("");
    setAnalysis(null);
    setJob(null);
    setAnalyzing(true);
    try {
      const result = await api("/api/analyze", {
        method: "POST",
        body: JSON.stringify({ url }),
      });
      setAnalysis(result);
      setPlaylist(Boolean(result.isPlaylist));
      if (!result.resolutions.some((resolution) => resolution >= Number(quality))) {
        setQuality("720");
      }
      setConvertToH264(result.has4kH264 === false && quality === "2160");
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  }

  async function startJob() {
    setError("");
    try {
      const result = await api("/api/jobs", {
        method: "POST",
        body: JSON.stringify({
          url,
          kind,
          quality,
          playlist,
          convertToH264: kind === "video" && quality === "2160" && convertToH264,
        }),
      });
      await pollJob(result.jobId);
      pollRef.current = window.setInterval(() => pollJob(result.jobId), 1000);
    } catch (err) {
      setError(err.message);
    }
  }

  async function pollJob(jobId) {
    try {
      const nextJob = await api(`/api/jobs/${jobId}`);
      setJob(nextJob);
      if (["completed", "failed", "cancelled"].includes(nextJob.status) && pollRef.current) {
        window.clearInterval(pollRef.current);
        pollRef.current = null;
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function cancelJob() {
    if (!job) return;
    try {
      await api(`/api/jobs/${job.jobId}/cancel`, { method: "POST" });
      await pollJob(job.jobId);
    } catch (err) {
      setError(err.message);
    }
  }

  async function downloadFile(file) {
    const fileUrl = file.url.startsWith("http") ? file.url : `${API_BASE_URL}${file.url}`;
    const response = await fetch(fileUrl, { headers: authHeaders() });
    if (!response.ok) {
      setError("File download failed");
      return;
    }
    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = file.name.split("/").pop();
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
  }

  return (
    <main className="shell">
      <section className="panel">
        <div className="header">
          <div>
            <h1>YS Video Downloader</h1>
            <p>Download videos or MP3 audio through your OCI backend.</p>
          </div>
          <div className="status">{job?.status || "idle"}</div>
        </div>

        <div className="urlRow">
          <div className="field">
            <label htmlFor="url">Video or playlist URL</label>
            <div className="inputShell">
              <Link2 size={18} />
              <input
                id="url"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
              />
            </div>
          </div>
          <button className="primary" onClick={analyze} disabled={!url.trim() || analyzing || isActive}>
            {analyzing ? <Loader2 className="spin" size={18} /> : <Link2 size={18} />}
            Analyze
          </button>
        </div>

        {analysis && (
          <div className="analysis">
            <strong>{analysis.title}</strong>
            <span>{analysis.isPlaylist ? `Playlist${analysis.playlistCount ? `, ${analysis.playlistCount} videos` : ""}` : "Single video"}</span>
          </div>
        )}

        <div className="controls">
          <div className="segmented">
            <button className={kind === "video" ? "selected" : ""} onClick={() => setKind("video")} disabled={isActive}>
              <Video size={17} /> MP4
            </button>
            <button className={kind === "mp3" ? "selected" : ""} onClick={() => setKind("mp3")} disabled={isActive}>
              <Music size={17} /> MP3
            </button>
          </div>

          <select value={quality} onChange={(event) => setQuality(event.target.value)} disabled={kind === "mp3" || isActive}>
            <option value="720">720p</option>
            <option value="1080">1080p</option>
            <option value="2160">4K</option>
          </select>

          <label className="toggle">
            <input
              type="checkbox"
              checked={playlist}
              onChange={(event) => setPlaylist(event.target.checked)}
              disabled={!analysis?.isPlaylist || isActive}
            />
            Playlist
          </label>

          <label className="toggle">
            <input
              type="checkbox"
              checked={convertToH264}
              onChange={(event) => setConvertToH264(event.target.checked)}
              disabled={kind !== "video" || quality !== "2160" || isActive}
            />
            H.264
          </label>
        </div>

        <div className="actions">
          <button className="primary" onClick={startJob} disabled={!canStart}>
            <Download size={18} />
            Start
          </button>
          <button className="danger" onClick={cancelJob} disabled={!isActive}>
            <Square size={16} />
            Cancel
          </button>
        </div>

        {job && (
          <div className="progressBlock">
            <div className="progressMeta">
              <span>{job.phase}</span>
              <span>{Math.round(job.progress)}%</span>
            </div>
            <div className="bar">
              <div style={{ width: `${job.progress}%` }} />
            </div>
          </div>
        )}

        {error && <div className="error">{error}</div>}

        {job?.files?.length > 0 && (
          <div className="files">
            <h2>Completed files</h2>
            {job.files.map((file) => (
              <button key={file.name} onClick={() => downloadFile(file)}>
                <Download size={16} />
                <span>{file.name}</span>
                <small>{(file.size / 1024 / 1024).toFixed(1)} MB</small>
              </button>
            ))}
          </div>
        )}

        <div className="logs">
          {(job?.logs || []).map((line) => (
            <div key={line}>{line}</div>
          ))}
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
