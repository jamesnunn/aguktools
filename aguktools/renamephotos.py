import argparse
import os
import re
import glob
import datetime
import shutil
import string
import sys
import traceback

import eacsd

HELP = ''' Links an EACSD file with photos and renames them. Optionally writes
a file with formatted water level text.

Photos must be named with one of the following patterns in order to link them:
    - Section number with us/ds/va suffix, e.g. 001us, 045ds
    - Section number with us/ds/va suffix plus enumerator, e.g. 001ds1, 0045ds2
    - Range of section numbers with single us/ds/va suffix, e.g. 010-015ds
    - Range of section numbers with single us/ds/va suffix plus enumerator, e.g. 010-015ds1

Photos named with a suffix will be linked to photo points in the order they are
found in the EACSD. The order they are written in the EACSD is based on the order
N4ce finds them in the cross section models, not based on the string number.
Care must be taken to make sure the photos are in the right order to use this
functionality.


Photos which do not match any of the above patterns will be ignored. If a range
is supplied, any section numbers missing from that range in the EACSD will be
ignored.

The output directory will contain copies of the photos renamed with a certain pattern.
At the moment, only 2 known patterns are accommodated:
    - EA - <REACH><REACHID>_<CHAINAGE>_<DIRECTION>_<ENUMERATOR>  e.g. WOOL01_00123_US_1
    - EANE - <REACH><REACHID>_P_<CHAINAGE>_<YYYMM>_<DIRECTION>_<ENUMERATOR>  e.g. WOOL01_P_00123_201612_US_1

If the water level file is requested, a CSV will be exported containing text
formatted for presentation, e.g. WL=21.61m at 16:18 on 15/02/2017
'''


def add_photo(p, direct, photo, d):
    if p not in d:
        d[p] = {}

    if direct not in d[p]:
        d[p][direct] = []

    d[p][direct].append(photo)


def main():
    parser = argparse.ArgumentParser('eacsdphotos')
    parser.add_argument('inpath', help='Path to eacsd file.')
    parser.add_argument('photopath', help='Path to photo folder.')
    parser.add_argument('outdir', help='Path to output directory')
    parser.add_argument('-p', '--pattern', choices=('EA', 'EANE'), default='EA',
        help='Photo name pattern. EA North East have a specific format: '
        'SITE_P_CHN_DATE_DIR_IDX while normally the format is: SITE_CHN_DIR_IDX')
    parser.add_argument('-w', '--water_levels', required=False, action='store_true', default=False,
        help='Output water level text file')

    args = parser.parse_args()
    link_eacsd_photos(args.inpath, args.photopath, args.outdir, args.pattern,
        args.water_levels, sys.stdout)



def link_eacsd_photos(inpath, photopath, outdir, pattern, water_levels=False,
    callback=None):

    with open(inpath) as inpath_obj:
        try:
            eacsd_obj = eacsd.parse_eacsd(inpath_obj)
        except eacsd.PhotoPointError as err:
            if callback:
                msg = traceback.format_exc()
                callback.write(str(err))
            return

    site_id = eacsd_obj.nfcdd_watercourse_ref + str(eacsd_obj.nfcdd_reach_ref)

    photos = sorted(glob.glob(os.path.join(photopath, '*.jpg')))
    photo_dict = {}
    water_levels_list = []
    linked_photos = []

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # Split out all multi-section photos
    for photo in photos:
        filename = os.path.basename(photo)
        if '-' in filename:
            try:
                num1, num2, direction, idx = re.findall(r'([0-9]{3})-([0-9]{3})(ds|us|va)([1-9])?', filename, re.I)[0]
            except Exception as e:
                callback.write('Photo range using \'-\' not recognised in {filename}'.format(filename=filename))
                continue
            first = min(int(num1), int(num2))
            last = max(int(num1), int(num2)) + 1

            for xs_id in range(first, last):
                id_ = '{0:03d}'.format(xs_id)
                add_photo(id_, direction.lower(), photo, photo_dict)
            continue

        else:
            photo_pattern = r'^([0-9]{3}[A-Za-z]?)(ds|us|va)([1-9])?'
            try:
                photo_xs_id, photo_xs_dir, idx = re.findall(photo_pattern, filename, re.I)[0]
                add_photo(photo_xs_id.lower(), photo_xs_dir.lower(), photo, photo_dict)
            except IndexError as err:
                # Ignore any photo where the pattern is not found
                continue

    for xs_id, xs in eacsd_obj.cross_section_headers.items():
        xs_p_dict = {'US': (xs.photo_group.us, xs.set_upstream_photo),
                    'DS': (xs.photo_group.ds, xs.set_downstream_photo),
                    'VA': (xs.photo_group.va, xs.set_across_photo)}

        for dir_, (get_photos, set_photos) in xs_p_dict.items():

            for i, row in enumerate(get_photos):
                if pattern == 'EA':
                    # Pattern SITE01_00123_US_1
                    elems = filter(None, (site_id,
                        xs.chainage_id, dir_, i + 1))
                elif pattern == 'EANE':
                    # Pattern SITE01_P_00123_201612_US_1
                    elems = (site_id, 'P', xs.chainage_id,
                        datetime.datetime.strftime(xs.survey_datetime, '%Y%m'),
                        dir_, '{0:02d}'.format(i + 1))
                new_name = '_'.join(map(str, elems)) + '.jpg'
                try:
                    photo = photo_dict[xs_id.lower()][dir_.lower()][i]
                    shutil.copyfile(photo, os.path.join(outdir, new_name))
                    set_photos(new_name, i)
                    linked_photos.append(photo)
                except (KeyError, IndexError):
                    if callback:
                        callback.write('Photo not found for {}-{}/{}_{} {}\n'.format(xs.reach, xs_id, xs.reach, xs.chainage_id, dir_))

        water_levels_list.append('{},WL={:.2f}m at {} on {}'.format(
            '_'.join((site_id, xs.chainage_id)),
            xs.water_level or 0,
            datetime.datetime.strftime(xs.survey_datetime, '%H:%M'),
            datetime.datetime.strftime(xs.survey_datetime, '%d/%m/%Y')))

    unlinked_photos = set(photos).difference(linked_photos)
    for ul in unlinked_photos:
        callback.write('Photo not linked: {}\n'.format(os.path.basename(ul)))

    if water_levels:
        filename = os.path.splitext(os.path.join(outdir, 'WL_' + os.path.basename(inpath)))[0] + '.csv'
        with open(filename, 'w') as wl_obj:
            wl_obj.write('\n'.join(water_levels_list))

    with open(os.path.join(outdir, os.path.basename(inpath)), 'w') as out_obj:
        out_obj.write(eacsd_obj.write())
