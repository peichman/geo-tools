#!/usr/bin/env python3

import sys

import click
import svgwrite


MILES_PER_METER = 0.0006213712
METERS_PER_MILE = 1609.344

STEP_FOR = {
    'km': 1000,
    'mi': METERS_PER_MILE,
    }

VERTICAL_STRETCH = 5

@click.command()
@click.option('--output-unit', '-o', type=click.Choice(['km', 'mi']), default='mi')
@click.argument('distances_file', type=click.File('r'), default=sys.stdin)
def main(distances_file, output_unit):
    distances = []
    for line in distances_file:
        (d, e) = line.split(' ', 2)
        distances.append((float(d), float(e)))

    min_elev = min([e for d, e in distances])
    max_elev = max([e for d, e in distances])
    total_meters = max([d for d, e in distances])

    total_miles = total_meters * MILES_PER_METER

    mx = max_elev * VERTICAL_STRETCH
    mn = min_elev * VERTICAL_STRETCH
    points = [ (d, e * VERTICAL_STRETCH) for d, e in distances ]
    height = mx - mn
    width = total_meters - 1
    offset = height + mn * 2

    drawing = svgwrite.Drawing()
    drawing.viewbox(0, mn, width, height)
    g = drawing.g(transform=f'matrix(1 0 0 -1 0 {offset})')

    # interval marker
    step = STEP_FOR[output_unit]
    i = step
    while i < total_meters:
        line = drawing.line(start=(i, mn), end=(i, mx), stroke='black', stroke_width='.5%', stroke_opacity='0.5')
        line.set_desc(title=f'{int(i/step)}{output_unit}')
        g.add(line)
        i += step

    """
    FEET_PER_METER = 3.28084
    METERS_PER_FOOT = 0.3048
    rise = 500 * METERS_PER_FOOT * VERTICAL_STRETCH
    j = mn + rise
    while j < mx:
        line = drawing.line(start=(0, j), end=(width, j), stroke='black', stroke_width='.5%', stroke_opacity='0.5')
        g.add(line)
        j += rise
    """

    # elevation line
    polyline = drawing.polyline(points, stroke='black', stroke_width='.5%', fill='none')

    g.add(polyline)
    drawing.add(g)

    print(drawing.tostring())


if __name__ == '__main__':
    main()
