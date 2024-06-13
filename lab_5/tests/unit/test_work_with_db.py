import sqlite3
from unittest.mock import patch, MagicMock, call, mock_open
from work_with_db import (split_user_full_name, split_full_name_in_dict, add_data, get_data_from_csv,
                          add_table_data_from_csv, modify_data, delete_from_db, get_balance, get_bank_name,
                          insert_transaction, perform_currency_conversion, update_balances, perform_transfer,
                          get_users_ids, get_data_from_db, get_transactions_for_user, get_discount_for_random_users,
                          get_users_with_debts, get_full_names_of_users_with_debts, get_bank_with_biggest_capital,
                          get_bank_serving_oldest_client, get_bank_with_most_unique_outbound_transactions, delete_row,
                          delete_users_and_accounts_with_missing_info, convert_transactions_datetime,
                          filter_transactions_past_3_months)
from const import (FULL_NAME, NAME, SURNAME, ID, USER_ID, BANK_ID, BIRTH_DAY, USERS_TABLE, TRANSACTIONS_TABLE,
                   ACCOUNTS_TABLE, DATETIME, THREE_MONTHS, FORMAT)
import pytest
from datetime import datetime, timedelta

TEST_ID = 1


@patch('validations.validate_user_name', return_value={NAME: 'John', SURNAME: 'Doe'})
@pytest.mark.parametrize('full_name, expected_output', [({FULL_NAME: 'John Doe'}, {NAME: 'John', SURNAME: 'Doe'})])
def test_split_user_full_name(mock_f, full_name, expected_output):
    assert split_user_full_name(full_name) == expected_output


@patch('work_with_db.split_user_full_name', return_value={'name': 'John', 'surname': 'Doe'})
@pytest.mark.parametrize('input_data, expected_output', [([{'user_full_name': 'John Doe'},
                                                           {'user_full_name': 'Jane Smith'}],
                                                          [{'name': 'John', 'surname': 'Doe'},
                                                           {'name': 'John', 'surname': 'Doe'}])])
def test_split_full_name_in_dict(mock_split_user_full_name, input_data, expected_output):
    actual = split_full_name_in_dict(input_data)

    for user_data in input_data:
        mock_split_user_full_name.assert_any_call(user_data)

    assert actual == expected_output


@pytest.mark.parametrize('test_table_name, test_fields, test_data, expected_query', [
    ('test_table', ('field1', 'field2'),
     [{'field1': 'value1', 'field2': 'value2'}, {'field1': 'value3', 'field2': 'value4'}],
     'INSERT INTO test_table (field1, field2) VALUES (:field1, :field2)'),
])
@patch('work_with_db.logger')
def test_add_data(mock_logger, test_table_name, test_fields, test_data, expected_query):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    add_data.__wrapped__(mock_cursor, test_table_name, test_fields, test_data)

    mock_cursor.executemany.assert_called_once()
    mock_logger.info.assert_called_once_with('%s data successfully added.', test_table_name)
    mock_logger.debug.assert_called_once_with('Inserted %s data: %s', test_table_name, test_data)


@patch('builtins.open', new_callable=mock_open,
       read_data='user_full_name;user_id;birth_day;accounts;bank_id;bank_name;type;account_number;currency;amount;status\n'
                 "Bob Smith;2;22.07.1988;7895643;11;Bank B;debit;789,012;EUR;500;silver\n"
                 "Emma Miller;5;10.12.1985;90146456;3;Bank E;credit;275,688;EUR;1500;platinum")
@patch('csv.DictReader', return_value=[
    {'user_full_name': 'Bob Smith', 'birth_day': '22.07.1988', 'accounts': '7895643'},
    {'user_full_name': 'Emma Miller', 'birth_day': '10.12.1985', 'accounts': '90146456'}
])
def test_get_data_from_csv(mock_dict_reader, mock_open_file):
    path = 'fake_path.csv'
    fields = ['user_full_name', 'birth_day', 'accounts']

    expected_result = [
        {'user_full_name': 'Bob Smith', 'birth_day': '22.07.1988', 'accounts': '7895643'},
        {'user_full_name': 'Emma Miller', 'birth_day': '10.12.1985', 'accounts': '90146456'}
    ]

    result = get_data_from_csv(path, fields)
    assert result == expected_result
    mock_open_file.assert_called_once_with(path, 'r', newline='', encoding='utf-8')


@patch('work_with_db.get_data_from_csv')
@patch('work_with_db.split_full_name_in_dict')
@patch('work_with_db.add_data')
@patch('work_with_db.logger')
def test_add_table_data_from_csv(mock_logger, mock_add_data, mock_split_full_name_in_dict, mock_get_data_from_csv):
    path = 'test_data.csv'
    table_name = 'users'
    fields = ['full_name', 'email', 'age']

    add_table_data_from_csv(path, table_name, fields)

    mock_get_data_from_csv.assert_called_once()
    mock_add_data.assert_called_once()
    mock_logger.info.assert_called_once_with('Data from csv successfully added.')



@patch('work_with_db.logger')
@pytest.mark.parametrize('table_name, data', [('test_table', {'field1': 'value1', 'field2': 'value2'})])
def test_modify_data(mock_logger, table_name, data):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    modify_data.__wrapped__(mock_cursor, table_name, TEST_ID, data)

    mock_cursor.execute.assert_called_once()
    mock_logger.info.assert_called_once_with('%s data %s successfully changed.', table_name, TEST_ID)
    mock_logger.debug.assert_called_once_with('Modified data: %s', data)


@patch('work_with_db.logger.info')
def test_delete_from_db(mock_logger):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)
    test_table_name = 'test_table'

    delete_from_db.__wrapped__(mock_cursor, TEST_ID, test_table_name)

    mock_cursor.execute.assert_called_once()
    mock_logger.assert_called_once_with('%s data %s successfully deleted', test_table_name, TEST_ID)


@patch('work_with_db.logger.debug')
@patch('work_with_db.validate_balance')
def test_get_balance(mock_validate_balance, mock_logger):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)
    test_amount = 100
    expected_query = 'SELECT amount, currency, bank_id FROM Accounts WHERE id = ?'
    expected_data = (1000, 'USD', 123)

    mock_cursor.fetchone.return_value = expected_data

    actual = get_balance.__wrapped__(mock_cursor, TEST_ID, test_amount)
    assert actual == expected_data

    mock_cursor.execute.assert_called_once_with(expected_query, (TEST_ID,))
    mock_validate_balance.assert_called_once_with(expected_data, TEST_ID, test_amount)
    mock_logger.assert_called_once_with('Received information from account %s: %s', TEST_ID, expected_data)


def test_get_bank_name():
    mock_cursor = MagicMock(spec=sqlite3.Cursor)
    expected_query = 'SELECT bank_name FROM Banks WHERE bank_id = ?'
    expected_data = 'Bank'

    mock_cursor.fetchone.return_value = ('Bank', 1)
    actual = get_bank_name.__wrapped__(mock_cursor, TEST_ID)
    assert actual == expected_data

    mock_cursor.execute.assert_called_once_with(expected_query, (TEST_ID,))


@patch('work_with_db.get_bank_name', return_value=['Bank1', 'Bank2'])
@patch('work_with_db.logger.debug')
@pytest.mark.parametrize('test_data', [(['value1', 'value2', 'value1', 'value2', 'value1', 'value2'])])
def test_insert_transaction(mock_logger, mock_f, test_data):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    insert_transaction.__wrapped__(mock_cursor, test_data)

    mock_cursor.execute.assert_called_once()
    mock_logger.assert_called_once_with('Inserted transaction data: %s', test_data)


@patch('work_with_db.client')
@patch('work_with_db.logger.debug')
def test_perform_currency_conversion(mock_logger, mock_client):
    sender_currency = 'USD'
    receiver_currency = 'EUR'
    test_amount = 100
    test_rate = 0.85
    expected = 85

    mock_client.latest.return_value = {'data': {receiver_currency: test_rate}}
    mock_client.status.return_value = 'Mocked status'

    actual = perform_currency_conversion(sender_currency, receiver_currency, test_amount)

    assert actual == expected

    mock_client.latest.assert_called_once_with(sender_currency, [receiver_currency])
    mock_client.status.assert_called_once()
    mock_logger.assert_any_call('Mocked status')
    mock_logger.assert_any_call('Exchange rates: %s', test_rate)


@patch('work_with_db.modify_data')
@patch('work_with_db.logger.debug')
def test_update_balances(mock_logger, mock_f):
    sender = {'id': 1, 'balance': 500}
    receiver = {'id': 2, 'balance': 300}
    sender_amount = 100
    receiver_amount = 90

    update_balances(sender, receiver, sender_amount, receiver_amount)

    assert mock_f.call_count == 2
    mock_logger.assert_called_once_with('New sender balance: %s, new receiver balance: %s', 400, 390)


@patch('work_with_db.get_balance', side_effect=['Bank1', 'Bank2'])
@patch('work_with_db.perform_currency_conversion')
@patch('work_with_db.update_balances')
@patch('work_with_db.insert_transaction')
@patch('work_with_db.logger')
def test_perform_transfer(mock_logger, mock_insert_transaction, mock_update_balances, mock_perform_currency_conversion,
                          mock_get_balance):
    sender_id = 1
    receiver_id = 2
    amount_in_sender_currency = 100
    sender_balance = 500
    sender_currency = 'USD'
    sender_bank_id = 'bank_1'
    receiver_balance = 300
    receiver_currency = 'EUR'
    receiver_bank_id = 'bank_2'
    amount_in_receiver_currency = 85

    mock_get_balance.side_effect = [
        (sender_balance, sender_currency, sender_bank_id),
        (receiver_balance, receiver_currency, receiver_bank_id)
    ]

    perform_transfer(sender_id, receiver_id, amount_in_sender_currency)

    assert mock_get_balance.call_count == 2
    mock_logger.debug.assert_any_call('Sender: id - %s, bank - %s, balance - %s, currency - %s',
                                      sender_id, sender_bank_id, sender_balance, sender_currency)
    mock_logger.debug.assert_any_call('Receiver: id - %s, bank - %s, balance - %s, currency - %s',
                                      receiver_id, receiver_bank_id, receiver_balance, receiver_currency)
    mock_logger.info.assert_called_once_with('Transaction has been successfully completed.')

    mock_perform_currency_conversion.assert_called_once()
    mock_update_balances.assert_called_once()
    mock_insert_transaction.assert_called_once()


def test_get_users_ids():
    mock_cursor = MagicMock(spec=sqlite3.Cursor)
    get_users_ids.__wrapped__(mock_cursor)
    mock_cursor.execute.assert_called_once()


def test_get_data_from_db():
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    mock_cursor.description = [('id',), ('account_sender_id',), ('account_receiver_id',), ('amount',)]
    mock_cursor.fetchall.return_value = [(1, 10, 20, 100), (2, 10, 30, 200)]
    expected = [{'id': 1, 'account_sender_id': 10, 'account_receiver_id': 20, 'amount': 100},
                {'id': 2, 'account_sender_id': 10, 'account_receiver_id': 30, 'amount': 200}]

    actual = get_data_from_db.__wrapped__(mock_cursor, 'Transactions', 1)

    mock_cursor.execute.assert_called_once()
    mock_cursor.fetchall.assert_called_once()

    assert actual == expected


@patch('work_with_db.get_data_from_db')
@patch('work_with_db.convert_transactions_datetime')
def test_get_transactions_for_user(mock_convert, mock_get_data):
    actual = get_transactions_for_user(TEST_ID)

    mock_convert.assert_called_once()
    mock_get_data.assert_called_once_with('Transactions', TEST_ID)


@patch('work_with_db.logger.info')
@patch('work_with_db.sample', return_value=[1, 2, 3])
@patch('work_with_db.choice', side_effect=[5, 10, 15])
@patch('work_with_db.randint', return_value=3)
@patch('work_with_db.get_users_ids', return_value=[1, 2, 3, 4, 5])
def test_get_discount_for_random_users(mock_get_users_ids, mock_randint, mock_choice, mock_sample, mock_logger):
    test_min, test_max = 1, 10
    expected = {1: 5, 2: 10, 3: 15}

    actual = get_discount_for_random_users()

    assert actual == expected
    mock_get_users_ids.assert_called()
    mock_randint.assert_called_once_with(test_min, min(len(mock_get_users_ids.return_value), test_max))
    mock_sample.assert_called_once_with(mock_get_users_ids.return_value, 3)
    assert mock_choice.call_count == 3
    mock_logger.assert_called_once_with('Users with discounts: %s.', expected)


@patch('work_with_db.logger.debug')
@pytest.mark.parametrize('expected', [[('John', 'Doe'), ('Jane', 'Smith')]])
def test_get_users_with_debts(mock_logger, expected):
    mock_cursor = MagicMock(spec=sqlite3.Cursor)
    mock_cursor.fetchall.return_value = [[(1,), (2,)]]
    mock_cursor.execute.return_value = [('John', 'Doe'), ('Jane', 'Smith')]

    actual = get_users_with_debts.__wrapped__(mock_cursor)

    mock_cursor.execute.assert_any_call('SELECT user_id FROM Accounts WHERE amount < 0')
    mock_cursor.execute.assert_any_call('SELECT name, surname AS full_name FROM Users WHERE id = ?', ((1,),))
    mock_logger.assert_called_once_with('User names with debts: %s.', expected)

    assert mock_cursor.execute.call_count == 2
    assert actual == expected


@patch('work_with_db.get_users_with_debts', return_value=[('John', 'Doe'), ('Jane', 'Smith')])
@patch('work_with_db.logger.info')
def test_get_full_names_of_users_with_debts(mock_logger, mock_get_users):
    expected = ['John Doe', 'Jane Smith']
    actual = get_full_names_of_users_with_debts()

    assert actual == expected

    mock_get_users.assert_called_once()
    mock_logger.assert_called_once_with('Users with debts: %s', expected)


@pytest.mark.parametrize('accounts, expected', [
    ([{'bank_id': 'BankA', 'amount': 100}, {'bank_id': 'BankB', 'amount': 200}, {'bank_id': 'BankA', 'amount': 150}],
     'BankB'),
    ([{'bank_id': 'BankA', 'amount': 100}, {'bank_id': 'BankB', 'amount': 200}, {'bank_id': 'BankB', 'amount': 300}],
     'BankB')])
@patch('work_with_db.get_data_from_db')
def test_get_bank_with_biggest_capital(mock_get_data, accounts, expected):
    mock_get_data.return_value = accounts

    actual = get_bank_with_biggest_capital()
    assert actual == expected


@patch('work_with_db.get_data_from_db')
def test_get_bank_serving_oldest_client(mock_get_data_from_db):
    mock_users = [{ID: 1, BIRTH_DAY: '1980-01-01'}, {ID: 2, BIRTH_DAY: '1970-05-15'}, {ID: 3, BIRTH_DAY: '1990-07-20'}]
    mock_accounts = [{USER_ID: 1, BANK_ID: 'BankA'}, {USER_ID: 2, BANK_ID: 'BankB'}, {USER_ID: 3, BANK_ID: 'BankC'}]
    mock_get_data_from_db.side_effect = lambda table: mock_users if table == USERS_TABLE else mock_accounts
    expected = 'BankB'

    actual = get_bank_serving_oldest_client()
    assert actual == expected

    mock_get_data_from_db.assert_any_call(USERS_TABLE)
    mock_get_data_from_db.assert_any_call(ACCOUNTS_TABLE)
    assert mock_get_data_from_db.call_count == 2


@patch('work_with_db.get_data_from_db', return_value=[{'bank_sender_name': 'BankA', 'account_sender_id': 1},
                                                      {'bank_sender_name': 'BankA', 'account_sender_id': 2},
                                                      {'bank_sender_name': 'BankB', 'account_sender_id': 3},
                                                      {'bank_sender_name': 'BankA', 'account_sender_id': 2}])
def test_get_bank_with_most_unique_outbound_transactions(mock_get_data_from_db):
    expected = 'BankA'
    actual = get_bank_with_most_unique_outbound_transactions()

    assert actual == expected

    mock_get_data_from_db.assert_called_once_with(TRANSACTIONS_TABLE)


@patch('work_with_db.delete_from_db')
@patch('work_with_db.logger.debug')
def test_delete_row(mock_logger, mock_delete_from_db):
    data_to_delete = [1, 2, 3]
    del_user = True

    delete_row(data_to_delete, del_user)

    for id_ in data_to_delete:
        mock_delete_from_db.assert_any_call(id_, del_user)
    assert mock_delete_from_db.call_count == len(data_to_delete)

    mock_logger.assert_called_once_with('Deleted data: %s', data_to_delete)


@patch('work_with_db.delete_row')
@patch('work_with_db.get_data_from_db')
@patch('work_with_db.logger')
def test_delete_users_and_accounts_with_missing_info(mock_logger, mock_get_data_from_db, mock_delete_row):
    mock_users = [
        {ID: 1, 'name': 'John', 'surname': 'Doe', BIRTH_DAY: None},
        {ID: 2, 'name': None, 'surname': 'Smith', BIRTH_DAY: '1980-05-05'},
        {ID: 3, 'name': 'Jane', 'surname': 'Doe', BIRTH_DAY: '1990-07-20'}
    ]
    mock_accounts = [
        {ID: 1, 'balance': 100, 'account_type': None},
        {ID: 2, 'balance': None, 'account_type': 'savings'},
        {ID: 3, 'balance': 200, 'account_type': 'checking'}
    ]
    mock_get_data_from_db.side_effect = lambda table: mock_users if table == USERS_TABLE else mock_accounts

    delete_users_and_accounts_with_missing_info()
    assert mock_delete_row.call_count == 4
    mock_logger.info.assert_called_once_with(
        'Users and accounts data without all information has been successfully deleted.')


def test_convert_transactions_datetime():
    expected = [
        {ID: 1, DATETIME: datetime.strptime('2023-01-01 12:00:00', FORMAT)},
        {ID: 2, DATETIME: datetime.strptime('2023-01-02 13:00:00', FORMAT)}
    ]
    test_data = [{ID: 1, DATETIME: '2023-01-01 12:00:00'}, {ID: 2, DATETIME: '2023-01-02 13:00:00'}]

    actual = convert_transactions_datetime(test_data)

    assert actual == expected


@patch('work_with_db.get_transactions_for_user')
def test_filter_transactions_past_3_months(mock_get_transactions_for_user):
    three_months_ago = datetime.now() - timedelta(days=THREE_MONTHS)
    expected = [{ID: 1, DATETIME: three_months_ago + timedelta(days=1)}]

    mock_get_transactions_for_user.return_value = [{ID: 1, DATETIME: three_months_ago + timedelta(days=1)},
                                                   {ID: 2, DATETIME: three_months_ago - timedelta(days=1)}]

    actual = filter_transactions_past_3_months(TEST_ID)

    assert actual == expected

    mock_get_transactions_for_user.assert_called_once_with(TEST_ID)
