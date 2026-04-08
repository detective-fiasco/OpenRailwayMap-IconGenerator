#!/usr/bin/env python3

import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import svgwrite


def create_svg(text, output_path, font_path="arial-bold.ttf", *, pruhy=False):

    SVG_SIZE = 21, 14
    BORDER_SIZE = 0.8
    BAR_WIDTH = 3 if pruhy else BORDER_SIZE
    FONT_SIZE = 13

    if pruhy and len(text) > 2:
        FONT_SIZE = 10

    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = FONT_SIZE / font["head"].unitsPerEm

    dwg = svgwrite.Drawing(output_path, size=SVG_SIZE)

    # Draw Background
    dwg.add(dwg.rect(
        insert=(0, 0),
        size=SVG_SIZE,
        fill="black"
    ))
    dwg.add(dwg.rect(
        insert=(BAR_WIDTH, BORDER_SIZE),
        size=(SVG_SIZE[0]-2*BAR_WIDTH, SVG_SIZE[1]-2*BORDER_SIZE),
        fill="white"
    ))

    if pruhy:
        for x in [BAR_WIDTH / 2, SVG_SIZE[0] - BAR_WIDTH / 2]:
            for y in [SVG_SIZE[1] / 4 * i for i in range(1, 4)]:
                dwg.add(dwg.circle(
                    center=(x, y),
                    r=BAR_WIDTH / 3,
                    fill='white'
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
    if text in [ "10", "15" ]:
        LETTER_SPACING = 300

    spacing_total = (len(text) - 1) * LETTER_SPACING
    total_width_scaled = (total_ink_width + spacing_total) * scale

    # Horizontal center
    current_x = (SVG_SIZE[0] - total_width_scaled) / 2

    # Vertical center: Using 0.35 * ascent is a good baseline for most fonts
    ascent = font["hhea"].ascent * scale
    y_baseline = (SVG_SIZE[1] / 2) + (ascent * 0.38)

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


# --- Execution ---
if __name__ == "__main__":
    os.makedirs("out/rychlostnik/N", exist_ok=True)
    for i in range(10, 161, 5):
        create_svg(str(i), f"out/rychlostnik/N/{{{i}}}.svg")
    create_svg("?", "out/rychlostnik/N/unknown.svg")

    os.makedirs("out/rychlostnik/N_s_pruhy", exist_ok=True)
    for i in range(10, 161, 5):
        create_svg(str(i), f"out/rychlostnik/N_s_pruhy/{{{i}}}.svg", pruhy=True)
    create_svg("?", "out/rychlostnik/N_s_pruhy/unknown.svg", pruhy=True)