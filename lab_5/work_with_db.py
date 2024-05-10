import csv
import re
from random import randint, sample, choice
import logging
from datetime import datetime, timedelta
import os
import freecurrencyapi
from dotenv import load_dotenv
from connect_to_db import connect_to_database
from const import USER_FIELDS, BANK_FIELDS, ACCOUNT_FIELDS, DISCOUNTS, MIN_USERS, MAX_USERS

logging.basicConfig(filename='file.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')


def split_user_full_name(user_full_name):
    """
    Splits a user's full name into first name and surname.

    :param user_full_name: The full name of the user, containing both first name and surname.
    :return: The first name and surname as separate strings.
    """
    name, surname = re.split(r'\W+', user_full_name)
    logging.info('Full name (%s) has been successfully split into name: %s and surname: %s.',
                 user_full_name, name, surname)
    return name, surname


def split_full_name_in_dict(*user_data_dicts):
    """
    Splits the full name in each dictionary into first name and surname.

    :param user_data_dicts: Dictionaries containing user data, including a 'user_full_name' key.
    :return: A list of new dictionaries with separate 'name' and 'surname' keys.
    """
    new_user_data_list = []
    for user_data in user_data_dicts:
        full_name = user_data.pop('user_full_name')
        name, surname = split_user_full_name(full_name)

        new_user_data = {'name': name, 'surname': surname}
        new_user_data.update(user_data)
        new_user_data_list.append(new_user_data)

    return new_user_data_list


@connect_to_database
def add_data(cursor, table_name, *args):
    """
    Adds data to a specified table in the database.

    :param cursor: The database cursor to execute the SQL command.
    :param table_name: The name of the table to add data to.
    :param args: Dictionaries containing the data to be added.
    """
    for data in args:
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'

        cursor.execute(query, tuple(data.values()))

        logging.info('%s data successfully added.', table_name)
        logging.debug('Inserted %s data: %s', table_name, data)


def get_data_from_csv(path, fields):
    """
    Retrieves data from a CSV file.

    :param path: The path to the CSV file containing data.
    :param fields: The fields to be included in the data.
    :return: A list of dictionaries representing the data from the CSV file.
    """
    with open(path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile, delimiter=';'))
        reader = list(filter(lambda row: all(field in row and row[field] for field in fields), reader))

    return reader


def add_users_from_csv(path):
    """
    Adds user data from a CSV file to the database.

    :param path: The path to the CSV file containing user data.
    """
    reader = get_data_from_csv(path, USER_FIELDS)
    for row in reader:
        name, surname = split_user_full_name(row['user_full_name'])
        user_data = {'name': name, 'surname': surname, 'birth_day': row['birth_day'],
                     'accounts': row['account_number']}
        add_data('Users', user_data)


def add_banks_from_csv(path):
    """
    Adds bank data from a CSV file to the database.

    :param path: The path to the CSV file containing bank data.
    """
    reader = get_data_from_csv(path, BANK_FIELDS)
    print(reader)
    for row in reader:
        bank_data = {'id': row['bank_id'], 'name': row['bank_name']}
        add_data('Banks', bank_data)


def add_accounts_from_csv(path):
    """
    Adds account data from a CSV file to the database.

    :param path: The path to the CSV file containing account data.
    """
    reader = get_data_from_csv(path, ACCOUNT_FIELDS)
    for row in reader:
        account_data = {'user_id': row['user_id'], 'type': row['type'], 'account_number': row['accounts'],
                        'bank_id': row['bank_id'], 'currency': row['currency'], 'amount': row['amount'],
                        'status': row['status']}
        add_data('Accounts', account_data)


def add_data_from_csv(path):
    """
    Adds data from a CSV file to the database.

    :param path: The path to the CSV file containing data.
    """
    add_users_from_csv(path)
    add_banks_from_csv(path)
    add_accounts_from_csv(path)

    logging.info('Data from csv successfully added.')


@connect_to_database
def modify_data(cursor, table_name, modified_id, new_data):
    """
    Modifies data in the specified table in the database.

    :param cursor: The database cursor to execute the SQL command.
    :param table_name: The name of the table to modify data in.
    :param modified_id: The ID to identify which data to modify.
    :param new_data: A dictionary containing the updated data.
    """
    set_clause = ', '.join(f'{key}=?' for key in new_data.keys())
    query = f'UPDATE {table_name} SET {set_clause} WHERE id=?'

    cursor.execute(query, tuple(new_data.values()) + (modified_id,))

    logging.info('%s data %s successfully changed.', table_name, modified_id)
    logging.debug('Modified data: %s', new_data)


@connect_to_database
def delete_from_db(cursor, deleted_id, name):
    """
    Deletes a user/bank/account from the database.

    :param cursor: The database cursor to execute the SQL command.
    :param deleted_id: The ID of the user to be deleted.
    :param name: The name of the table from which the information will be deleted.
    """
    cursor.execute(f"DELETE FROM {name} WHERE id IN ('id_1', 'id_2')", (deleted_id,))
    logging.info('%s data %s successfully deleted', name, deleted_id)


@connect_to_database
def get_balance(cursor, account_id, amount):
    """
    Retrieves the balance information for an account from the database.

    :param cursor: The database cursor to execute the SQL command.
    :param account_id: The ID of the account for which to get the balance.
    :return: A tuple containing (balance_amount, currency, bank_id)
              or raises an exception if the account is not found.
    """
    cursor.execute('SELECT amount, currency, bank_id FROM Accounts WHERE id = ?', (account_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        raise ValueError(f'Account with id {account_id} not found.')

    if user_data[0] < amount:
        raise ValueError('Insufficient balance.')

    balance_info = (user_data[0], user_data[1], user_data[2])

    logging.debug('Received information from account %s: %s', account_id, user_data)
    return balance_info


@connect_to_database
def update_balance(cursor, account_id, new_balance):
    """
    Updates the balance of an account in the database.

    :param cursor: The database cursor to execute the SQL command.
    :param account_id: The ID of the account for which to update the balance.
    :param new_balance: The new balance amount to set for the account.
    """
    cursor.execute('UPDATE Accounts SET amount = ? WHERE id = ?', (new_balance, account_id))
    logging.info('The balance for account %s has been successfully updated to %s.', account_id, new_balance)


@connect_to_database
def get_bank_name(cursor, bank_id):
    """
    Retrieves the name of a bank from the database.

    :param cursor: The database cursor to execute the SQL command.
    :param bank_id: The ID of the bank for which to retrieve the name.
    :return: The name of the bank if found, or None if not found.
    """
    cursor.execute('SELECT name FROM Banks WHERE Id = ?', (bank_id,))
    name = cursor.fetchone()
    bank_name = name[0] if name else None
    return bank_name


@connect_to_database
def insert_transaction(cursor, transaction_data):
    """
    Inserts a transaction record into the database.

    :param cursor: The database cursor to execute the SQL command.
    :param transaction_data: A tuple containing transaction data in the following format:
                             (sender_bank_id, sender_account_id, receiver_bank_id, receiver_account_id,
                             currency, amount)
    """
    cursor.execute('INSERT INTO Transactions (bank_sender_name, account_sender_id, bank_receiver_name, '
                   'account_receiver_id, sent_currency, sent_amount, datetime) VALUES (?, ?, ?, ?, ?, ?, '
                   'datetime("now"))', (get_bank_name(transaction_data[0]), transaction_data[1],
                                        get_bank_name(transaction_data[2]), transaction_data[3],
                                        transaction_data[4], transaction_data[5]))

    logging.debug('Inserted transaction data: %s', transaction_data)


def get_exchange_rate(currency):
    """
    Retrieves the exchange rate for a given currency.

    :param currency: The currency to get the exchange rate for.
    :return: The exchange rate for the given currency.
    """
    load_dotenv()
    client = freecurrencyapi.Client(os.getenv("API_KEY"))
    exchange_rates = client.latest()

    logging.debug(client.status())
    logging.debug('Exchange rates: %s', exchange_rates)

    return exchange_rates['data'][currency]


def perform_currency_conversion(sender_currency, receiver_currency, amount):
    """
    Performs a currency conversion.

    :param sender_currency: The currency of the sender.
    :param receiver_currency: The currency of the receiver.
    :param amount: The amount to convert.
    :return: The converted amount.
    """
    sender_exchange_rate = get_exchange_rate(sender_currency)
    receiver_exchange_rate = get_exchange_rate(receiver_currency)

    return amount * receiver_exchange_rate / sender_exchange_rate if sender_currency != receiver_currency else amount


def update_balances(sender, receiver, sender_amount, receiver_amount):
    """
    Updates the balances of the sender and receiver.

    :param sender: A dictionary containing the sender's account details.
    :param receiver: A dictionary containing the receiver's account details.
    :param sender_amount: The amount sent by the sender.
    :param receiver_amount: The amount received by the receiver.
    """
    new_sender_balance = sender['balance'] - sender_amount
    new_receiver_balance = receiver['balance'] + receiver_amount

    logging.debug('New sender balance: %s, new receiver balance: %s', new_sender_balance,
                  new_receiver_balance)

    update_balance(sender['id'], new_sender_balance)
    update_balance(receiver['id'], new_receiver_balance)


def perform_transfer(sender_id, receiver_id, amount_in_sender_currency):
    """
    Performs a transfer of funds between two accounts.

    :param sender_id: The ID of the sender's account.
    :param receiver_id: The ID of the receiver's account.
    :param amount_in_sender_currency: The amount to transfer.
    """
    try:
        sender_balance, sender_currency, sender_bank_id = get_balance(sender_id, amount_in_sender_currency)
        receiver_balance, receiver_currency, receiver_bank_id = get_balance(receiver_id, amount_in_sender_currency)
    except ValueError as error:
        logging.error(str(error))
        return

    logging.debug('Sender: id - %s, bank - %s, balance - %s, currency - %s', sender_id, sender_bank_id,
                  sender_balance, sender_currency)
    logging.debug('Receiver: id - %s, bank - %s, balance - %s, currency - %s', receiver_id, receiver_bank_id,
                  receiver_balance, receiver_currency)
    logging.info('Transaction has been successfully completed.')

    sender = {'id': sender_id, 'balance': sender_balance, 'currency': sender_currency, 'bank_id': sender_bank_id}
    receiver = {'id': receiver_id, 'balance': receiver_balance, 'currency': receiver_currency,
                'bank_id': receiver_bank_id}

    amount_in_receiver_currency = perform_currency_conversion(sender['currency'], receiver['currency'],
                                                              amount_in_sender_currency)
    update_balances(sender, receiver, amount_in_sender_currency, amount_in_receiver_currency)
    insert_transaction((sender['bank_id'], sender['id'], receiver['bank_id'], receiver['id'], sender['currency'],
                        amount_in_sender_currency))


@connect_to_database
def get_data_from_db(cursor, table_name):
    """
    Retrieves data from a specified table in the database.

    :param cursor: The database cursor to execute the SQL command.
    :param table_name: The name of the table to retrieve data from.
    :return: A list of dictionaries representing the data from the table.
    """
    cursor.execute(f'SELECT * FROM {table_name}')
    columns = [column[0] for column in cursor.description]
    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return data


@connect_to_database
def get_users_ids(cursor):
    """
    Retrieves a list of user IDs from the database.

    :param cursor: The database cursor to execute the SQL command.
    :return: A list of user IDs.
    """
    cursor.execute('SELECT user_id FROM Accounts')
    return [i[0] for i in cursor.fetchall()]


@connect_to_database
def get_transactions_for_user(cursor, user_id):
    """
    Retrieves all transactions for a specific user.

    :param cursor: The database cursor to execute the SQL command.
    :param user_id: The ID of the user to retrieve transactions for.
    :return: A list of all transactions for the user.
    """
    cursor.execute('SELECT * FROM Transactions WHERE account_sender_id = ? OR account_receiver_id = ?',
                   (user_id, user_id))
    columns = [column[0] for column in cursor.description]
    transactions = [dict(zip(columns, row)) for row in cursor.fetchall()]
    transactions = convert_transactions_datetime(transactions)

    return transactions


def get_discount_for_random_users():
    """
    Generates random discounts for a random selection of users.

    :return: A dictionary where the keys are user IDs and the values are the corresponding discounts.
    """
    random_users_count = randint(MIN_USERS, min(len(get_users_ids()), MAX_USERS))
    users_with_discounts = {user_id: choice(DISCOUNTS) for user_id in sample(get_users_ids(), random_users_count)}
    logging.info('Users with discounts: %s.', users_with_discounts)
    return users_with_discounts


@connect_to_database
def get_users_with_debts(cursor):
    """
    Retrieves a list of users with negative account balances.

    :param cursor: The database cursor to execute the SQL command.
    :return: A list of tuples containing usernames and surnames for users with negative account balances.
    """
    cursor.execute('SELECT user_id FROM Accounts WHERE amount < 0')
    user_name = []
    for i in cursor.fetchall():
        cursor.execute('SELECT name, surname  AS full_name FROM Users WHERE id = ?', (i[0],))
        user_name.extend(cursor.fetchall())
    logging.debug('User names with debts: %s.', user_name)  # concat()
    return user_name


def get_full_names_of_users_with_debts():
    """
    Retrieves the full names of users with negative account balances.

    :return: A list of full names (name + surname) for users with negative account balances.
    """
    full_names = []
    for name, surname in get_users_with_debts():
        full_names.append(name + ' ' + surname)
    logging.info('Users with debts: %s', full_names)
    return full_names


def get_bank_with_biggest_capital():
    """
    Retrieves the bank with the biggest capital based on the sum of account balances.

    :return: The name of the bank with the biggest capital or None if no banks are found.
    """
    accounts = get_data_from_db('Accounts')
    banks = {}
    for account in accounts:
        if account['bank_id'] not in banks:
            banks[account['bank_id']] = 0
        banks[account['bank_id']] += account['amount']

    bank_with_biggest_capital = max(banks, key=banks.get)
    return bank_with_biggest_capital


def get_bank_serving_oldest_client():
    """
    Retrieves the bank serving the oldest client based on the client's birthdate.

    :return: The name of the bank serving the oldest client or None if no banks are found.
    """
    users = get_data_from_db('Users')
    accounts = get_data_from_db('Accounts')

    oldest_user = min(users, key=lambda user: user['birth_day'])
    account_of_oldest_user = next(account for account in accounts if account['user_id'] == oldest_user['id'])
    bank_serving_oldest_client = account_of_oldest_user['bank_id']

    return bank_serving_oldest_client


def get_bank_with_most_unique_outbound_transactions():
    """
    Retrieves the bank with the highest number of unique users who performed outbound transactions.

    :return: The name of the bank with the most unique users performing outbound transactions or None if no banks
    are found.
    """
    transactions = get_data_from_db('Transactions')
    banks = {}
    for transaction in transactions:
        if transaction['bank_sender_name'] not in banks:
            banks[transaction['bank_sender_name']] = set()
        banks[transaction['bank_sender_name']].add(transaction['account_sender_id'])

    bank_with_most_unique_users = max(banks, key=lambda bank: len(banks[bank]))
    return bank_with_most_unique_users


def delete_row(data_to_delete, del_user):
    """
    Deletes either user or account rows based on the input data.

    :param data_to_delete: A list of user IDs or account IDs to be deleted.
    :param del_user: If True, delete user rows; if False, delete account rows.
    """
    [delete_from_db(i, del_user) for i in data_to_delete]
    logging.debug('Deleted data: %s', data_to_delete)


def delete_users_and_accounts_with_missing_info():
    """
    Deletes users and accounts with missing information (NULL values).
    """
    users = get_data_from_db('Users')
    accounts = get_data_from_db('Accounts')
    users_to_delete = [user for user in users if None in user.values()]
    accounts_to_delete = [account for account in accounts if None in account.values()]

    [delete_row(user['id'], 'User') for user in users_to_delete]
    [delete_row(account['id'], 'Accounts') for account in accounts_to_delete]

    logging.info('Users and accounts data without all information has been successfully deleted.')


def convert_transactions_datetime(transactions):
    """
    Converts the datetime strings in a list of transactions to datetime objects.

    :param transactions: A list of transactions.
    :return: The same list of transactions, but with datetime strings replaced by datetime objects.
    """
    return [{**transaction, 'datetime': datetime.strptime(transaction['datetime'], '%Y-%m-%d %H:%M:%S')}
            for transaction in transactions]


def filter_transactions_past_3_months(user_id):
    """
    Filters transactions for the past 3 months.

    :param user_id: The ID of the user whose transactions to filter.
    :return: A list of transactions for the user in the past 3 months.
    """
    transactions = get_transactions_for_user(user_id)

    three_months_ago = datetime.now() - timedelta(days=90)
    filtered_transactions = [transaction for transaction in transactions if transaction['datetime'] >= three_months_ago]

    return filtered_transactions
