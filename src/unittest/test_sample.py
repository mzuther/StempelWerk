import pytest


def inc(x):
    return x + 1


def test_increment_integer():
    assert inc(3) == 4


def test_increment_float():
    assert inc(3.14) == pytest.approx(4.14)
