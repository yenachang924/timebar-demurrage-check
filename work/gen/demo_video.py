"""Studio 화면 캡처(work/runs/demo/a2, b2)에 자막을 붙여 데모 영상(mp4)을 만든다.

사용: uv run python work/gen/demo_video.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "work" / "runs" / "demo"
OUT_DIR = DEMO / "out"
TEAM = json.loads((ROOT / "team.json").read_text(encoding="utf-8"))
TARGET = ROOT / "submission" / f"{TEAM['team']}_{TEAM['phase']}_데모영상.mp4"

W, H, BAR = 1680, 950, 90
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"
CARD_SECONDS = 6.0
RUN_SPEED = 3.0

# (폴더, 시작 ms, 끝 ms, 배속, 자막)
SEGMENTS = [
    ("a2", 0, 8300, 1.0, "Upload: the handler drops one claim package into the workflow. A single PDF with five documents."),
    ("a2", 8300, 23000, 1.0, "The file appears in the list. Select it and press Run."),
    ("a2", 23000, 55100, RUN_SPEED, "Running: Parse, Classify, Extract, Merge, Instruct. About 30 seconds per package (shown at 3x)."),
    ("b2", 0, 11940, 1.0, "Step 1, Parse: every page is read with OCR, including scans."),
    ("b2", 11940, 22360, 1.0, "Step 2, Classify: the bundle is split into document types. Page 5 is the cargo pumping log."),
    ("b2", 22360, 29644, 1.0, "Step 3, Extract: the terminal signature line is empty. chief officer signed = true, terminal signed = false."),
    ("b2", 29644, 39467, 1.0, "Step 4, Instruct (the graded node): decision \"보완 요청\" = request documents, with a one-line reason."),
    ("b2", 39467, 49057, 1.0, "Step 5, Instruct: the next document. A draft letter to Owners asking for the countersigned log."),
    ("b2", 49057, 59184, 1.0, "Second case: a blurred scan, with one time box smudged out on the Statement of Facts."),
    ("b2", 59184, 67723, 1.0, "Decision \"검토 필요\" = review needed. The workflow does not guess the hidden time."),
    ("b2", 67723, 75162, 1.0, "The follow-up memo tells the handler where to look."),
    ("b2", 75162, 79777, 1.0, "Third case: the claim arrived one day after the 90-day deadline."),
    ("b2", 79777, 88518, 1.0, "Decision \"기한 위험\" = time-bar risk. Received 2026-10-29, deadline 2026-10-28."),
    ("b2", 88518, 94600, 1.0, "The follow-up memo shows the two dates and what the handler should confirm."),
]

TITLE = [
    ("TimeBar", 72, True),
    ("Tanker Demurrage Claim Evidence Check", 44, True),
    ("", 20, False),
    ("An Upstage Studio workflow: Parse, Classify, Extract, Merge, Instruct", 28, False),
    ("All documents in this video are fictional samples.", 24, False),
]
PROBLEM = [
    ("One missing signature can erase the whole claim", 44, True),
    ("", 20, False),
    ("Under BPVOY4, the claim and all supporting documents must arrive within 90 days.", 28, False),
    ("Three English judgments: USD 535,784 of demurrage claims barred over documents.", 28, False),
    ("Bahri's prospectus: under its contract with Aramco's subsidiary Bolanter,", 28, False),
    ("demurrage is the rate payable by Bolanter when loading or discharge runs late.", 28, False),
]
CLOSING = [
    ("84 of 84 runs matched on the submitted configuration", 44, True),
    ("decision, missing documents, claim number, vessel name", 32, True),
    ("", 20, False),
    ("10 test packages run twice, 21 boundary packages run three times.", 28, False),
    ("Four decisions: clear for payment review, request documents,", 28, False),
    ("time-bar risk, review needed.", 28, False),
    ("The workflow never says \"reject\". That call belongs to a person.", 28, False),
]


def frames_between(folder: str, start: int, end: int) -> list[tuple[int, Path]]:
    found = []
    for path in sorted((DEMO / folder).glob("f_*.png")):
        stamp = int(path.stem.split("_")[1])
        if start <= stamp < end:
            found.append((stamp, path))
    if not found:
        raise SystemExit(f"프레임 없음: {folder} {start}-{end}")
    return found


def with_caption(frame: Image.Image, caption: str) -> Image.Image:
    canvas = Image.new("RGB", (W, H + BAR), (18, 24, 38))
    canvas.paste(frame.convert("RGB").resize((W, H)), (0, 0))
    draw = ImageDraw.Draw(canvas)
    size = 30
    font = ImageFont.truetype(FONT_BOLD, size)
    while draw.textlength(caption, font=font) > W - 80 and size > 18:
        size -= 1
        font = ImageFont.truetype(FONT_BOLD, size)
    width = draw.textlength(caption, font=font)
    draw.text(((W - width) / 2, H + (BAR - size) / 2 - 4), caption, font=font, fill=(255, 255, 255))
    return canvas


def card(lines: list[tuple[str, int, bool]]) -> Image.Image:
    canvas = Image.new("RGB", (W, H + BAR), (18, 24, 38))
    draw = ImageDraw.Draw(canvas)
    total = sum(size + 26 for _, size, _ in lines)
    y = (H + BAR - total) / 2
    for text, size, bold in lines:
        font = ImageFont.truetype(FONT_BOLD if bold else FONT, size)
        width = draw.textlength(text, font=font)
        colour = (255, 255, 255) if bold else (190, 200, 215)
        draw.text(((W - width) / 2, y), text, font=font, fill=colour)
        y += size + 26
    return canvas


def build() -> float:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)
    entries: list[tuple[str, float]] = []

    def add(image: Image.Image, seconds: float) -> None:
        name = f"o_{len(entries):05d}.jpg"
        image.save(OUT_DIR / name, quality=92)
        entries.append((name, seconds))

    add(card(TITLE), CARD_SECONDS)
    add(card(PROBLEM), CARD_SECONDS + 2)
    for folder, start, end, speed, caption in SEGMENTS:
        frames = frames_between(folder, start, end)
        for index, (stamp, path) in enumerate(frames):
            following = frames[index + 1][0] if index + 1 < len(frames) else end
            add(with_caption(Image.open(path), caption), (following - stamp) / 1000 / speed)
    add(card(CLOSING), CARD_SECONDS)

    lines = []
    for name, seconds in entries:
        lines += [f"file '{name}'", f"duration {seconds:.3f}"]
    lines.append(f"file '{entries[-1][0]}'")
    (OUT_DIR / "list.txt").write_text("\n".join(lines), encoding="utf-8")
    return sum(seconds for _, seconds in entries)


def encode() -> None:
    command = [
        "ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt",
        "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-crf", "23", "-movflags", "+faststart",
        str(TARGET),
    ]
    subprocess.run(command, cwd=OUT_DIR, check=True)


if __name__ == "__main__":
    length = build()
    encode()
    print(f"{TARGET.name}: {length:.1f}초, {TARGET.stat().st_size / 1e6:.1f} MB")
