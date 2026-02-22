#!/usr/bin/env python3
"""
修復 .whl 內的 WHEEL 檔案：移除 BOM，確保 pip 能辨識 Wheel-Version。
用法: python fix_wheel_wheel_file.py <path_to.whl>
會覆寫原檔（建議先備份或指定輸出路徑）。
"""
import sys
import zipfile
import tempfile
import os
import shutil

def fix_wheel(whl_path: str, out_path: str | None = None) -> None:
    out_path = out_path or whl_path
    if not whl_path.lower().endswith(".whl"):
        print(f"不是 .whl 檔: {whl_path}")
        sys.exit(1)
    if not os.path.isfile(whl_path):
        print(f"檔案不存在: {whl_path}")
        sys.exit(1)

    with zipfile.ZipFile(whl_path, "r") as z:
        names = z.namelist()
        wheel_name = None
        for n in names:
            if n.endswith(".dist-info/WHEEL") or (n.endswith("WHEEL") and "dist-info" in n):
                wheel_name = n
                break
        if not wheel_name:
            print("此 wheel 內找不到 WHEEL 檔。")
            sys.exit(1)

        raw = z.read(wheel_name)
        # 移除 BOM
        if raw.startswith(b"\xef\xbb\xbf"):
            new_content = raw[3:]
        else:
            new_content = raw

        if b"Wheel-Version:" not in new_content:
            print("WHEEL 內容缺少 Wheel-Version，無法自動修復。")
            sys.exit(1)

        # 寫入新 zip（其餘成員不變，只替換 WHEEL 內容）
        same_dir = os.path.dirname(out_path) or "."
        fd, tmp_path = tempfile.mkstemp(suffix=".whl", dir=same_dir)
        os.close(fd)
        try:
            with zipfile.ZipFile(whl_path, "r") as z_in:
                with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as z_out:
                    for name in z_in.namelist():
                        if name == wheel_name:
                            z_out.writestr(name, new_content)
                        else:
                            z_out.writestr(name, z_in.read(name))
            if os.path.abspath(tmp_path) != os.path.abspath(out_path):
                shutil.move(tmp_path, out_path)
            else:
                shutil.move(tmp_path, out_path + ".new")
                os.replace(out_path + ".new", out_path)
            print(f"已修復並寫入: {out_path}")
        except Exception as e:
            if os.path.isfile(tmp_path):
                os.remove(tmp_path)
            raise e

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fix_wheel_wheel_file.py <path_to.whl> [out.whl]")
        sys.exit(1)
    whl = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    fix_wheel(whl, out)
