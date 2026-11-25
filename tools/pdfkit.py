"""데이터셋 문서용 PDF 도구.

    uv run python tools/pdfkit.py html2pdf 문서.html 문서.pdf
    uv run python tools/pdfkit.py merge 합친것.pdf a.pdf b.pdf ...
    uv run python tools/pdfkit.py degrade 원본.pdf 스캔본.pdf [--dpi 110] [--blur 0.9] [--tilt 1.2]
"""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tempfile
from pathlib import Path

BROWSERS = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
)
RENDER_TIMEOUT_SECONDS = 60
JPEG_QUALITY = 40


def find_browser() -> str:
    for candidate in BROWSERS:
        if Path(candidate).is_file():
            return candidate
    raise FileNotFoundError("Edge나 Chrome을 찾지 못했습니다. tools/pdfkit.py의 BROWSERS에 경로를 추가하세요.")


def html2pdf(source: Path, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(
            [
                find_browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--user-data-dir={profile}", f"--print-to-pdf={target.resolve()}",
                source.resolve().as_uri(),
            ],
            check=True, capture_output=True, timeout=RENDER_TIMEOUT_SECONDS,
        )
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError(f"PDF가 만들어지지 않았습니다: {target}")
    return target


def merge(target: Path, sources: list[Path]) -> Path:
    from pypdf import PdfWriter

    writer = PdfWriter()
    for source in sources:
        writer.append(str(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as handle:
        writer.write(handle)
    return target


def degrade(source: Path, target: Path, dpi: int, blur: float, tilt: float) -> Path:
    """낮은 해상도로 찍어 기울이고 흐리게 만든다 — 스캔·팩스 문서 흉내."""
    import pymupdf as fitz
    from PIL import Image, ImageFilter

    pages = []
    with fitz.open(str(source)) as document:
        for page in document:
            pixmap = page.get_pixmap(dpi=dpi)
            image = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("L")
            image = image.rotate(tilt, expand=True, fillcolor=255).filter(ImageFilter.GaussianBlur(blur))
            buffer = io.BytesIO()
            image.save(buffer, "JPEG", quality=JPEG_QUALITY)
            pages.append(Image.open(io.BytesIO(buffer.getvalue())))
    target.parent.mkdir(parents=True, exist_ok=True)
    pages[0].save(str(target), "PDF", save_all=True, append_images=pages[1:], resolution=dpi)
    return target


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="데이터셋 PDF 도구")
    commands = parser.add_subparsers(dest="command", required=True)
    convert = commands.add_parser("html2pdf")
    convert.add_argument("source", type=Path)
    convert.add_argument("target", type=Path)
    combine = commands.add_parser("merge")
    combine.add_argument("target", type=Path)
    combine.add_argument("sources", type=Path, nargs="+")
    scan = commands.add_parser("degrade")
    scan.add_argument("source", type=Path)
    scan.add_argument("target", type=Path)
    scan.add_argument("--dpi", type=int, default=110)
    scan.add_argument("--blur", type=float, default=0.9)
    scan.add_argument("--tilt", type=float, default=1.2)
    args = parser.parse_args()
    if args.command == "html2pdf":
        result = html2pdf(args.source, args.target)
    elif args.command == "merge":
        result = merge(args.target, args.sources)
    else:
        result = degrade(args.source, args.target, args.dpi, args.blur, args.tilt)
    print(f"만들었습니다: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
