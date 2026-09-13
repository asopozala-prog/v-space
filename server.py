# Runs the V🌔Space one-minute browser experience against the current local render engine.
from __future__ import annotations

import importlib.util
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

HOST = "127.0.0.1"
PORT = 8788
SITE_ROOT = Path(__file__).resolve().parent

STAGE1 = Path("/Users/kugel/🍄MushroomHouseMusicLab/synchronization/vspace_orchestrator")
RECORDER_PATH = STAGE1 / "orchestration_recorder/orchestration_recorder.py"
RESOLVER_PATH = STAGE1 / "orchestration_resolver/orchestration_resolver.py"
RENDERER_PATH = STAGE1 / "resolved_plan_renderer/render_resolved_plan.py"

ORCHESTRATIONS_DIR = Path("/Users/kugel/V🌔Space/orchestrations")
AUDIO_INGEST_DIR = Path.home() / "Library/Application Support/VSpace/cloud_demo_audio"
VIDEO_OUTPUT_DIR = Path.home() / "Movies/VSpace/CloudDemo"
MODEL_PREVIEW = Path("/Users/kugel/V🌔Space/space_models/01_sand_moon/previews/sand_moon_variations_9x16.gif")

JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()
RENDER_RE = re.compile(r"render\s+([0-9.]+)s\s*/\s*([0-9.]+)s")


def load_recorder():
    spec = importlib.util.spec_from_file_location("recorder", RECORDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load V🌔Space orchestration recorder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RECORDER = load_recorder()


def safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._ -]+", "_", Path(name).name.strip())[:180] or "vspace"


def update_job(job_id: str, **changes):
    with JOBS_LOCK:
        JOBS[job_id].update(changes)


def run_stage(cmd: list[str], label: str) -> str:
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{label} failed: {(result.stderr or result.stdout).strip()[-1800:]}")
    return result.stdout


def ffmpeg_path() -> str:
    candidates = [
        shutil.which("ffmpeg"),
        "/usr/local/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("ffmpeg not found")


def apply_fades(source: Path, target: Path, duration: float):
    fade = min(2.0, max(0.25, duration / 4))
    out_start = max(0.0, duration - fade)

    cmd = [
        ffmpeg_path(), "-y", "-i", str(source),
        "-vf", f"fade=t=in:st=0:d={fade:.3f},fade=t=out:st={out_start:.3f}:d={fade:.3f}",
        "-af", f"afade=t=in:st=0:d={fade:.3f},afade=t=out:st={out_start:.3f}:d={fade:.3f}",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(target),
    ]
    run_stage(cmd, "fade encoding")


def render_process(job_id: str, record_path: Path, raw_video: Path):
    update_job(job_id, label="Analyzing", progress=12)

    process = subprocess.Popen(
        [sys.executable, str(RENDERER_PATH), "--record", str(record_path), "--output", str(raw_video), "--sync-profile", "intensive"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    tail: list[str] = []
    assert process.stdout is not None

    for raw in process.stdout:
        line = raw.strip()
        if line:
            print("[vspace-renderer]", line)
            tail.append(line)
            tail = tail[-80:]

        if line == "vspace-stage analyzing":
            update_job(job_id, label="Analyzing", progress=12)
            continue

        if line == "vspace-stage rendering":
            update_job(job_id, label="Rendering", progress=20)
            continue

        match = RENDER_RE.search(line)
        if match:
            current = float(match.group(1))
            total = max(float(match.group(2)), 0.001)
            fraction = max(0.0, min(1.0, current / total))
            update_job(job_id, label=f"Rendering {round(fraction * 100)}%", progress=20 + fraction * 70)
            continue

        if line == "vspace-stage encoding":
            update_job(job_id, label="Encoding", progress=91)

    return_code = process.wait()
    if return_code:
        raise RuntimeError("renderer failed: " + "\n".join(tail[-20:]))
    if not raw_video.is_file():
        raise RuntimeError("renderer completed without producing an MP4")


def create_job(job_id: str, payload: dict):
    raw_video: Path | None = None
    try:
        audio = Path(payload["audio_path"])
        if not audio.is_file():
            raise ValueError("uploaded music source not found")

        start = max(0.0, float(payload["start_seconds"]))
        requested_end = float(payload["end_seconds"])
        duration = max(0.1, min(60.0, requested_end - start))
        end = start + duration

        update_job(job_id, status="running", label="Preparing", progress=2)

        record = RECORDER.new_record(
            project_name=payload["project_name"],
            audio_path=str(audio),
            start_seconds=start,
            end_seconds=end,
            model_id="01_sand_moon",
            frame_preset="square_1_1",
            model_composition_rule="01_duration_variation_composition",
            camera_composition_rule="03_camera_rule_dynamic_music_push",
            sync_composition_rule="06_sync_rule_rhythmic_pulse",
            vspace_version="v1-one-minute-cloud-demo",
        )
        record["source"]["original_name"] = payload.get("audio_original_name")
        RECORDER.validate_record(record)
        record_path = Path(RECORDER.save_record(record, output_dir=ORCHESTRATIONS_DIR))

        update_job(job_id, label="Resolving", progress=6)
        run_stage([sys.executable, str(RESOLVER_PATH), "--record", str(record_path)], "resolver")

        VIDEO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        stem = f'{datetime.now():%Y-%m-%d_%H%M%S}_{safe(payload["project_name"])}_one-minute'
        raw_video = VIDEO_OUTPUT_DIR / f"{stem}.raw.mp4"
        final_video = VIDEO_OUTPUT_DIR / f"{stem}.mp4"

        render_process(job_id, record_path, raw_video)

        update_job(job_id, label="Encoding", progress=94)
        apply_fades(raw_video, final_video, duration)

        update_job(
            job_id,
            status="ready",
            label="Video Ready",
            progress=100,
            video_path=str(final_video),
            download_name=f"{safe(payload['project_name'])}_vspace_1min.mp4",
        )
    except Exception as exc:
        print("[vspace-one-minute-error]", exc)
        update_job(job_id, status="error", label="Render Error", error=str(exc))
    finally:
        if raw_video and raw_video.exists():
            raw_video.unlink(missing_ok=True)


class Handler(BaseHTTPRequestHandler):
    def json(self, status: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        return json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))).decode())

    def do_POST(self):
        if self.path == "/api/audio":
            return self.audio()
        if self.path == "/api/create-video":
            return self.start_create_video()
        self.json(404, {"error": "not found"})

    def audio(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            original = unquote(self.headers.get("X-VSpace-Filename", "audio"))
            if length <= 0:
                raise ValueError("empty audio upload")

            AUDIO_INGEST_DIR.mkdir(parents=True, exist_ok=True)
            target = AUDIO_INGEST_DIR / f"{uuid.uuid4().hex[:12]}_{safe(original)}"

            remaining = length
            with target.open("wb") as handle:
                while remaining:
                    chunk = self.rfile.read(min(1048576, remaining))
                    if not chunk:
                        raise IOError("audio upload ended unexpectedly")
                    handle.write(chunk)
                    remaining -= len(chunk)

            self.json(201, {"status": "stored", "local_path": str(target)})
        except Exception as exc:
            self.json(400, {"error": str(exc)})

    def start_create_video(self):
        try:
            payload = self.read_json()
            job_id = uuid.uuid4().hex
            with JOBS_LOCK:
                JOBS[job_id] = {
                    "job_id": job_id,
                    "status": "queued",
                    "label": "Preparing",
                    "progress": 1,
                }
            threading.Thread(target=create_job, args=(job_id, payload), daemon=True).start()
            self.json(202, {"status": "started", "job_id": job_id})
        except Exception as exc:
            self.json(400, {"error": str(exc)})

    def render_status(self, query: dict[str, list[str]]):
        job_id = query.get("id", [""])[0]
        with JOBS_LOCK:
            job = dict(JOBS.get(job_id, {}))
        if not job:
            return self.json(404, {"error": "render job not found"})
        public = {key: value for key, value in job.items() if key != "video_path"}
        self.json(200, public)

    def job_video(self, query: dict[str, list[str]]) -> tuple[Path, dict]:
        job_id = query.get("id", [""])[0]
        with JOBS_LOCK:
            job = dict(JOBS.get(job_id, {}))
        path = Path(job.get("video_path", ""))
        if job.get("status") != "ready" or not path.is_file():
            raise FileNotFoundError("rendered video not found")
        return path, job

    def serve_video(self, path: Path):
        size = path.stat().st_size
        range_header = self.headers.get("Range")

        if range_header:
            match = re.match(r"bytes=(\d*)-(\d*)", range_header)
            if not match:
                return self.send_error(416)
            start = int(match.group(1) or 0)
            end = int(match.group(2) or size - 1)
            end = min(end, size - 1)
            if start > end:
                return self.send_error(416)

            length = end - start + 1
            self.send_response(206)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

            with path.open("rb") as handle:
                handle.seek(start)
                remaining = length
                while remaining:
                    chunk = handle.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
            return

        self.send_response(200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Content-Length", str(size))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        with path.open("rb") as handle:
            shutil.copyfileobj(handle, self.wfile)

    def do_GET(self):
        parsed = urlparse(self.path)
        req = unquote(parsed.path)
        query = parse_qs(parsed.query)

        if req == "/api/render-status":
            return self.render_status(query)

        if req == "/rendered-video":
            try:
                path, _ = self.job_video(query)
                return self.serve_video(path)
            except FileNotFoundError:
                return self.send_error(404)

        if req == "/download-video":
            try:
                path, job = self.job_video(query)
            except FileNotFoundError:
                return self.send_error(404)

            data = path.read_bytes()
            name = job.get("download_name", "vspace-one-minute.mp4")
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Disposition", f'attachment; filename="{name}"')
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return

        if req == "/model-preview/sand-moon.gif":
            target = MODEL_PREVIEW
        else:
            if req == "/":
                req = "/index.html"
            target = (SITE_ROOT / req.lstrip("/")).resolve()
            if SITE_ROOT not in target.parents and target != SITE_ROOT:
                return self.send_error(403)

        if not target.is_file():
            return self.send_error(404)

        data = target.read_bytes()
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print("[vspace-one-minute]", fmt % args)


def main():
    for path in (ORCHESTRATIONS_DIR, AUDIO_INGEST_DIR, VIDEO_OUTPUT_DIR):
        path.mkdir(parents=True, exist_ok=True)

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"V🌔Space one-minute browser: http://{HOST}:{PORT}")
    print("Output: 1:1 · maximum 60 seconds · 2 second audio/video fades")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
