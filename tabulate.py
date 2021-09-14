#!/usr/bin/env python3

import sys
from datetime import timedelta
from importlib import import_module

import click
import gpxpy.gpx
from geographiclib.geodesic import Geodesic


class DelimitedList(click.ParamType):
    def __init__(self, delimiter=','):
        self.delimiter = delimiter

    def convert(self, value, param, ctx):
        if isinstance(value, list):
            return value

        return value.split(self.delimiter)

@click.command()
@click.argument('gpx_file', type=click.File('r'), default=sys.stdin)
@click.option('--output-fields', '-o', type=DelimitedList(), default=['distance', 'elevation'])
def main(gpx_file, output_fields):
    fields = [get_function(name) for name in output_fields]

    gpx = gpxpy.parse(gpx_file)

    for track in gpx.tracks:
        for segment in track.segments:
            for n, point in enumerate(segment.points[1:], 1):
                print(*(fn(n, point, segment) for fn in fields))


# track a total (or other static value) as a function attribute
# this is preserved across calls
def track(attr_name, init=0):
    def decorated(func):
        if callable(init):
            setattr(func, attr_name, init())
        else:
            setattr(func, attr_name, init)
        return func
    return decorated


def get_function(name):
    try:
        return getattr(import_module('__main__'), name)
    except AttributeError as e:
        raise click.BadParameter(f'No output function named {name}', param_hint='--output-fields') from e


@track('total')
def distance(n, point, segment):
    # get distance between the current point and previous point
    previous_point = segment.points[n - 1]
    g = Geodesic.WGS84.Inverse(
        previous_point.latitude, previous_point.longitude,
        point.latitude, point.longitude,
        Geodesic.DISTANCE
    )
    distance.total += g['s12']
    return distance.total


def elevation(n, point, segment):
    return point.elevation


def clock_time(n, point, segment):
    return point.time.isoformat()


@track('total', init=timedelta)
def elapsed_time(n, point, segment):
    previous_point = segment.points[n - 1]
    elapsed_time.total += (point.time - previous_point.time)
    return elapsed_time.total


AVAILABLE_FUNCTIONS = [distance, elevation, clock_time, elapsed_time]


if __name__ == '__main__':
    main()
