"""Upstage API 키가 동작하는지 확인한다. 키 값은 출력하지 않는다.

    uv run python tools/upstage_smoke.py

.env의 UPSTAGE_API_KEY를 읽는다. 모델 이름은 UPSTAGE_MODEL로 바꿀 수 있다.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENDPOINT = "https://api.upstage.ai/v1/chat/completions"
DEFAULT_MODEL = "solar-pro2"
TIMEOUT_SECONDS = 30


def read_env(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    pairs = (
        line.split("=", 1)
        for line in path.read_text(encoding="utf-8").splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    )
    return {key.strip(): value.strip().strip("\"'") for key, value in pairs}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    env = {**read_env(ROOT / ".env"), **os.environ}
    key = env.get("UPSTAGE_API_KEY", "")
    if not key or key.startswith("여기에"):
        print(".env에 UPSTAGE_API_KEY가 없습니다. console.upstage.ai에서 키를 발급해 .env에 직접 넣으세요.")
        return 2
    model = env.get("UPSTAGE_MODEL", DEFAULT_MODEL)
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": "Reply with OK."}], "max_tokens": 5})
    request = urllib.request.Request(
        ENDPOINT, data=body.encode(), method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            reply = json.load(response)["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:300]
        print(f"실패: HTTP {error.code} (모델 {model})\n{detail}")
        print("401이면 키를, 404·400이면 UPSTAGE_MODEL의 모델 이름을 콘솔 문서에서 확인하세요.")
        return 1
    except urllib.error.URLError as error:
        print(f"실패: 연결할 수 없습니다 — {error.reason}")
        return 1
    print(f"연결 성공 (모델 {model}) — 응답: {reply!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
