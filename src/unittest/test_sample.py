import pytest


def inc(x):
    return x + 1


class TestSample:
    def test_increment_integer(self):
        result = inc(3)
        assert result == 4
        assert isinstance(result, int)


    def test_increment_float(self):
        result = inc(3.14)
        assert result == pytest.approx(4.14)
        assert isinstance(result, float)
