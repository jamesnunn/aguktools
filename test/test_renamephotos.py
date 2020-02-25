import glob
import tempfile
import os
import hashlib

from aguktools.renamephotos import link_eacsd_photos


ROOT = os.path.dirname(__file__)


def md5(path):
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def test_link_data():

    eacsd_path = os.path.join(ROOT, 'data/SHEE01.txt')
    photo_path = os.path.join(ROOT, 'data/photos')
    exp_out_dir = os.path.join(ROOT, 'data/renamedphotos')
    out = tempfile.TemporaryDirectory()

    link_eacsd_photos(eacsd_path, photo_path, out.name, 'EA', True)

    exp_photos = {
        'SHEE01_00001_DS_1.jpg': '71055a87745fbfd119c374810fdd2002',
        'SHEE01_00001_US_1.jpg': '0ef91a4e7ab6612e26b9bcc467fc56e3',
        'SHEE01_00007_DS_1.jpg': '71055a87745fbfd119c374810fdd2002',
        'SHEE01_00007_US_1.jpg': '0ef91a4e7ab6612e26b9bcc467fc56e3',
        'SHEE01_00009_DS_1.jpg': '0ef91a4e7ab6612e26b9bcc467fc56e3',
        'SHEE01_00009_US_1.jpg': '0ef91a4e7ab6612e26b9bcc467fc56e3',
        'SHEE01_00012_DS_1.jpg': '71055a87745fbfd119c374810fdd2002',
        'SHEE01_00012_US_1.jpg': '0ef91a4e7ab6612e26b9bcc467fc56e3',
        'SHEE01_00019_DS_1.jpg': '1127afb8988120063841235ff6dfdc65',
        'SHEE01_00019_US_1.jpg': '62c4534393da3b0b854ff99f3711e4df',
        'SHEE01_00019_US_2.jpg': '0ef91a4e7ab6612e26b9bcc467fc56e3'
    }

    out_photos = {os.path.basename(x): md5(x) for x in glob.glob(os.path.join(out.name, '*.jpg'))}
    assert exp_photos == out_photos

    exp_wl = [
        'SHEE01_00001,WL=2.31m at 14:08 on 17/02/2017',
        'SHEE01_00007,WL=2.31m at 13:53 on 17/02/2017',
        'SHEE01_00009,WL=2.31m at 13:53 on 17/02/2017',
        'SHEE01_00012,WL=2.30m at 13:40 on 17/02/2017',
        'SHEE01_00019,WL=2.31m at 13:33 on 17/02/2017',
        'SHEE01_00026,WL=2.29m at 11:14 on 17/02/2017',
        'SHEE01_00030,WL=2.29m at 11:07 on 17/02/2017',
        'SHEE01_00034,WL=2.28m at 11:00 on 17/02/2017',
        'SHEE01_00040,WL=2.29m at 11:04 on 17/02/2017',
        'SHEE01_00046,WL=2.27m at 10:35 on 17/02/2017',
        'SHEE01_00052,WL=2.32m at 10:23 on 17/02/2017',
        'SHEE01_00058,WL=2.28m at 10:18 on 17/02/2017',
        'SHEE01_00064,WL=2.35m at 09:31 on 17/02/2017',
        'SHEE01_00070,WL=2.30m at 09:39 on 17/02/2017',
        'SHEE01_00076,WL=2.29m at 09:46 on 17/02/2017',
        'SHEE01_00081,WL=2.29m at 09:57 on 17/02/2017',
        'SHEE01_00087,WL=2.30m at 12:45 on 17/02/2017',
        'SHEE01_00093,WL=2.27m at 12:51 on 17/02/2017',
        'SHEE01_00098,WL=2.30m at 12:55 on 17/02/2017',
        'SHEE01_00104,WL=2.31m at 13:00 on 17/02/2017']

    out_wl = [x.strip() for x in open(os.path.join(out.name, 'WL_SHEE01.csv')).readlines()]
    assert exp_wl == out_wl


    exp_eacsd = open(os.path.join(exp_out_dir, 'SHEE01.txt')).read()
    out_eacsd = open(os.path.join(out.name, 'SHEE01.txt')).read()
    assert exp_eacsd == out_eacsd
