"""
Kiểm tra tĩnh Frontend:
1. Mọi file HTML tham chiếu CSS/JS phải tồn tại.
2. Mọi endpoint khai báo trong js/api.js phải có trong OpenAPI Backend.

Chạy:
    python QA/frontend/check_frontend.py [base_url]
"""

import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FRONTEND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "Frontend")
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

issues = []


def main():
    # 1. File tham chiếu
    html_files = []
    for name in os.listdir(FRONTEND):
        if name.endswith(".html"):
            html_files.append(os.path.join(FRONTEND, name))

    for html_path in sorted(html_files):
        with open(html_path, encoding="utf-8") as f:
            content = f.read()
        for ref in re.findall(r'(?:src|href)="([^"]+)"', content):
            if ref.startswith(("http://", "https://", "#", "mailto:")):
                continue
            local = os.path.normpath(os.path.join(os.path.dirname(html_path), ref.split("?")[0]))
            if not os.path.isfile(local):
                issues.append(f"[THIEU_FILE] {os.path.basename(html_path)} -> {ref}")

    # 2. Endpoint api.js vs OpenAPI
    try:
        import urllib.request

        with urllib.request.urlopen(f"{BASE_URL}/openapi.json", timeout=10) as resp:
            openapi = json.loads(resp.read().decode("utf-8"))
        api_paths = set(openapi.get("paths", {}).keys())
    except Exception as exc:  # noqa: BLE001
        issues.append(f"[OPENAPI] Không đọc được OpenAPI từ {BASE_URL}: {exc}")
        api_paths = None

    api_js_path = os.path.join(FRONTEND, "js", "api.js")
    if api_paths is not None and os.path.isfile(api_js_path):
        with open(api_js_path, encoding="utf-8") as f:
            api_js = f.read()
        start = api_js.find("endpoints: {")
        endpoints = []
        if start == -1:
            issues.append("[API_JS] Không tìm thấy khối endpoints trong api.js")
        else:
            depth = 0
            i = api_js.find("{", start)
            end = i
            for j in range(i, len(api_js)):
                if api_js[j] == "{":
                    depth += 1
                elif api_js[j] == "}":
                    depth -= 1
                    if depth == 0:
                        end = j + 1
                        break
            block = api_js[i:end]
            endpoints = re.findall(r'^\s*([A-Za-z]+):\s*"([^"]+)"', block, re.MULTILINE)
        seen = set()
        for name, path in endpoints:
            if name in seen:
                continue
            seen.add(name)
            pattern = re.sub(r"\{[^}]+\}", "{}", path)
            normalized_paths = {re.sub(r"\{[^}]+\}", "{}", p) for p in api_paths}
            if pattern not in normalized_paths:
                issues.append(f"[ENDPOINT] api.js '{name}' -> {pattern} không có trong OpenAPI")

    if issues:
        print(f"TÌM THẤY {len(issues)} VẤN ĐỀ:")
        for issue in issues:
            print(" -", issue)
        return 1
    print("OK: mọi file tham chiếu tồn tại và mọi endpoint trong api.js đều có trong OpenAPI.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
