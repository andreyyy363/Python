import pytest
from lab_1.var_5 import generating_random_array, sum_of_positive_elements, min_sum


def test_generating_random_array():
    input_size = 10
    actual = generating_random_array(input_size)
    expected = 10
    # Check for array size
    assert len(actual) == expected
    assert all(len(i) == expected for i in actual)

    for i in actual:
        for j in i:
            # Check for range
            assert -5 <= j <= 10
            # Check for int type
            assert isinstance(j, int)


def test_sum_of_positive():
    # Test for all positive elements
    input_arr = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    input_size = 3
    actual = sum_of_positive_elements(input_arr, input_size)
    expected = [12, 15, 18]
    assert actual == expected

    # Test for all negative elements
    input_arr = [[-1, -2, -3], [-4, -5, -6], [-7, -8, -9]]
    input_size = 3
    actual = sum_of_positive_elements(input_arr, input_size)
    expected = [0, 0, 0]
    assert actual == expected

    # Test for mixed values
    input_arr = [[1, 2, -3], [-4, 5, -6], [7, 8, 9]]
    input_size = 3
    actual = sum_of_positive_elements(input_arr, input_size)
    expected = [0, 15, 0]
    assert actual == expected


def test_min_sum():
    # Test for all positive elements
    input_arr = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    input_size = 3
    actual = min_sum(input_arr, input_size)
    expected = 1
    assert actual == expected

    # Test for all negative elements
    input_arr = [[-1, -2, -3], [-4, -5, -6], [-7, -8, -9]]
    input_size = 3
    actual = min_sum(input_arr, input_size)
    expected = 1
    assert actual == expected

    # Test for mixed values
    input_arr = [[-4, 8, -6, 10], [15, 1, 3, -7], [-9, -5, 19, -1], [8, 6, -13, 0]]
    input_size = 4
    actual = min_sum(input_arr, input_size)
    expected = 0
    assert actual == expected
