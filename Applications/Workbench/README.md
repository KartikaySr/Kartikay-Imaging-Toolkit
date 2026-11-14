# Slice workbench

Kartikay Imaging Toolkit's browser interface for 2D research images. Start with the synthetic phantom or import a PNG or JPEG. The browser converts the image to 8-bit grayscale and fits it within 1024 × 1024 pixels. Choose a filter, compare the source and output, then export the result as PNG.

The standalone C++17 processor implements threshold masking, four-connected region growing from an (x, y) seed, Gaussian noise with a fixed seed, and box smoothing. The web service processes the grayscale buffer in memory. The native ITK library provides the wider project's volume-processing APIs.

## Run with Docker

From the repository root:

```sh
docker build -t kartikay-workbench Applications/Workbench
docker run --rm -p 127.0.0.1:8080:8080 kartikay-workbench
```

Open http://localhost:8080. Container hosts can set the PORT environment variable and use /api/health for readiness. Terminate HTTPS at the host's reverse proxy.

## Build and test locally

From Applications/Workbench on macOS or Linux:

```sh
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/gunicorn --bind 127.0.0.1:8080 server:app
```
