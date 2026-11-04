#!/usr/bin/env python3
"""Generate CyberRange Academy PWA icons: a shield with a terminal prompt.

Stdlib only. Writes icon-192.png and icon-512.png in the repo root.
"""
import struct
import zlib
from pathlib import Path

BG = (11, 14, 20, 255)          # #0b0e14
RIM = (31, 111, 235, 255)       # #1f6feb
SHIELD = (74, 163, 255, 255)    # #4aa3ff
GLYPH = (7, 16, 25, 255)        # #071019

ROOT = Path(__file__).resolve().parent.parent


def chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(path, width, height, rgba):
    raw = b"".join(
        b"\x00" + rgba[y * width * 4 : (y + 1) * width * 4] for y in range(height)
    )
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    Path(path).write_bytes(png)


def point_in_poly(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            xinter = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xinter:
                inside = not inside
        j = i
    return inside


def dist_to_seg(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    length_sq = vx * vx + vy * vy
    if length_sq == 0:
        dx, dy = px - ax, py - ay
        return (dx * dx + dy * dy) ** 0.5
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / length_sq))
    qx, qy = ax + t * vx, ay + t * vy
    dx, dy = px - qx, py - qy
    return (dx * dx + dy * dy) ** 0.5


def shield_poly(size, grow=1.0):
    cx = size / 2
    cy = size * 0.48
    pts = [
        (size * 0.24, size * 0.22),
        (size * 0.32, size * 0.16),
        (size * 0.50, size * 0.175),
        (size * 0.68, size * 0.16),
        (size * 0.76, size * 0.22),
        (size * 0.74, size * 0.50),
        (size * 0.50, size * 0.84),
        (size * 0.26, size * 0.50),
    ]
    if grow == 1.0:
        return pts
    return [((x - cx) * grow + cx, (y - cy) * grow + cy) for x, y in pts]


def prompt_segments(size):
    """A '>_' prompt sitting in the body of the shield."""
    cy = size * 0.42
    return [
        (size * 0.38, cy - size * 0.07, size * 0.50, cy),
        (size * 0.50, cy, size * 0.38, cy + size * 0.07),
        (size * 0.54, cy + size * 0.07, size * 0.64, cy + size * 0.07),
    ]


def sample(x, y, size):
    if point_in_poly(x, y, shield_poly(size, 1.045)):
        color = RIM
    else:
        color = BG
    if point_in_poly(x, y, shield_poly(size, 1.0)):
        color = SHIELD
    thickness = size * 0.028
    for ax, ay, bx, by in prompt_segments(size):
        if dist_to_seg(x, y, ax, ay, bx, by) <= thickness / 2:
            color = GLYPH
            break
    return color


def render(size, samples=4):
    buf = bytearray(size * size * 4)
    for y in range(size):
        for x in range(size):
            acc = [0, 0, 0, 0]
            for sy in range(samples):
                for sx in range(samples):
                    px = x + (sx + 0.5) / samples
                    py = y + (sy + 0.5) / samples
                    color = sample(px, py, size)
                    for i in range(4):
                        acc[i] += color[i]
            n = samples * samples
            offset = (y * size + x) * 4
            for i in range(4):
                buf[offset + i] = acc[i] // n
    return buf


def main():
    for size in (192, 512):
        print(f"rendering {size}", flush=True)
        rgba = render(size)
        path = ROOT / f"icon-{size}.png"
        write_png(path, size, size, rgba)
        print(f"wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
