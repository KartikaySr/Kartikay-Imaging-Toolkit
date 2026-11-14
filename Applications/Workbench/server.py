"""Kartikay Imaging Toolkit workbench API. SPDX-License-Identifier: Apache-2.0."""
import os
from pathlib import Path
import subprocess
import threading
import time
from flask import Flask, Response, jsonify, request

ROOT = Path(__file__).resolve().parent
PROCESSOR = Path(os.environ.get("KIT_PROCESSOR", ROOT / "build/kit_processor"))
app = Flask(__name__, static_folder="static", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
slots = threading.BoundedSemaphore(2)

@app.after_request
def headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' blob: data:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/")
def index():
    return app.send_static_file("index.html")

@app.get("/api/health")
def health():
    ready = PROCESSOR.is_file() and os.access(PROCESSOR, os.X_OK)
    return jsonify(ready=ready, engine="C++17"), 200 if ready else 503

@app.errorhandler(413)
def too_large(error):
    return jsonify(error="Image exceeds the 1024 × 1024 pixel limit."), 413

@app.post("/api/process")
def process():
    if request.mimetype != "application/octet-stream":
        return jsonify(error="Expected an 8-bit grayscale pixel buffer."), 415
    try:
        operation = request.args["operation"]
        width, height, amount, seed_x, seed_y = [int(request.args[key]) for key in ("width", "height", "amount", "x", "y")]
        if operation not in {"threshold", "region", "noise", "smooth"}:
            raise ValueError()
        if not (1 <= width <= 1024 and 1 <= height <= 1024 and 0 <= amount <= 255 and 0 <= seed_x < width and 0 <= seed_y < height):
            raise ValueError()
        pixels = request.get_data()
        if len(pixels) != width * height:
            raise ValueError()
    except (KeyError, ValueError):
        return jsonify(error="Invalid operation, dimensions, parameters, or pixel buffer."), 400
    if not slots.acquire(blocking=False):
        return jsonify(error="Processor busy. Try again shortly."), 429
    try:
        started = time.perf_counter()
        result = subprocess.run([str(PROCESSOR), operation, str(width), str(height), str(amount), str(seed_x), str(seed_y)], input=pixels, capture_output=True, timeout=15, check=True)
        if len(result.stdout) != len(pixels):
            raise RuntimeError("Invalid processor output")
        return Response(result.stdout, mimetype="application/octet-stream", headers={"Server-Timing": f"process;dur={(time.perf_counter() - started) * 1000:.2f}"})
    except subprocess.TimeoutExpired:
        return jsonify(error="Processing timed out. Try a smaller image."), 504
    except (OSError, subprocess.CalledProcessError, RuntimeError):
        app.logger.exception("Processing failed")
        return jsonify(error="Processing engine unavailable."), 503
    finally:
        slots.release()
