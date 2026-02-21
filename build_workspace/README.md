# Build workspace (build_workspace)

All **OpenCV + GStreamer** compilation is done in this directory.

## How to use

1. **In this directory**, clone OpenCV and opencv_contrib (or use a script):
   - `opencv/` — main repo
   - `opencv_contrib/` — extra modules (optional)

2. Create a `build/` (or your preferred) directory here and run CMake configure and build.  
   Default paths for this repo: **GStreamer** `C:\Program Files\gstreamer\1.0\msvc_x86_64`, **CMake** `C:\Program Files\CMake\bin`.

3. After building, **copy** the resulting **wheel** (or the wheel you package from `cv2.*.pyd` and DLLs) **out** to the parent `wheels/` folder by Python version:
   - **Python 3.11** → `../wheels/cp311/`
   - **Python 3.12** → `../wheels/cp312/`
   - **Python 3.13** → `../wheels/cp313/`

You can then upload from `wheels/` to GitHub Releases or PyPI.

## Notes

- `opencv/`, `opencv_contrib/`, `build/`, and build artifacts under this directory are in `.gitignore` and will not be committed.
- Only this README and any build scripts you add are tracked.
