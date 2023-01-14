import pytest


def inc(x):
    return x + 1


class TestSample:
    def test_increment_integer(self):
        assert inc(3) == 4


    def test_increment_float(self):
        assert inc(3.14) == pytest.approx(4.14)
