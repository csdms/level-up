"""Unit tests for the nc20reanalysis module."""

import os
import pytest
from nc20reanalysis import read, prep, view


test_dir = os.path.dirname(__file__)
data_dir = os.path.abspath(os.path.join(test_dir, '..', 'data'))
reanalysis_file = os.path.join(data_dir, 'X174.29.255.181.65.14.23.9.nc')


def test_file_exists():
    assert os.path.exists(reanalysis_file) == True


def test_read_no_file():
    with pytest.raises(TypeError):
        r = read()


def test_read_not_netcdf_file():
    r = read('foo.txt')
    assert r == None


def test_read_success():
    r = read(reanalysis_file)
    assert type(r) == dict
    assert r['file'] == reanalysis_file
    assert r['level'] == 500.0


def test_prep_no_data():
    with pytest.raises(TypeError):
        p = prep()


def test_prep_bad_data():
    with pytest.raises(TypeError):
        p = prep([1, 2, 3])


def test_view_no_data():
    with pytest.raises(TypeError):
        v = view()


def test_view_bad_data():
    with pytest.raises(TypeError):
        v = view([1, 2, 3])


def test_view_bad_dayofyear():
    r = read(reanalysis_file)
    p = prep(r)
    with pytest.raises(IndexError):
        v = view(p, dayofyear=1000)


# def test_view_output_exists():
#     assert os.path.exists('gph.png')
