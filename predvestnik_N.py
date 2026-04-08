#!/usr/bin/env python3

import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import svgwrite


def create_svg(text, output_path, font_path="arial-bold.ttf"):

    SVG_SIZE = 21, 17
    BORDER_SIZE = 0.8
    FONT_SIZE = 13
    if len(text) > 1:
        FONT_SIZE = 11

    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = FONT_SIZE / font["head"].unitsPerEm

    dwg = svgwrite.Drawing(output_path, size=SVG_SIZE)

    # --- Draw Triangle Background ---
    p1 = (BORDER_SIZE/2, BORDER_SIZE/2)
    p2 = (SVG_SIZE[0] - BORDER_SIZE/2, BORDER_SIZE/2)
    p3 = (SVG_SIZE[0] / 2, SVG_SIZE[1] - BORDER_SIZE/2)

    # Creating the path data string:
    # M = Move to, L = Line to, Z = Close Path
    path_data = f"M {p1[0]},{p1[1]} L {p2[0]},{p2[1]} L {p3[0]},{p3[1]} Z"

    dwg.add(dwg.path(
        d=path_data,
        fill="#f4da6f",
        stroke="black",
        stroke_width=BORDER_SIZE,
        stroke_linejoin="round"
    ))

    glyphs_to_render = []
    total_ink_width = 0

    for char in text:
        glyph_name = cmap.get(ord(char), ".notdef")
        glyph = glyph_set[glyph_name]

        # Use BoundsPen to find the exact "ink" coordinates
        bp = BoundsPen(glyph_set)
        glyph.draw(bp)

        if bp.bounds:
            x_min, y_min, x_max, y_max = bp.bounds
            tight_width = x_max - x_min
        else:
            # Fallback for invisible characters (like space)
            x_min = 0
            tight_width = font["hmtx"][glyph_name][0] * 0.5

        glyphs_to_render.append({
            'glyph': glyph,
            'x_min': x_min,
            'tight_width': tight_width
        })
        total_ink_width += tight_width

    # Calculate total layout width
    LETTER_SPACING = 90

    spacing_total = (len(text) - 1) * LETTER_SPACING
    total_width_scaled = (total_ink_width + spacing_total) * scale

    # Horizontal center
    current_x = (SVG_SIZE[0] - total_width_scaled) / 2

    if text == "1":
        current_x -= 0.7

    if text == "7":
        current_x += 0.5

    if text == "11":
        current_x -= 0.4

    if text == "12":
        current_x -= 0.4

    if len(text) > 1:
        current_x -= 0.4

    # Vertical center: Using 0.35 * ascent is a good baseline for most fonts
    ascent = font["hhea"].ascent * scale
    y_baseline = (SVG_SIZE[1] * 1/3) + (ascent * 0.38)

    if len(text) == 1:
        y_baseline += 0.6

    group = dwg.g(fill="black")

    for item in glyphs_to_render:
        pen = SVGPathPen(glyph_set)

        # KEY: We subtract x_min to eliminate the "side bearing" (empty space)
        # This makes the "1" behave like a narrow character rather than a wide one.
        transform = TransformPen(pen, (
            scale, 0,
            0, -scale,
            current_x - (item['x_min'] * scale),
            y_baseline
        ))

        item['glyph'].draw(transform)
        group.add(dwg.path(d=pen.getCommands()))

        # Advance current_x by only the ink width + the small spacing
        current_x += (item['tight_width'] + LETTER_SPACING) * scale

    dwg.add(group)
    dwg.save()


if __name__ == "__main__":
    os.makedirs("out/predvestnik/N", exist_ok=True)
    for i in range(10, 161, 10):
        create_svg(str(i // 10), f"out/predvestnik/N/{{{i}}}.svg")
    create_svg("?", "out/predvestnik/N/unknown.svg")