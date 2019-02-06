#!/usr/bin/env python3

from geographiclib.geodesic import Geodesic
import gpxpy.gpx
import sys

geod = Geodesic.WGS84

with open(sys.argv[1], 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

distances = []
last_point = None
total_meters = 0
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            if last_point is not None:
                # get distance between the current point and previous point
                g = geod.Inverse(
                        last_point.latitude, last_point.longitude,
                        point.latitude, point.longitude,
                        Geodesic.DISTANCE
                        )
                d = g['s12']
                total_meters += d
                distances.append((total_meters, point.elevation))
            last_point = point

for d, e in distances:
    print(d, e)
