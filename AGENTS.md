# AGENTS.md — OpenCV + GStreamer Wheels (Windows)

Guidance for this repo and for AI / maintainers.

---

## Project scope

- **Goal**: Build **OpenCV with GStreamer** on **Windows**, produce **wheels**, and publish to GitHub Releases (or PyPI).
- **Python versions**: **3.11, 3.12, 3.13**.
- **Target users**:
  - **Capture card** users
  - **Real-time / low-latency** streaming needs
  - **GStreamer pipeline** usage (e.g. RTSP, appsink/appsrc)
  - Prefer **not building OpenCV** themselves; want `pip install` or a ready-made wheel.

**Important**: `pip install opencv-python` has **no** GStreamer support by default; this repo exists to fill that gap.

---

## References (required reading)

- **Windows build guide**: [Building OpenCV + GStreamer on Windows: A 8-Hour Battle](https://medium.com/@kenancan.dev/building-opencv-gstreamer-on-windows-a-8-hour-battle-bdb3211aa834)  
  - Tools: VS2022, CMake, GStreamer MSVC dev + runtime, Python 3.9+
  - Recommended OpenCV **4.9.0** (4.10.0 has compatibility issues with VS2022)
  - Key CMake: `WITH_GSTREAMER=ON`, `BUILD_SHARED_LIBS=ON`, `BUILD_opencv_gapi=OFF`
  - Python 3.8+ on Windows needs `os.add_dll_directory()` for GStreamer/OpenCV DLLs
- **GStreamer + OpenCV examples**: [mad4ms/python-opencv-gstreamer-examples](https://github.com/mad4ms/python-opencv-gstreamer-examples)  
  - Linux-oriented (v4l2, shm, RTP, Intel/NVIDIA HW enc); pipeline concepts and `cv2.CAP_GSTREAMER` usage are useful for docs/examples.

---

## Build environment (Windows)

When suggesting or writing build scripts, use:

| Item | Description |
|------|-------------|
| OS | Windows 10/11 (Windows only) |
| Compiler | Visual Studio 2022 (MSVC v143, Windows 10/11 SDK, C++ desktop, CMake tools) |
| CMake | Latest, on PATH (this repo uses: `C:\Program Files\CMake\bin`) |
| GStreamer | [GStreamer downloads](https://gstreamer.freedesktop.org/download/) — **MSVC x86_64** **Runtime + Devel**; install both to the same directory (this repo: `C:\Program Files\gstreamer\1.0\msvc_x86_64`) |
| Env vars | `GSTREAMER_1_0_ROOT_MSVC_X86_64`, `GSTREAMER_ROOT_X86_64` point to GStreamer root; PATH includes `...\bin` and `...\lib` |
| Python | 3.11, 3.12, 3.13 (build separate wheels per version) |
| Deps | `pip install wheel setuptools numpy` (for building wheels) |

### Default paths for this repo (prefer in build scripts / CI)

| Purpose | Path |
|---------|------|
| **GStreamer** | `C:\Program Files\gstreamer\1.0\msvc_x86_64` |
| **CMake** | `C:\Program Files\CMake\bin` |

Example env vars (for the GStreamer path above):

- `GSTREAMER_1_0_ROOT_MSVC_X86_64` = `C:\Program Files\gstreamer\1.0\msvc_x86_64`
- `GSTREAMER_ROOT_X86_64` = `C:\Program Files\gstreamer\1.0\msvc_x86_64`
- Add to PATH: `C:\Program Files\gstreamer\1.0\msvc_x86_64\bin`, `C:\Program Files\gstreamer\1.0\msvc_x86_64\lib`

If CMake does not find GStreamer automatically, set the variables below.

---

## Key CMake settings

When building OpenCV, ensure:

- **WITH_GSTREAMER** = ON  
- **BUILD_SHARED_LIBS** = ON (otherwise Python cannot load DLLs)  
- **BUILD_opencv_gapi** = OFF (avoids chrono/etc. issues with VS2022)  
- **OPENCV_EXTRA_MODULES_PATH** = opencv_contrib modules (if using contrib)  
- **BUILD_opencv_world** = ON (single DLL, easier packaging and DLL path setup)

If GStreamer is not detected, set these manually. **Default GStreamer path** for this repo: `C:\Program Files\gstreamer\1.0\msvc_x86_64` (use `/` in CMake, e.g. `C:/Program Files/gstreamer/1.0/msvc_x86_64`):

- `GSTREAMER_DIR` = `C:/Program Files/gstreamer/1.0/msvc_x86_64`
- `GSTREAMER_INCLUDE_DIR` = `C:/Program Files/gstreamer/1.0/msvc_x86_64/include/gstreamer-1.0`
- `GSTREAMER_LIBRARY` = `C:/Program Files/gstreamer/1.0/msvc_x86_64/lib/gstreamer-1.0.lib`
- `GSTREAMER_APP_LIBRARY` = `C:/Program Files/gstreamer/1.0/msvc_x86_64/lib/gstapp-1.0.lib`
- `GSTREAMER_BASE_LIBRARY` = `C:/Program Files/gstreamer/1.0/msvc_x86_64/lib/gstbase-1.0.lib`
- `GSTREAMER_VIDEO_LIBRARY` = `C:/Program Files/gstreamer/1.0/msvc_x86_64/lib/gstvideo-1.0.lib`
- `GLIB2_LIBRARY` = `C:/Program Files/gstreamer/1.0/msvc_x86_64/lib/glib-2.0.lib`
- `GOBJECT2_LIBRARY` = `C:/Program Files/gstreamer/1.0/msvc_x86_64/lib/gobject-2.0.lib`

Success: CMake should show `Video I/O: GStreamer: YES`.

---

## Build output and packaging

- Build target: `opencv_python3` (or the project’s Python binding target).  
- Output: `cv2.*.pyd` and `opencv_world*.dll`, etc.  
- **Wheel**: Package the above plus required DLLs (or document GStreamer path for `os.add_dll_directory`). If the wheel does not bundle GStreamer, document that users must install GStreamer Runtime and set PATH or `add_dll_directory`.  
- Naming: Include OpenCV version, Python version, GStreamer version (e.g. `opencv_gst-4.9.0-cp311-cp311-win_amd64.whl`).

---

## CI / automation (suggested)

- Use **GitHub Actions** with **windows-latest**.  
- Install in workflow: VS build tools, CMake, GStreamer (MSI silent install or pre-installed image), Python 3.11/3.12/3.13 (matrix).  
- Flow: clone OpenCV + opencv_contrib → set env and CMake → build → package wheel → upload to Artifacts or GitHub Release.  
- If GStreamer is not on the runner, use cache or a self-hosted runner with GStreamer pre-installed.

---

## Docs and examples (suggested)

- **README**: Describe pre-built OpenCV + GStreamer wheels, supported Python versions, install (pip or Release), and **GStreamer Runtime install and PATH/add_dll_directory**.  
- Reference [python-opencv-gstreamer-examples](https://github.com/mad4ms/python-opencv-gstreamer-examples) for pipeline ideas; add Windows examples (e.g. RTSP, videotestsrc, Capture Card via DirectShow/Media Foundation → GStreamer) under `examples/` or in docs.  
- Include a short “verify GStreamer” snippet (`cv2.getBuildInformation()` shows `GStreamer: YES` and a simple `cv2.CAP_GSTREAMER` pipeline test).

---

## Version policy

- **OpenCV**: Prefer 4.9.x (per reference article); if moving to 4.10+, verify VS2022 compatibility (chrono, GAPI).  
- **GStreamer**: Use 1.22+ / 1.24+ MSVC builds; note recommended Runtime version in README.  
- **Python**: Only 3.11, 3.12, 3.13; build scripts and CI matrix use only these.

---

## Pushing to GitHub (manual)

**When the user asks to “upload to GitHub” or “push to GitHub”**: Do **not** run `git push` for them. Instead, provide this **code block** so they can run it themselves:

```bash
git add -A
git commit -m "Your message"
git push
```

- Replace `"Your message"` with a short, meaningful commit message for the changes.  
- The user will run these three commands to push.

---

## Short checklist for AI

1. All builds and scripts target **Windows** only.  
2. When building wheels, handle **DLL search path** (in wheel or document GStreamer install and `add_dll_directory`).  
3. CMake must have **WITH_GSTREAMER=ON**, **BUILD_SHARED_LIBS=ON**, **BUILD_opencv_gapi=OFF**.  
4. CI uses only Python **3.11 / 3.12 / 3.13**.  
5. Docs must describe target users (capture cards, streaming, GStreamer pipeline, no self-build OpenCV) and reference the Medium article and example repo.  
6. **GitHub push**: Only provide the `git add -A` / `git commit -m "..."` / `git push` code block; do not run `git push` for the user.

When adding build scripts, CI workflows, or README sections, follow the above and cite the Medium article and mad4ms examples repo.
