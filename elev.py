#!/usr/bin/env python3

import click
import gpxpy
import gpxpy.gpx
import os
import rasterio
import requests
import sys

from collections import namedtuple
from math import floor, ceil
from zipfile import ZipFile

DEM_ROOT = os.path.join(os.environ['HOME'], 'gps/dem')

GridFile = namedtuple('GridFile', 'dataset elevation_for')
data_from = {}

def get_gridfile(lat, lon):
    n = ceil(lat) if lat > 0 else abs(floor(lat))
    w = ceil(lon) if lon > 0 else abs(floor(lon))

    gridname = f'USGS_NED_13_n{n:02d}w{w:03d}_IMG'

    def extract_zip(zip_file):
        target_dir = os.path.join(DEM_ROOT, gridname)
        os.makedirs(target_dir)
        print(f'Extracting {zip_file} contents to {target_dir}', file=sys.stderr)
        with ZipFile(zip_file) as zip_archive:
            zip_archive.extractall(path=target_dir)

    img_file = os.path.join(DEM_ROOT, gridname, f'{gridname}.img')
    if os.path.isfile(img_file):
        return img_file

    # .img file not found, check for .zip and extract
    zip_file = os.path.join(DEM_ROOT, f'{gridname}.zip')
    if os.path.isfile(zip_file):
        extract_zip(zip_file)
        return img_file

    # download and unzip on demand from the National Map
    # FTP URL: ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Elevation/13/IMG/
    url = f'https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/IMG/{gridname}.zip'
    if requests.head(url).status_code == 200:
        print(f'Downloading {zip_file} from {url}', file=sys.stderr)
        with requests.get(url, stream=True) as r:
            with open(zip_file, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
        extract_zip(zip_file)
        return img_file

    raise Exception(f'Missing files for {gridname}')

def get_elevation(lat, lon):
    gridfile = get_gridfile(lat, lon)
    if gridfile not in data_from:
        # load and cache the dataset and elevation data band
        ds = rasterio.open(gridfile)
        data_from[gridfile] = GridFile(dataset=ds, elevation_for=ds.read(1))

    grid = data_from[gridfile]
    return grid.elevation_for[grid.dataset.index(lon, lat)]

@click.command()
@click.argument('gpx_file', type=click.File('r'), default=sys.stdin)
def main(gpx_file):
    gpx = gpxpy.parse(gpx_file)

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.elevation is None:
                    # use rasterio to get the elevation here
                    point.elevation = get_elevation(point.latitude, point.longitude)

    try:
        #TODO: how to stop gpxpy from truncating trailing 0s in decimal places?
        print(gpx.to_xml())
    except BrokenPipeError:
        # pipe closed STDOUT, we don't care
        pass


if __name__ == '__main__':
    main()
