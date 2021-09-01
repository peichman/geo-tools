#!/usr/bin/env python3

import sys

import click
from lxml import etree
from lxml.etree import DocumentInvalid

ns = {
    'gpx': "http://www.topografix.com/GPX/1/1",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}

@click.command()
@click.argument('xml_file', type=click.File('r'))
def main(xml_file):
    xml_doc = etree.parse(xml_file)
    locations = xml_doc.xpath('//@xsi:schemaLocation', namespaces=ns)[0]

    xsd_uri = locations.split(' ')[1]
    xsd = etree.XMLSchema(etree.parse(xsd_uri))

    try:
        xsd.assertValid(xml_doc)
    except DocumentInvalid as e:
        print(f'INVALID: {e}')
        sys.exit(1)

    print('VALID')


if __name__ == '__main__':
    main()
