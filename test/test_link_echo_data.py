import tempfile
import os
import gdal

from aguktools.link_echo_data import link_data


ROOT = os.path.dirname(__file__)


def test_link_data():
    out = tempfile.NamedTemporaryFile()
    out.close()
    link_data(os.path.join(ROOT, 'data/surveydata'),
        os.path.join(ROOT, 'data/echodata'), out.name)

    with open(os.path.join(ROOT, 'data/echoout.csv')) as outexpfile, open(out.name) as outfile:
        out_exp_data = outexpfile.readlines()
        out_data = outfile.readlines()

    assert out_exp_data == out_data


def test_link_data_with_prefix():
    out = tempfile.NamedTemporaryFile()
    out.close()
    link_data(os.path.join(ROOT, 'data/surveydata'),
        os.path.join(ROOT, 'data/echodata'), out.name, 'ES')

    with open(os.path.join(ROOT, 'data/echoout_prefix.csv')) as outexpfile, open(out.name) as outfile:
        out_exp_data = outexpfile.readlines()
        out_data = outfile.readlines()

    assert out_exp_data == out_data