import argparse
import re
import sys
from collections import defaultdict


def parse_eacsd_errors(eacsdpath, errorspath, callback=None):
    results = defaultdict(list)

    with open(eacsdpath) as eacsd_file, open(errorspath) as eacsd_error_list:
        errors = eacsd_error_list.read()
        eacsd_data = eacsd_file.readlines()

        lines_errors = re.findall('Line (\d*):\s(.*)', errors, re.I)
        for line_no, error in lines_errors:
            line_no = int(line_no)

            rev = list(reversed(eacsd_data))

            for search_line in rev[len(rev) - line_no:]:
                if 'Section_Name' in search_line:
                    name = search_line.strip().split('=')[-1]
                    results[name].append(error)
                    break

    name_order = sorted(results.keys())

    for name in name_order:
        callback.write(name + '\n')
        for error in results[name]:
            callback.write('    ' + error + '\n')
        callback.write('\n')


def cli_main():
    parser = argparse.ArgumentParser('eacsderrors')
    parser.add_argument('eacsd')
    parser.add_argument('errors')

    args = parser.parse_args()

    parse_eacsd_errors(args.eacsd, args.errors, sys.stdout)
