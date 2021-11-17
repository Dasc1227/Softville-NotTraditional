import pytest

tests = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5)
]


@pytest.mark.parametrize("value1, value2", tests)
def test_example2(value1, value2):
    assert value1 == value2
