import argparse
from collections import OrderedDict
import csv
import glob
import os
import sys


def make_int_key(strings):
    """Creates a hashable 'key' by naively concatenating a sequence of floats
    in string format and converting to a string.

    args:
        strings: sequence of floats as strings e.g. `('32154.345', '56498.568')`.

    returns:
        list of integers converted from input float strings.
    """
    if not all(strings):
        return ['']
    return list(map(str, map(int, map(float, strings))))


def concat_csv_data(path, skiprows=0, header=None):
    """Collects all rows from all CSVs in `path` into a list.

    Assumes that All csv's in the folder will contain the same type of data
    and the headers are the same, if they exist.

    args:
        path: path to folder containing CSVs.
        skiprows: int, number of rows to skip, including the header row
        header: int, row index of the header row.

    returns: (list of lists, list of strings for header)
        list of rows of all files
    """
    data_list = []

    files = glob.glob(os.path.join(path, '*.csv'))
    if not files:
        raise FileNotFoundError('{} contains no eligible csv files'.format(path))

    for file_ in files:
        with open(file_) as infile:
            data = list(csv.reader(infile))
            if header is not None:
                header_row = data[header]
            else:
                header_row = None
            data_list.extend(data[skiprows:])

    return data_list, header_row


def link_data(surveydatafolder, echodatafolder, outpath, echo_prefix=None, callback=None):

    echo_data, _ = concat_csv_data(echodatafolder, 2)
    reduced_list, reduced_header = concat_csv_data(surveydatafolder, 1, 0)
    reduced_data = OrderedDict((''.join(row[:2] + make_int_key(row[2:5])), row) for row in reduced_list)

    with open(outpath, 'w', newline='') as out_file:
        errors = []
        out_csv = csv.writer(out_file)
        out_csv.writerow(reduced_header)

        for echo_row in echo_data:
            e_id, e_easting, e_northing, e_ht, e_depth, e_code = echo_row
            key = ''.join([e_code, e_id] + make_int_key([e_easting, e_northing, e_ht]))

            if echo_prefix and e_id.startswith(echo_prefix) and not e_depth:
                try:
                    reduced_data.pop(key)
                    errors.append('Discarding point {} with no depth'.format(e_id))
                except KeyError as err:
                    pass

            if not all((e_ht, e_depth)):
                continue

            # Update the corresponding record from the reduced data
            try:
                reduced_data[key][4] = float(reduced_data[key][4]) - float(e_depth)
            except KeyError as err:
                errors.append('ID {} not found in reduced file'.format(e_id))

        for k, v in reduced_data.items():
            # Remove trailing zeroes from heights
            v[4] = round(float(v[4]), 3)
            out_csv.writerow(v)

    if callback:
        callback.write('\n'.join(errors))



def cli_main():
    parser = argparse.ArgumentParser('linkechodata')
    parser.add_argument('surveydatafolder')
    parser.add_argument('echodatafolder')
    parser.add_argument('outpath')
    parser.add_argument('-p', '--prefix', required=False,
        help='Point ids with this prefix will be considered as echo sounder '
        'points to allow automatic filtering of points without depths. If '
        'omitted, or if the points do not have the prefix, no filtering will '
        'occur.')

    args = parser.parse_args()

    link_data(args.surveydatafolder, args.echodatafolder, args.outpath, args.prefix, sys.stdout)
