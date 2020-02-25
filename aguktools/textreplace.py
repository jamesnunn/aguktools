import argparse
import csv
import glob
import os
import re
import sys
import time
from collections import OrderedDict

import aguktools.common


def multi_replace(instr, replace_list, case_sensitive=False):
    """Replaces multiple substrings in a string

    Arguments:
        instr (str): Input string to replace substrings in.
        replace_list (list(str, str)): List of (find, replace) string pairs.
    """
    for repl_item, repl_val in replace_list:
        instr = re.sub(repl_item, repl_val, instr, flags=case_sensitive or re.I)
    return instr


def replace_strings_in_file_paths(paths, replace_list, case_sensitive=False,
    callback=None, eacsd_date=False):
    clean_folder = os.path.join(os.path.dirname(os.path.abspath(paths[0])), 'clean')

    if not os.path.exists(clean_folder):
        os.mkdir(clean_folder)

    with open(os.path.join(clean_folder, 'README.txt'), 'w') as readme_obj:
        readme_obj.write('These files are automatically generated, if you edit'
            ' these your changes may be lost')

    for path in paths:
        outpath = os.path.join(clean_folder, os.path.basename(path))
        with open(path, 'r') as infile_obj, open(outpath, 'w') as outfile_obj:
            for line in infile_obj.readlines():
                replaced_str = multi_replace(line, replace_list, case_sensitive).strip()

                if eacsd_date:
                    if re.search('fcdate', replaced_str, re.I):
                        found_date = re.findall('.*FCDATE\s*(.*)', replaced_str, re.I)
                        if found_date:
                            date = found_date[0]
                            replaced_str = re.sub(date, aguktools.common.parse_date(date, eacsd_date=eacsd_date), replaced_str)
                outfile_obj.write(replaced_str + '\n')
    if callback:
        callback.write('Replacements:\n' + '\n  '.join([' --> '.join(pair) for pair in replace_list]))
        callback.write('\nFiles found:\n' + '\n  '.join(paths))


def get_replace_list(infile):
    with open(infile) as replace_file:
        replace_list = list(csv.reader(replace_file))
    return replace_list


def get_file_list(inpath, extension):
    if os.path.isfile(inpath):
        paths = [inpath]
    elif os.path.isdir(inpath):
        ext = ''.join(OrderedDict.fromkeys(extension))
        if not ext.startswith('.'):
            ext = '.' + ext
        paths = glob.glob(os.path.join(inpath, '*' + ext))
    else:
        raise FileNotFoundError('File not found: {}'.format(inpath))
    return paths


def cli_main():
    parser = argparse.ArgumentParser('textreplace')
    parser.add_argument('inpath')
    parser.add_argument('replacefile')
    parser.add_argument('-c', '--case_sensitive', default=False, action='store_true', required=False)
    parser.add_argument('-d', '--dates', default=False, action='store_true', required=False, help='Reformat dates')
    parser.add_argument('--ext', required=False, default='.dc')
    args = parser.parse_args()

    try:
        paths = get_file_list(args.inpath, args.ext)
    except FileNotFoundError as err:
        print(str(err))
        sys.exit(1)

    replace_list = get_replace_list(args.replacefile)
    replace_strings_in_file_paths(paths, replace_list, args.case_sensitive, sys.stdout, args.dates)
