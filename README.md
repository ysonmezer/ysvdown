# YS Video Downloader Web

This branch rewrites the original Tkinter desktop app as a web app:

- `backend/`: FastAPI service for metadata analysis, download jobs, progress, cancellation, and authenticated file delivery.
- `frontend/`: React + Vite UI intended for Vercel.
- Downloads are stored temporarily on the OCI server and cleaned up after `FILE_TTL_HOURS`.

## Backend Local Development

Install Python dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Install `ffmpeg` and make sure it is available on `PATH`. The Docker image does this automatically, but local MP4 merging, MP3 conversion, and H.264 conversion require it.

Create `backend/.env` from `backend/.env.example`:

```env
API_TOKEN=replace-with-a-long-random-token
FRONTEND_ORIGIN=http://localhost:5173
PUBLIC_BASE_URL=http://localhost:8000
DOWNLOAD_DIR=./downloads
FILE_TTL_HOURS=24
MAX_CONCURRENT_JOBS=1
```

Start the API:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Check health:

```bash
curl http://localhost:8000/health
```

All `/api/*` routes require:

```http
Authorization: Bearer <API_TOKEN>
```

## Frontend Local Development

Create `frontend/.env` from `frontend/.env.example`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TOKEN=replace-with-the-same-token-as-backend
```

Run the app:

```bash
cd frontend
npm install
npm run dev
```

## API

- `POST /api/analyze`
  - Body: `{ "url": "https://..." }`
  - Returns title, playlist status/count, available resolutions, and 4K H.264 availability.
- `POST /api/jobs`
  - Body: `{ "url": "...", "kind": "video", "quality": "1080", "playlist": false, "convertToH264": false }`
  - Returns `{ "jobId": "..." }`.
- `GET /api/jobs/{jobId}`
  - Returns status, progress, phase, logs, errors, and completed file links.
- `POST /api/jobs/{jobId}/cancel`
  - Requests cancellation.
- `GET /api/files/{jobId}/{fileName}`
  - Authenticated completed-file download.

## OCI Deployment

Build and run the backend container:

```bash
docker build -f backend/Dockerfile -t ysvdown-api .
docker run -d \
  --name ysvdown-api \
  -p 8000:8000 \
  --env-file backend/.env \
  -v ysvdown-downloads:/app/downloads \
  ysvdown-api
```

Set `PUBLIC_BASE_URL` to the public HTTPS URL for the OCI backend if file URLs should be absolute.

Put the API behind HTTPS with a reverse proxy such as Nginx or Caddy. Open only the required port in OCI security lists.

## Vercel Deployment

Deploy `frontend/` as the Vercel project root and set:

- `VITE_API_BASE_URL=https://your-oci-api-domain`
- `VITE_API_TOKEN=<same token as API_TOKEN>`

Set backend `FRONTEND_ORIGIN` to the Vercel deployment origin, for example:

```env
FRONTEND_ORIGIN=https://your-project.vercel.app
```

## Security Notes

- Use a long random `API_TOKEN`.
- CORS limits browser access, but the bearer token is still the real authorization control.
- This app can consume bandwidth and disk space quickly. Keep `MAX_CONCURRENT_JOBS=1` unless the OCI instance has enough CPU, memory, and network capacity.
- Downloaded files are temporary local server files. They are removed after `FILE_TTL_HOURS` once their job is complete, failed, or cancelled.
