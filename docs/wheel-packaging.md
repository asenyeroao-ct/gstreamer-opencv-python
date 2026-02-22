# Wheel 打包說明 (OpenCV + GStreamer)

本文件說明本專案如何將編譯好的 OpenCV Python 綁定打包成 `.whl`，以及 wheel 內部結構與注意事項。

---

## 1. Wheel 檔名規則

```
opencv_gst-<OpenCV版本>-<Python標籤>-<Python標籤>-win_amd64.whl
```

範例：
- `opencv_gst-4.9.0-cp311-cp311-win_amd64.whl` — OpenCV 4.9.0，Python 3.11
- `opencv_gst-4.13.0-cp312-cp312-win_amd64.whl` — OpenCV 4.13.0，Python 3.12

對應的 **pip 套件名稱** 為 `opencv-gst`（在 METADATA 的 `Name:` 欄位）。

---

## 2. Wheel 內部結構（.whl 實為 ZIP）

解壓後目錄結構：

```
opencv_gst-<version>.dist-info/
├── METADATA      # PyPI 元資料 (Name, Version, Summary, Requires-Python 等)
├── WHEEL         # Wheel 格式版本與 tag
└── RECORD         # 檔案清單與雜湊 (pip 安裝時會重算)
cv2/
├── __init__.py   # 套件初始化（可含 add_dll_directory 提示）
├── cv2.*.pyd     # OpenCV Python 綁定 (Windows DLL)
└── opencv_world*.dll   # OpenCV 共用庫（可選，依建置設定）
```

- **cv2/**：實際的 Python 套件，`import cv2` 會載入此目錄。
- **opencv_gst-\<version>.dist-info/**：標準 [PEP 491](https://peps.python.org/pep-0491/) wheel 元資料目錄。

---

## 3. 各檔案用途與格式

| 路徑 | 說明 | 格式要求 |
|------|------|----------|
| `cv2/__init__.py` | 套件入口，可提醒使用者設定 GStreamer DLL 路徑 | UTF-8 **無 BOM** |
| `cv2/cv2.*.pyd` | 從 CMake 建置輸出複製 | 二進位 |
| `cv2/opencv_world*.dll` | 從 CMake 建置輸出複製（若有） | 二進位 |
| `*.dist-info/METADATA` | [Core metadata](https://packaging.python.org/en/latest/specifications/core-metadata/) (Name, Version, Summary, Requires-Python) | UTF-8 **無 BOM** |
| `*.dist-info/WHEEL` | Wheel 版本與 tag，例如 `Tag: cp312-cp312-win_amd64` | UTF-8 **無 BOM** |
| `*.dist-info/RECORD` | 列出 wheel 內每個檔案的相對路徑與 (選填) 雜湊、大小 | UTF-8 **無 BOM**，每行一筆 |

**重要**：PowerShell 的 `Set-Content -Encoding UTF8` 會寫入 BOM，pip 會因此報錯（如「WHEEL is missing Wheel-Version」「invalid metadata entry 'name'」）。建置腳本一律使用 **無 BOM 的 UTF-8**，例如：

```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
```

---

## 4. 打包流程（與 build_wheel_*.ps1 對應）

1. **準備 staging 目錄**  
   在 build 目錄下建立 `wheel_staging/`，其下建立 `cv2/` 與 `opencv_gst-<version>.dist-info/`。

2. **複製建置產物**  
   - 將 `cv2*.pyd`、`opencv_world*.dll` 複製到 `wheel_staging/cv2/`。

3. **寫入 cv2 套件**  
   - 在 `cv2/` 下寫入 `__init__.py`（UTF-8 無 BOM）。

4. **寫入 dist-info**  
   - **METADATA**：`Metadata-Version: 2.1`、`Name: opencv-gst`、`Version`、`Summary`、`Requires-Python: >=3.11`。  
   - **WHEEL**：`Wheel-Version: 1.0`、`Generator`、`Root-Is-Purelib: false`、`Tag: <py_tag>-<py_tag>-win_amd64`。  
   - **RECORD**：列出 `cv2/` 與 `dist-info/` 內所有檔案（路徑, sha256=_, 大小），最後一筆為 `RECORD` 自身（結尾 `,,`）。  
   以上皆以 **UTF-8 無 BOM** 寫入。

5. **壓縮為 wheel**  
   - 對 `wheel_staging/*` 做 ZIP（`Compress-Archive`），再將副檔名改為 `.whl`，輸出到 `wheels/<opencv_version>/cp3xx/`。

---

## 5. 既有 wheel 的 BOM 修復

若既有 `.whl` 的 METADATA/WHEEL/RECORD 帶有 UTF-8 BOM，可用專案內腳本批次修復：

```powershell
# 修復單一 wheel
python scripts/fix_wheel_wheel_file.py path/to/file.whl

# 修復 wheels/ 目錄下所有 .whl
python scripts/fix_wheel_wheel_file.py wheels
```

詳見 `scripts/fix_wheel_wheel_file.py` 註解。

---

## 6. 參考

- [PEP 491 – Wheel binary package format](https://peps.python.org/pep-0491/)
- [Core metadata specification](https://packaging.python.org/en/latest/specifications/core-metadata/)
- 本專案建置腳本：`build_workspace/build_wheel_cp311.ps1`、`build_wheel_cp312.ps1`、`build_wheel_4.13_cp*.ps1` 等。
