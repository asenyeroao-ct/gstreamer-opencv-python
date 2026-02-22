#!/usr/bin/env python3
"""
修復 .whl 內 dist-info 的 WHEEL / METADATA / RECORD：移除 UTF-8 BOM，
避免 pip 報「WHEEL is missing Wheel-Version」或「invalid metadata entry 'name'」。
用法: python fix_wheel_wheel_file.py <path_to.whl> [out.whl]
"""
import sys
import zipfile
import tempfile
import os
import shutil

BOM = b"\xef\xbb\xbf"

def strip_bom(raw: bytes) -> bytes:
    return raw[3:] if raw.startswith(BOM) else raw

def fix_wheel(whl_path: str, out_path: str | None = None) -> bool:
    """修復單一 .whl，回傳 True 表示有寫入修復，False 表示無需修復。"""
    out_path = out_path or whl_path
    if not whl_path.lower().endswith(".whl"):
        print(f"不是 .whl 檔: {whl_path}")
        sys.exit(1)
    if not os.path.isfile(whl_path):
        print(f"檔案不存在: {whl_path}")
        sys.exit(1)

    replacements = {}
    with zipfile.ZipFile(whl_path, "r") as z:
        names = z.namelist()
        wheel_name = next((x for x in names if x.endswith("WHEEL") and "dist-info" in x), None)
        for n in names:
            if "dist-info" not in n:
                continue
            if n.endswith("WHEEL") or n.endswith("METADATA") or n.endswith("RECORD"):
                raw = z.read(n)
                if raw.startswith(BOM):
                    replacements[n] = strip_bom(raw)

        if wheel_name:
            content = replacements.get(wheel_name) or z.read(wheel_name)
            if content.startswith(BOM):
                content = strip_bom(content)
            if b"Wheel-Version:" not in content:
                print("WHEEL 內容缺少 Wheel-Version，無法自動修復。")
                sys.exit(1)

        if not replacements:
            return False

    same_dir = os.path.dirname(out_path) or "."
    fd, tmp_path = tempfile.mkstemp(suffix=".whl", dir=same_dir)
    os.close(fd)
    try:
        with zipfile.ZipFile(whl_path, "r") as z_in:
            with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as z_out:
                for name in z_in.namelist():
                    if name in replacements:
                        z_out.writestr(name, replacements[name])
                    else:
                        z_out.writestr(name, z_in.read(name))
        if os.path.abspath(tmp_path) != os.path.abspath(out_path):
            shutil.move(tmp_path, out_path)
        else:
            shutil.move(tmp_path, out_path + ".new")
            os.replace(out_path + ".new", out_path)
        print("已修復並寫入:", out_path)
        return True
    except Exception as e:
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
        raise e

def fix_all_wheels_in_dir(dir_path: str) -> None:
    """修復目錄下所有 .whl（遞迴）。"""
    if not os.path.isdir(dir_path):
        print(f"不是目錄: {dir_path}")
        sys.exit(1)
    total = 0
    fixed = 0
    for root, _dirs, files in os.walk(dir_path):
        for f in files:
            if f.lower().endswith(".whl"):
                total += 1
                whl_path = os.path.join(root, f)
                try:
                    if fix_wheel(whl_path, whl_path):
                        fixed += 1
                except SystemExit:
                    raise
                except Exception as e:
                    print(f"修復失敗 {whl_path}: {e}")
    print(f"共掃描 {total} 個 wheel，修復 {fixed} 個。")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fix_wheel_wheel_file.py <path_to.whl> [out.whl]")
        print("       python fix_wheel_wheel_file.py <目錄>   # 修復該目錄下所有 .whl")
        sys.exit(1)
    target = sys.argv[1]
    if os.path.isdir(target):
        fix_all_wheels_in_dir(target)
    else:
        out = sys.argv[2] if len(sys.argv) > 2 else None
        fix_wheel(target, out)
        # 單檔模式不特別區分有無修復
