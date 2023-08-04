import pytest
from lab_1.var_15 import generate_random_array, find_zero, find_sum_of_negative_paired_elements


def test_generating_random_array():
    input_row = 3
    input_col = 5
    actual = generate_random_array(input_row, input_col)
    expected_row = 3
    expected_col = 5
    # Check for array size
    assert len(actual) == expected_row
    assert all(len(i) == expected_col for i in actual)

    for i in actual:
        for j in i:
            # Check for range
            assert -10 <= j <= 10
            # Check for int type
            assert isinstance(j, int)


def test_find_zero():
    # Test for array with zero
    input_arr = [[1, 2, 3], [4, 0, 6], [7, 8, 9]]
    actual = find_zero(input_arr)
    expected = True
    assert actual == expected

    # Test for array without zero
    input_arr = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    actual = find_zero(input_arr)
    expected = False
    assert actual == expected


def test_find_sum_of_negative_paired_elements():
    # Test for random values in array
    input_arr = [[-2, -3, 4], [-6, 6, -9], [7, -8, -4]]
    actual = find_sum_of_negative_paired_elements(input_arr)
    expected = [-8, -6, -4, -2]
    assert actual == expected

    # Test for all positive elements
    input_arr = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    actual = find_sum_of_negative_paired_elements(input_arr)
    expected = []
    assert actual == expected
