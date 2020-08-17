import csv
import argparse
from math import degrees, atan2, sqrt
import re
from collections import defaultdict
import pprint
from eacsd import ViewDirections
import sys


def calculate_bearing(x, y, center_x, center_y):
    angle = degrees(atan2(y - center_y, x - center_x))
    bearing2 = (90 - angle) % 360
    return bearing2


def resolve_photo_points(infile, outfile, callback=None):

    with open(infile, newline='') as infile_open_1:
        reader = csv.reader(infile_open_1)
        header = next(reader)
        ppts = defaultdict(lambda: defaultdict(list))
        for row in reader:
            code, no, e, n, _, direction = row[:6]
            pp = re.search('PH(\d?)(\d{3})', code)
            pp_group = pp.group(1)
            xs = pp.group(2)
            if direction not in (ViewDirections.US, ViewDirections.DS, ViewDirections.VA):
                callback.write('Photo point for {} missing one of: \'{}\', \'{}\', \'{}\''.format(code, ViewDirections.US, ViewDirections.DS, ViewDirections.VA))
            ppts[xs][pp_group].append([no, float(e), float(n), direction])

    final_ppt_pairs = defaultdict(dict)


    out_data = ['Code', 'Number', 'Easting', 'Northing', 'Height', 'Remarks', 'BRG']
    with open(outfile, 'w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(out_data)
        for xs, group in ppts.items():
            for id_, pts in group.items():
                if len(pts) == 2:
                    pts.sort()
                    pt0, pt1 = pts
                    no, pt0e, pt0n, direction = pt0
                    _, pt1e, pt1n, _ = pt1
                    brg = calculate_bearing(pt1e, pt1n, pt0e, pt0n)
                    writer.writerow(['PH{}{}'.format(id_, xs), no, pt0e, pt0n, None, direction, brg])
                else:
                    callback.write('Photo points for {xs}{id_} not grouped in numbered pairs'.format(xs=xs,id_=id_))
                    for pt in pts:
                        no, pte, ptn, direction = pt
                        writer.writerow(['PH{}{}'.format(id_, xs), no, pte, ptn, None, direction, None])


def cli_main():
    parser = argparse.ArgumentParser('calcphotobearings')
    parser.add_argument('inpath', help='Path to photo points csv file.')
    parser.add_argument('outpath', help='Output file')

    args = parser.parse_args()
    resolve_photo_points(args.inpath, args.outpath, sys.stdout)