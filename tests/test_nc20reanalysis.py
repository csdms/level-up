"""Unit tests for the nc20reanalysis module."""

import os
import pytest
from nc20reanalysis import Nc20Reanalysis


test_dir = os.path.dirname(__file__)
data_dir = os.path.abspath(os.path.join(test_dir, '..', 'data'))
reanalysis_file = os.path.join(data_dir, 'X174.29.255.181.65.14.23.9.nc')


def test_file_exists():
    assert os.path.exists(reanalysis_file) == True


def test_instantiate():
    n = Nc20Reanalysis()
    assert isinstance(n, Nc20Reanalysis)
    assert n.filename is None


def test_instantiate_with_file():
    n = Nc20Reanalysis(reanalysis_file)
    assert isinstance(n, Nc20Reanalysis)
    assert n.filename == reanalysis_file


def test_read_no_file():
    with pytest.raises(TypeError):
        n = Nc20Reanalysis()
        n.read()


def test_read_not_netcdf_file():
    n = Nc20Reanalysis('foo.txt')
    n.read()
    assert n.filename == 'foo.txt'
    assert n.level == None


def test_read_success():
    n = Nc20Reanalysis(reanalysis_file)
    n.read()
    assert n.filename == reanalysis_file
    assert n.level == 500.0


def test_read_success_set_file():
    n = Nc20Reanalysis()
    n.filename = reanalysis_file
    n.read()
    assert n.filename == reanalysis_file
    assert n.level == 500.0


def test_prep_no_data():
    with pytest.raises(AttributeError):
        n = Nc20Reanalysis()
        n.prep()


def test_view_no_data():
    with pytest.raises(TypeError):
        n = Nc20Reanalysis()
        n.view()


def test_view_bad_dayofyear():
    n = Nc20Reanalysis(reanalysis_file)
    n.read()
    n.prep()
    with pytest.raises(IndexError):
        n.view(dayofyear=1000)


def test_view_output_exists():
    n = Nc20Reanalysis(reanalysis_file)
    n.read()
    n.prep()
    n.view()
    assert os.path.exists('gph.png')
