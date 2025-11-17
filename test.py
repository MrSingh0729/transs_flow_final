#!/usr/bin/env python3
"""
generate_assets.py

Usage:
    python generate_assets.py path/to/source_logo.png

Generates:
- PWA icons (normal + maskable)
- PWA screenshots in required sizes
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Icon sizes
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Screenshot sizes
SCREENSHOTS = {
    "mobile-home.png": (750, 1334),
    "desktop-home.png": (1920, 1080)
}

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def make_square_icon(src_img: Image.Image, size: int, padding: int = 0):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    src_w, src_h = src_img.size

    avail = size - 2 * padding
    scale = min(avail / src_w, avail / src_h)
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)

    resized = src_img.resize((new_w, new_h), Image.LANCZOS)
    canvas.paste(resized, ((size - new_w)//2, (size - new_h)//2), resized)
    return canvas

def generate_screenshot(src_img: Image.Image, size: tuple, out_path: str):
    w, h = size

    # create white background
    canvas = Image.new("RGBA", (w, h), (255, 255, 255, 255))

    # Resize logo to fit nicely (40% of width)
    target_width = int(w * 0.4)
    scale = target_width / src_img.width
    new_h = int(src_img.height * scale)
    resized = src_img.resize((target_width, new_h), Image.LANCZOS)

    # paste centered
    canvas.paste(resized, ((w - target_width) // 2, (h - new_h) // 2), resized)

    canvas.save(out_path, optimize=True)
    print("Saved screenshot:", out_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_assets.py path/to/logo.png")
        sys.exit(1)

    logo_path = sys.argv[1]
    if not os.path.exists(logo_path):
        print("Error: source image not found")
        sys.exit(1)

    src = Image.open(logo_path).convert("RGBA")

    out_icon_dir = os.path.join("output", "icons")
    out_ss_dir = os.path.join("output", "screenshots")

    ensure_dir(out_icon_dir)
    ensure_dir(out_ss_dir)

    print("\nGenerating icons...")
    for s in ICON_SIZES:
        icon = make_square_icon(src, s, padding=0)
        icon.save(os.path.join(out_icon_dir, f"icon-{s}x{s}.png"))
        print("Saved icon:", f"icon-{s}x{s}.png")

    print("\nGenerating maskable icons...")
    for s in ICON_SIZES:
        padding = int(s * 0.10)  # 10% padding
        mask_icon = make_square_icon(src, s, padding)
        mask_icon.save(os.path.join(out_icon_dir, f"icon-{s}x{s}-maskable.png"))
        print("Saved maskable:", f"icon-{s}x{s}-maskable.png")

    print("\nGenerating PWA screenshots...")
    for name, size in SCREENSHOTS.items():
        out_path = os.path.join(out_ss_dir, name)
        generate_screenshot(src, size, out_path)

    print("\nDone! Assets generated in /output/")

if __name__ == "__main__":
    main()
