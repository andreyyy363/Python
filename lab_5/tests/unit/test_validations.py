import pytest
from unittest.mock import patch
from datetime import datetime
from validations import (validate_user_name, validate_field_with_strict_set_of_values, validate_current_time,
                         validate_account_number)


@pytest.mark.parametrize('test_full_name, expected', [
    ('John123 Doe!?', ('John', 'Doe'))
])
def test_validate_user_name_success(test_full_name, expected):
    assert validate_user_name(test_full_name) == expected


@pytest.mark.parametrize('value, expected', [('savings', 'Not allowed value savings for field account_type!'),
                                             ('rent', 'Not allowed value rent for field account_type!')])
def test_validate_field_with_strict_set_of_values(value, expected):
    with pytest.raises(ValueError, match=expected):
        validate_field_with_strict_set_of_values({'credit', 'debit'}, value, 'account_type')


@pytest.mark.parametrize('input_date_time, expected', [
    ('2023-11-11 23:32:10', '2023-11-11 23:32:10'),
    (None, '2024-05-06 12:43:26')
])
@patch('validations.datetime')
def test_validate_current_time(mock_datetime, input_date_time, expected):
    mock_now = datetime(2024, 5, 6, 12, 43, 26)
    mock_datetime.now.return_value = mock_now

    assert validate_current_time(input_date_time) == expected


@pytest.mark.parametrize('number, expected', [('ID--AB-12345679012', 'Account number has broken ID pattern!'),
                                              ('ID--12345678901234567', 'Too many chars in account number!'),
                                              ('ID--1234567890', 'Too little chars in account number!'),
                                              ('ID-123456789012348', 'Account number has the wrong format')])
def test_validate_account_number(number, expected):
    with pytest.raises(ValueError, match=expected):
        validate_account_number(number)
