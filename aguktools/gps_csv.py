""" This program processes points exported from Trimble Business Center
specifically for AGUK EACSD formats. The export format from TBC is messy and
needs editing to get all dimensions into the right columns.
"""
import csv
import datetime
import os
import re
import argparse
import sys
from textwrap import dedent
import dateutil.parser

import aguktools.common


HELP = {'short': 'Reformats TBC CSV attributes into regular columns.',
        'full': dedent('''
            Searches rows in `infile` for attributes
            exported by Trimble Business Center (stored as `KEY=VALUE`) and
            moves them into columns in `--outfile`. This can then be imported
            into N4ce as a CSV file with those columns defined. If `inspect` is
            passed, the program returns the columns found in `infile`. Since
            they have no guaranteed order, it is up to the user to provide the
            column order using `--columns` which can be a path to a text file
            containing space-separated column names or a sequence of
            space-separated column names. If this option is not passed, all
            columns will be written in an unpredictable order. For the rare
            instances where junk rows which contain no eastings and northings,
            `--retain` can be passed to keep such rows.''')}


DEFAULT_COLS = ['Code', 'Number', 'Easting', 'Northing', 'Height']


class GPSCSVObs(object):
    def __init__(self, obs, eacsd_date=False):
        self.code, self.num, self.e, self.n, self.h = obs[:5]

        self.attr_dict = {}
        for attr in obs[5:]:

            if attr:
                try:
                    k, v = attr.split('=')
                except ValueError:
                    k, v = 'Remark', attr

                if k.lower() == 'date':
                    v = aguktools.common.parse_date(v, eacsd_date=eacsd_date)
                elif k.lower() == 'time':
                    time = dateutil.parser.parse(v, fuzzy=True)
                    v = datetime.datetime.strftime(time, '%H:%M:%S')
                elif not k:
                    continue
                v = v.replace('NaN', '')
                if v:
                    self.attr_dict[k] = v


    def write(self, columns):
        return ([self.code, self.num, self.e, self.n, self.h] +
                [self.attr_dict.get(cell, '') for cell in columns])


def reformat_csv(inpath, outpath, columns=None, inspect=False, keep_empty=False,
    callback=None, date_reformat=False):
    with open(inpath, 'r') as infile_obj:
        reader = csv.reader(infile_obj)
        rows = []
        seen_cols = set()
        for row in reader:
            if not keep_empty and row[2:4] == ['', '']:
                continue
            out_row = GPSCSVObs(row, eacsd_date=date_reformat)
            seen_cols = seen_cols.union(out_row.attr_dict.keys())
            rows.append(out_row)

        seen_cols = sorted(list(seen_cols))

        if inspect:
            if callback:
                callback.write('Columns found:\n' + ' '.join(seen_cols))
        else:
            with open(outpath, 'w') as outfile_obj:
                writer = csv.writer(outfile_obj, lineterminator='\n')
                writer.writerow(DEFAULT_COLS + (columns or seen_cols))
                for row in rows:
                    writer.writerow(row.write(columns or seen_cols))
            if callback:
                callback.write('TBC file reformat complete')
    return ' '.join(seen_cols)


def cli_main():
    parser = argparse.ArgumentParser('gps_csv',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='\n\n'.join((HELP['short'], HELP['full'])))
    parser.add_argument('infile', help='Path to csv')

    exc_group = parser.add_mutually_exclusive_group(required=True)

    exc_group.add_argument('-o', '--outfile', help='Path to output csv')
    parser.add_argument('-c', '--columns', required=False,
        help='''Output column order, space separated. E.g. C1 C2 BK.
            If a path to a text file is provided instead, columns will be
            searched for on the first line in the same fashion.''', nargs='+')
    parser.add_argument('-r', '--retain_empty', action='store_true', default=False,
        help='Retain rows with empty coordinates.')
    exc_group.add_argument('-i', '--inspect', action='store_true', default=False,
        help='Show attributes found in CSV.')

    parser.add_argument('-d', '--date_reformat', action='store_true', default=False,
        help='Reformat dates to EACSD compliant format.')


    args = parser.parse_args()

    if args.columns and os.path.exists(str(args.columns[0])):
        columns = open(args.columns[0]).read().strip().split('\n')[0].split()
        if not columns:
            print('{} does not contain any column data.'.format(args.columns))
            sys.exit(1)
    else:
        columns = args.columns

    try:
        result = reformat_csv(args.infile, args.outfile, columns, args.inspect,
            args.retain_empty, sys.stdout, args.date_reformat)
    except PermissionError:
        print('ERROR: {} is already open.'.format(args.outpath))

    if result:
        print('\nColumns: {}'.format(result))
