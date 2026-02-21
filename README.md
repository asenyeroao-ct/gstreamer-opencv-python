# OpenCV + GStreamer Wheels (Windows)

Pre-built **OpenCV with GStreamer** support on **Windows**, producing wheels for Python 3.11–3.13.  
For users with capture cards, real-time / low-latency streaming needs, GStreamer pipelines, and who prefer not to build OpenCV themselves.

---

## Overview

- `pip install opencv-python` has **no** GStreamer support by default; this repo provides pre-built wheels with GStreamer.
- **Windows only.** Python versions: **3.11, 3.12, 3.13**.

---

## Project structure

```
GST-openCV/
├── README.md            # This file
├── build_workspace/     # Build directory (clone OpenCV here, run CMake and build)
└── wheels/              # Built wheels, organized by Python version
    ├── cp311/           # Python 3.11 wheels
    ├── cp312/           # Python 3.12 wheels
    └── cp313/           # Python 3.13 wheels
```

- **Build**: Do all compilation inside `build_workspace/` (clone opencv, opencv_contrib, build). See [build_workspace/README.md](build_workspace/README.md).
- **Output**: Copy built wheels from the build directory into `wheels/cp3xx/`, then upload from there to GitHub Releases or PyPI.

---

## Using pre-built wheels (end users)

1. Install [GStreamer Runtime (MSVC x86_64)](https://gstreamer.freedesktop.org/download/) and ensure `C:\Program Files\gstreamer\1.0\msvc_x86_64\bin` is on PATH, or use `os.add_dll_directory(...)` in your code.
2. Download the matching `.whl` for your Python version from [Releases](https://github.com/asenyeroao-ct/opencv-gstreamer-python/releases).
3. Install: `pip install opencv_gst-xxx-cp3xx-cpxx-win_amd64.whl`
4. Verify GStreamer: `print(cv2.getBuildInformation())` should show `GStreamer: YES`.

---

## References

- [Building OpenCV + GStreamer on Windows (Medium)](https://medium.com/@kenancan.dev/building-opencv-gstreamer-on-windows-a-8-hour-battle-bdb3211aa834)
- [python-opencv-gstreamer-examples](https://github.com/mad4ms/python-opencv-gstreamer-examples)
