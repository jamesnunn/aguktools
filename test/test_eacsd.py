import os

import eacsd

ROOT = os.path.dirname(__file__)


def test_parse_eacsd():
    eacsd_path = os.path.join(ROOT, 'MARN01_check.txt')
    with open(eacsd_path) as infile_obj:
        contents = infile_obj.read()
        infile_obj.seek(0)
        eacsd_obj = eacsd.parse_eacsd(infile_obj)

    assert contents == eacsd_obj.write()

