#!/usr/bin/env python3

import sys
import svgwrite

if len(sys.argv) > 1:
    UNIT = sys.argv[1]
else:
    UNIT = 'mi'

distances = []
for line in sys.stdin:
    (d, e) = line.split(' ', 2)
    distances.append((float(d), float(e)))

MILES_PER_METER = 0.0006213712
METERS_PER_MILE = 1609.344

STEP_FOR = {
    'km': 1000,
    'mi': METERS_PER_MILE,
    }

VERTICAL_STRETCH = 5

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
step = STEP_FOR[UNIT]
i = step
while i < total_meters:
    line = drawing.line(start=(i, mn), end=(i, mx), stroke='black', stroke_width='.5%', stroke_opacity='0.5')
    line.set_desc(title=f'{int(i/step)}{UNIT}')
    g.add(line)
    i += step

# elevation line
polyline = drawing.polyline(points, stroke='black', stroke_width='.5%', fill='none')

g.add(polyline)
drawing.add(g)

print(drawing.tostring())
