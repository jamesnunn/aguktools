import os
import aguktools.checkisis as isis

ROOT = os.path.dirname(__file__)


def test_isis_check():
    dat_path = os.path.join(ROOT, 'MLHB01.dat')
    with open(dat_path) as infile_obj:
        messages = isis.check_isis_banks(infile_obj.read())

    assert messages == ['MLHB01_00551 contains multiple RB',
                        'MLHB01_00551 contains multiple LB',
                        'MLHB01_00438 contains multiple RB',
                        'MLHB01_00438 RB found before LB',
                        'MLHB01_00213 missing RB',
                        'MLHB01_00213 contains multiple LB',
                        'MLHB01_00124 missing LB',
                        'MLHB01_00124 contains multiple RB',
                        'MLHB01_00122 missing RB',
                        'MLHB01_00122 missing LB',
                        'MLHB01_00121 missing RB']




