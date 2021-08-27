#!/usr/bin/env python3

import sys

import click
import gpxpy.gpx

from geographiclib.geodesic import Geodesic


geod = Geodesic.WGS84


@click.command()
@click.argument('gpx_file', type=click.File('r'), default=sys.stdin)
def main(gpx_file):
    gpx = gpxpy.parse(gpx_file)

    total_meters = 0
    for track in gpx.tracks:
        for segment in track.segments:
            for n, point in enumerate(segment.points[1:], 1):
                # get distance between the current point and previous point
                previous_point = segment.points[n - 1]
                g = geod.Inverse(
                    previous_point.latitude, previous_point.longitude,
                    point.latitude, point.longitude,
                    Geodesic.DISTANCE
                )
                distance = g['s12']
                total_meters += distance
                print(total_meters, point.elevation)


if __name__ == '__main__':
    main()
