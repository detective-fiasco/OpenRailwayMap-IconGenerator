#!/usr/bin/env python3

import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import svgwrite


def create_svg(text, output_path, font_path="arial-bold.ttf", *, background="white", strike=None):
    FIXED_WIDTH = 11

    # Base height for a single char, scaled by character count
    # Ensures it fits at least 2 characters even if text is shorter
    char_count = len(text)
    virtual_count = (3 + char_count) / 2
    DYNAMIC_HEIGHT = (virtual_count * 12)

    SVG_SIZE = (FIXED_WIDTH, DYNAMIC_HEIGHT)
    BORDER_SIZE = 0.8
    FONT_SIZE = 13

    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    units_per_em = font["head"].unitsPerEm
    scale = FONT_SIZE / units_per_em

    dwg = svgwrite.Drawing(output_path, size=SVG_SIZE)

    # Draw Background
    dwg.add(dwg.rect(
        insert=(0, 0),
        size=SVG_SIZE,
        fill="black"
    ))
    dwg.add(dwg.rect(
        insert=(BORDER_SIZE, BORDER_SIZE),
        size=(SVG_SIZE[0] - 2 * BORDER_SIZE, SVG_SIZE[1] - 2 * BORDER_SIZE),
        fill=background
    ))

    glyphs_to_render = []
    total_ink_height = 0
    line_spacing = 200 * scale  # Adjust vertical gap between characters

    for char in text:
        glyph_name = cmap.get(ord(char), ".notdef")
        glyph = glyph_set[glyph_name]

        bp = BoundsPen(glyph_set)
        glyph.draw(bp)

        if bp.bounds:
            x_min, y_min, x_max, y_max = bp.bounds
            tight_width = (x_max - x_min) * scale
            tight_height = (y_max - y_min) * scale
        else:
            x_min = 0
            y_max = 0
            tight_width = (font["hmtx"][glyph_name][0] * 0.5) * scale
            tight_height = FONT_SIZE * 0.7

        if char == "1":
            x_min += 100

        glyphs_to_render.append({
            'glyph': glyph,
            'x_min': x_min,
            'y_max': y_max,
            'tight_width': tight_width,
            'tight_height': tight_height
        })
        total_ink_height += tight_height

    # Total height of all characters plus the gaps between them
    total_content_height = total_ink_height + (line_spacing * (len(text) - 1))

    # --- Step 2: Vertical Rendering ---
    # Start Y position to center the block of text vertically in the dynamic height
    current_y = (SVG_SIZE[1] - total_content_height) / 2

    group = dwg.g(fill="black")

    for item in glyphs_to_render:
        pen = SVGPathPen(glyph_set)

        # Horizontal centering: Center each glyph relative to FIXED_WIDTH
        char_x = (SVG_SIZE[0] - item['tight_width']) / 2

        # Vertical placement:
        # We use item['y_max'] * scale because SVG coordinates increase downwards,
        # but font coordinates increase upwards.
        transform = TransformPen(pen, (
            scale, 0,
            0, -scale,
            char_x - (item['x_min'] * scale),
            current_y + (item['y_max'] * scale)
        ))

        item['glyph'].draw(transform)
        group.add(dwg.path(d=pen.getCommands()))

        # Move current_y down for the next character
        current_y += item['tight_height'] + line_spacing

    dwg.add(group)

    if strike:
        clip = dwg.defs.add(dwg.clipPath(id="inner_clip"))
        clip.add(dwg.rect(
            insert=(BORDER_SIZE, BORDER_SIZE),
            size=(SVG_SIZE[0] - 2 * BORDER_SIZE, SVG_SIZE[1] - 2 * BORDER_SIZE)
        ))

        dwg.add(dwg.line(
            start=(SVG_SIZE[0] - BORDER_SIZE, BORDER_SIZE),
            end=(BORDER_SIZE, SVG_SIZE[1] - BORDER_SIZE),
            stroke=strike,
            stroke_width=BORDER_SIZE * 2,
            clip_path="url(#inner_clip)"
        ))

    dwg.save()


YELLOW = "#f4da6f"
WHITE = "white"
RED = "#d9283b"

if __name__ == "__main__":

    os.makedirs("out/predvestnik/NS", exist_ok=True)
    for i in range(10, 161, 10):
        create_svg(str(i // 10), f"out/predvestnik/NS/{{{i}}}.svg", background=YELLOW)
    create_svg("?", "out/predvestnik/NS/unknown.svg", background=YELLOW)
    create_svg("NS", "out/predvestnik/NS/end.svg", background=YELLOW, strike=RED)

    os.makedirs("out/rychlostnik/NS", exist_ok=True)
    for i in range(10, 161, 5):
        create_svg(str(i), f"out/rychlostnik/NS/{{{i}}}.svg", background=WHITE)
    create_svg("?", "out/rychlostnik/NS/unknown.svg", background=WHITE)
    create_svg("NS", "out/rychlostnik/NS/end.svg", background=WHITE, strike=RED)