
### IN PROGRESS, DON'T CHECK!!! ###

import sqlite3
from unittest.mock import patch, MagicMock, call
from work_with_db import split_user_full_name, insert_user_info, insert_bank_name, insert_account_info, add_user, \
    add_bank, add_account, get_data_from_csv, logging_modified_data, modify_user, modify_bank, modify_account, \
    logging_deleted_id, delete_from_db, get_balance
import pytest
from connect_to_db import connect_to_database


@patch('logging.info')
@pytest.mark.parametrize("full_name, expected_output", [
    ('John Doe', ('John', 'Doe')),  # Check with full name
    ('John-Doe', ('John', 'Doe')),  # Check with a hyphen in the name
])
def test_split_user_full_name(mock_logging, full_name, expected_output):
    assert split_user_full_name(full_name) == expected_output


@patch('logging.debug')
def test_insert_user_info(mock_logging):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    test_data = ('John', 'Doe', '1990-01-01', 2)

    insert_user_info(mock_cursor, *test_data)
    mock_cursor.execute.assert_called_once_with(
        'INSERT INTO User (name, surname, birth_day, accounts) VALUES (?, ?, ?, ?)', test_data)


@connect_to_database
@patch('logging.debug')
def test_insert_bank_name(mock_logging):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    test_name = 'Bank A'

    insert_bank_name(mock_cursor, test_name)
    mock_cursor.execute.assert_called_once_with('INSERT INTO Bank (name) VALUES (?)', (test_name,))


@patch('logging.debug')
def test_insert_account_info(mock_logging):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    test_data = (1, 'credit', '12345678', 1, 'USD', -2000, 'gold')

    insert_account_info(mock_cursor, test_data)
    mock_cursor.execute.assert_called_once_with(
        'INSERT INTO Account (User_id, Type, Account_Number, Bank_id, Currency, Amount, Status) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)', test_data)


# @patch('logging.debug')
# @patch('work_with_db.split_user_full_name', return_value=['John', 'Doe'])
# @patch('work_with_db.insert_user_info')
# def test_add_user(mock_logging, mock_insert_user_info, mock_split_user_full_name):
#     mock_cursor = MagicMock()
#
#     user_info_dict = {'user_full_name': 'John Doe', 'birth_day': '1990-01-01', 'accounts': '123,456'}
#     user_info_tuple = ('Jane Doe', '1992-02-02', '789,012')
#     add_user(mock_cursor, user_info_dict)
#
#     assert mock_split_user_full_name.called
#     assert mock_insert_user_info.called


@patch('logging.info')
@patch('logging.debug')
def test_logging_modified_data(mock_debug, mock_info):
    name = 'John Doe'
    modified_id = '123'
    modified_data = {'email': 'johndoe@example.com'}
    logging_modified_data(name, modified_id, modified_data)

    mock_info.assert_called_once_with(f'{name} data {modified_id} successfully changed.')
    mock_debug.assert_called_once_with(f'Modified data: {modified_data}')


@patch('work_with_db.logging_modified_data')
def test_modify_user(mock_logging):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    test_data = {
        'name': 'New Name',
        'surname': 'New Surname',
        'birth_day': '2000-01-01',
        'accounts': '987,674'
    }
    test_id = 1

    modify_user.__wrapped__(mock_cursor, test_id, test_data)
    mock_cursor.execute.assert_called_once_with(
        'UPDATE User SET name=?, surname=?, birth_day=?, accounts=? WHERE id=?',
        (test_data['name'], test_data['surname'], test_data['birth_day'], test_data['accounts'], test_id))


@patch('work_with_db.logging_modified_data')
def test_modify_bank(mock_logging):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    test_data = {'bank_name': 'Bank O'}
    test_id = 1

    modify_bank.__wrapped__(mock_cursor, test_id, test_data)
    mock_cursor.execute.assert_called_once_with('UPDATE Bank SET name=? WHERE id=?', (test_data['bank_name'], test_id))


@patch('work_with_db.logging_modified_data')
def test_modify_account(mock_logging):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    test_data = {'user_id': 123,
                 'type': 'debit',
                 'account_number': '12345778',
                 'bank_id': 1,
                 'currency': 'USD',
                 'amount': -13400,
                 'status': 'gold'
                 }

    test_id = 1

    modify_account.__wrapped__(mock_cursor, test_id, test_data)
    mock_cursor.execute.assert_called_once_with(
        'UPDATE Account SET user_id=?, type=?, account_number=?, bank_id=?, currency=?, amount=?, status=? WHERE Id=?',
        (test_data['user_id'], test_data['type'], test_data['account_number'], test_data['bank_id'],
         test_data['currency'],
         test_data['amount'], test_data['status'], test_id))


@patch('logging.info')
def test_logging_deleted_id(mock_info):
    test_name = 'User'
    test_id = 1

    logging_deleted_id(test_name, 1)
    mock_info.assert_called_once_with(f'{test_name} data {test_id} successfully deleted')


#############################################

# @patch('work_with_db.logging_deleted_id')
# def test__delete_user(mock_logging):
#     mock_cursor = MagicMock(spec=sqlite3.Cursor)
#
#     test_id = 1
#
#     delete_user.__wrapped__(mock_cursor, test_id)
#     mock_cursor.execute.assert_called_once_with('DELETE FROM User WHERE id = ?', (test_id,))
#
#
# @patch('work_with_db.logging_deleted_id')
# def test_delete_bank(mock_logging):
#     mock_cursor = MagicMock(spec=sqlite3.Cursor)
#
#     test_id = 1
#
#     delete_user.__wrapped__(mock_cursor, test_id)
#     mock_cursor.execute.assert_called_once_with('DELETE FROM Bank WHERE id = ?', (bank_id,))
#
#

# @patch('work_with_db.logging_deleted_id')
# def test_delete_account(mock_logging):
#     mock_cursor = MagicMock(spec=sqlite3.Cursor)
#
#     test_id = 1
#
#     delete_user.__wrapped__(mock_cursor, test_id)
#     mock_cursor.execute.assert_called_once_with('DELETE FROM User WHERE id = ?', (test_id,))
###########################################################################################


@patch('work_with_db.logging_deleted_id')
def test_delete_from_db(mock_logging):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    test_id = 1
    test_name = 'User'

    delete_from_db.__wrapped__(mock_cursor, test_id, test_name)
    mock_cursor.execute.assert_called_once_with(f'DELETE FROM {test_name} WHERE id = ?', (test_id,))

# @patch('logging.debug')
# def test_get_balance(mock_logging):
#     mock_cursor = MagicMock(spec=sqlite3.Cursor)
#
#     test_id = 1
#
#     actual = get_balance.__wrapped__(mock_cursor, test_id)
#     expected = (1000, 'USD', '001')
#     mock_cursor.fetchone.return_value = expected
#     mock_cursor.execute.assert_called_once_with('SELECT amount, currency, bank_id FROM Account WHERE id = ?',
#                                                 (test_id,))
#
#
#     assert actual == expected
