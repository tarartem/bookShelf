import os
import hashlib
import logging
import textwrap
from typing import Optional, Tuple
import zipfile

from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)


# ── Cover placeholder generator ───────────────────────────────────────────────

def _generate_placeholder_cover(title: str, author: str, epub_path: str) -> str:
    """Generate a styled gradient cover image using Pillow and return its path."""
    os.makedirs("uploads/covers", exist_ok=True)

    name_hash = hashlib.md5(epub_path.encode()).hexdigest()[:10]
    cover_filename = f"{name_hash}_cover.png"
    cover_filepath = f"uploads/covers/{cover_filename}"

    W, H = 400, 580

    # Pick a deterministic gradient color based on title hash
    hue_seed = int(hashlib.md5(title.encode()).hexdigest()[:4], 16) % 360
    colors = _hue_to_gradient(hue_seed)

    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(H):
        t = y / H
        r = int(colors[0][0] * (1 - t) + colors[1][0] * t)
        g = int(colors[0][1] * (1 - t) + colors[1][1] * t)
        b = int(colors[0][2] * (1 - t) + colors[1][2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Dark overlay strip at bottom
    overlay_h = 180
    for y in range(H - overlay_h, H):
        alpha = int(200 * (y - (H - overlay_h)) / overlay_h)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0))

    # Try to load a font; fall back to default
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        font_author = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except Exception:
        font_title = ImageFont.load_default()
        font_author = font_title

    # Wrap title
    title_lines = textwrap.wrap(title, width=18)
    y_text = H - overlay_h + 20
    for line in title_lines[:3]:
        draw.text((20, y_text), line, font=font_title, fill=(255, 255, 255))
        y_text += 38

    # Author
    y_text += 4
    draw.text((20, y_text), author or "", font=font_author, fill=(200, 200, 200))

    img.save(cover_filepath, "PNG")
    logger.info(f"Generated placeholder cover: {cover_filepath}")
    return cover_filepath


def _hue_to_gradient(hue: int):
    """Return two dark-ish RGB tuples for a gradient based on a hue (0-360)."""
    import colorsys
    h = hue / 360.0
    r1, g1, b1 = colorsys.hsv_to_rgb(h, 0.6, 0.5)
    r2, g2, b2 = colorsys.hsv_to_rgb((h + 0.08) % 1.0, 0.8, 0.25)
    return (
        (int(r1 * 255), int(g1 * 255), int(b1 * 255)),
        (int(r2 * 255), int(g2 * 255), int(b2 * 255)),
    )


# ── EPUB metadata extractor ───────────────────────────────────────────────────

def _try_extract_embedded_cover(epub_path: str) -> Optional[bytes]:
    """
    Attempt to extract embedded cover image bytes directly from the EPUB zip,
    trying multiple common patterns.
    """
    try:
        with zipfile.ZipFile(epub_path, "r") as zf:
            names = zf.namelist()
            # Pattern 1: file named "cover.*"
            for n in names:
                base = n.split("/")[-1].lower()
                if base.startswith("cover") and any(base.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")):
                    return zf.read(n)
            # Pattern 2: any image inside Images/ or images/ dir
            for n in names:
                lower = n.lower()
                if ("images/" in lower or "image/" in lower) and any(lower.endswith(ext) for ext in (".jpg", ".jpeg", ".png")):
                    return zf.read(n)
    except Exception as e:
        logger.warning(f"ZIP cover extraction failed for {epub_path}: {e}")
    return None


def extract_epub_metadata(epub_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract (title, author, cover_filepath) from an EPUB.
    Falls back to a generated placeholder if no cover image is found.
    """
    title = None
    author = None
    cover_filepath = None

    try:
        import warnings
        import ebooklib
        from ebooklib import epub as ebooklib_epub

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            book = ebooklib_epub.read_epub(epub_path, options={"ignore_ncx": True})

        dc_title = book.get_metadata("DC", "title")
        if dc_title:
            title = dc_title[0][0]

        dc_creator = book.get_metadata("DC", "creator")
        if dc_creator:
            author = dc_creator[0][0]

        # Try ebooklib image items first
        cover_data = None
        cover_ext = "jpg"
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE:
                name = (item.get_name() or "").lower()
                item_id = (item.get_id() or "").lower()
                if "cover" in name or "cover" in item_id:
                    cover_data = item.get_content()
                    cover_ext = "png" if name.endswith(".png") else "jpg"
                    break

        # Fallback: scan ZIP directly
        if not cover_data:
            cover_data = _try_extract_embedded_cover(epub_path)

        if cover_data:
            os.makedirs("uploads/covers", exist_ok=True)
            name_hash = hashlib.md5(epub_path.encode()).hexdigest()[:10]
            cover_filename = f"{name_hash}_cover.{cover_ext}"
            cover_filepath = f"uploads/covers/{cover_filename}"
            try:
                img = Image.open(io.BytesIO(cover_data))
                img.save(cover_filepath)
            except Exception:
                with open(cover_filepath, "wb") as f:
                    f.write(cover_data)

    except Exception as e:
        logger.error(f"Failed to read epub metadata from {epub_path}: {e}")

    # Always ensure a cover exists — generate placeholder if needed
    if not cover_filepath or not os.path.exists(cover_filepath):
        cover_filepath = _generate_placeholder_cover(
            title or os.path.splitext(os.path.basename(epub_path))[0],
            author or "Unknown",
            epub_path
        )

    return title, author, cover_filepath
