from random import randint, sample, choice
import logging
from datetime import datetime, timedelta
import os
from csv import DictReader
from collections import defaultdict
from freecurrencyapi import Client
from dotenv import load_dotenv
from connect_to_db import connect_to_database
from const import (DISCOUNTS, MIN_USERS, MAX_USERS, REQUIRED_FIELDS, DB_USER_FIELDS, FORMAT, DATETIME, NAME, SURNAME,
                   FULL_NAME, USERS_TABLE, ACCOUNTS_TABLE, TRANSACTIONS_TABLE, DATA, BALANCE, AMOUNT, ID, CURRENCY,
                   BANK_ID, BIRTH_DAY, USER_ID)
from validations import validate_user_name, validate_balance


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('file.log')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()
client = Client(os.getenv('API_KEY'))


# Remove
def split_user_full_name(user_data):
    """
    Splits a user's full name into first name and surname.

    :param user_full_name: The full name of the user, containing both first name and surname.
    :return: The first name and surname as separate strings.
    """
    name, surname = validate_user_name(user_data.pop(FULL_NAME))
    user_data.update({NAME: name, SURNAME: surname})
    return user_data


def split_full_name_in_dict(*args):
    """
    Splits the full name in each dictionary into first name and surname.

    :param args: Dictionaries containing user data, including a 'user_full_name' key.
    :return: A list of new dictionaries with separate 'name' and 'surname' keys.
    """
    logger.info('Full name has been successfully split!')
    return list(map(split_user_full_name, (args[0] if len(args) == 1 and isinstance(args[0], list) else list(args))))


@connect_to_database
def add_data(cursor, table_name, fields, *args):
    """
    Adds data to a specified table in the database.

    :param cursor: The database cursor to execute the SQL command.
    :param table_name: The name of the table to add data to.
    :param args: Dictionaries containing the data to be added.
    """
    data_list = (args[0] if len(args) == 1 and isinstance(args[0], list) else list(args))

    query = f'INSERT INTO {table_name} ({", ".join(fields)}) VALUES ({', '.join(':' + field for field in fields)})'
    cursor.executemany(query, data_list)

    logging.info('%s data successfully added.', table_name)
    logging.debug('Inserted %s data: %s', table_name, data_list)


def get_data_from_csv(path, fields):
    """
    Retrieves data from a CSV file.

    :param path: The path to the CSV file containing data.
    :param fields: The fields to be included in the data.
    :return: A list of dictionaries representing the data from the CSV file.
    """
    with open(path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = DictReader(csvfile, delimiter=';')
        return [{field: row[field] for field in fields} for row in reader if
                all(row.get(field) for field in REQUIRED_FIELDS)]


def add_table_data_from_csv(path, table_name, fields):
    """
    Adds user data from a CSV file to the database.

    :param path: The path to the CSV file containing user data.
    """
    data = get_data_from_csv(path, fields)
    if table_name == USERS_TABLE:
        data = split_full_name_in_dict(data)
        fields = DB_USER_FIELDS

    add_data(table_name, fields, data)
    logger.info('Data from csv successfully added.')


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

    cursor.execute(query, (*new_data.values(), modified_id))

    logger.info('%s data %s successfully changed.', table_name, modified_id)
    logger.debug('Modified data: %s', new_data)


@connect_to_database
def delete_from_db(cursor, deleted_id, table_name):
    """
    Deletes a user/bank/account from the database.

    :param cursor: The database cursor to execute the SQL command.
    :param deleted_id: The ID of the user to be deleted.
    :param table_name: The name of the table from which the information will be deleted.
    """
    cursor.execute(f"DELETE FROM {table_name} WHERE id IN ('id_1', 'id_2')", (deleted_id,))
    logger.info('%s data %s successfully deleted', table_name, deleted_id)


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

    validate_balance(user_data, account_id, amount)

    logger.debug('Received information from account %s: %s', account_id, user_data)
    return user_data


@connect_to_database
def get_bank_name(cursor, bank_id):
    """
    Retrieves the name of a bank from the database.

    :param cursor: The database cursor to execute the SQL command.
    :param bank_id: The ID of the bank for which to retrieve the name.
    :return: The name of the bank if found, or None if not found.
    """
    cursor.execute('SELECT bank_name FROM Banks WHERE bank_id = ?', (bank_id,))
    name = cursor.fetchone()

    return name[0] if name else None


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

    logger.debug('Inserted transaction data: %s', transaction_data)


def perform_currency_conversion(sender_currency, receiver_currency, amount):
    """
    Performs a currency conversion.

    :param sender_currency: The currency of the sender.
    :param receiver_currency: The currency of the receiver.
    :param amount: The amount to convert.
    :return: The converted amount.
    """

    exchange_rates = client.latest(sender_currency, [receiver_currency])[DATA][receiver_currency]

    logger.debug(client.status())
    logger.debug('Exchange rates: %s', exchange_rates)

    return amount * exchange_rates


def update_balances(sender, receiver, sender_amount, receiver_amount):
    """
    Updates the balances of the sender and receiver.

    :param sender: A dictionary containing the sender's account details.
    :param receiver: A dictionary containing the receiver's account details.
    :param sender_amount: The amount sent by the sender.
    :param receiver_amount: The amount received by the receiver.
    """
    new_sender_balance = sender[BALANCE] - sender_amount
    new_receiver_balance = receiver[BALANCE] + receiver_amount

    logger.debug('New sender balance: %s, new receiver balance: %s', new_sender_balance,
                 new_receiver_balance)

    modify_data(ACCOUNTS_TABLE, sender[ID], {AMOUNT: new_sender_balance})
    modify_data(ACCOUNTS_TABLE, receiver[ID], {AMOUNT: new_receiver_balance})


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
        logger.error(str(error))
        return

    logger.debug('Sender: id - %s, bank - %s, balance - %s, currency - %s', sender_id, sender_bank_id,
                 sender_balance, sender_currency)
    logger.debug('Receiver: id - %s, bank - %s, balance - %s, currency - %s', receiver_id, receiver_bank_id,
                 receiver_balance, receiver_currency)
    logger.info('Transaction has been successfully completed.')

    sender = {ID: sender_id, BALANCE: sender_balance, CURRENCY: sender_currency, BANK_ID: sender_bank_id}
    receiver = {ID: receiver_id, BALANCE: receiver_balance, CURRENCY: receiver_currency, BANK_ID: receiver_bank_id}

    amount_in_receiver_currency = perform_currency_conversion(sender_currency, receiver_currency,
                                                              amount_in_sender_currency)
    update_balances(sender, receiver, amount_in_sender_currency, amount_in_receiver_currency)
    insert_transaction((sender_bank_id, sender_id, receiver_bank_id, receiver_id, sender_currency,
                        amount_in_sender_currency))


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
def get_data_from_db(cursor, table_name, user_id=None):
    """
    Retrieves data from a specified table in the database.

    :param cursor: The database cursor to execute the SQL command.
    :param table_name: The name of the table to retrieve data from.
    :return: A list of dictionaries representing the data from the table.
    """
    extra_query = f'WHERE account_sender_id = {user_id} OR account_receiver_id = {user_id}'
    cursor.execute(f'SELECT * FROM {table_name} {extra_query if user_id is not None else ""}')
    columns = [column[0] for column in cursor.description]

    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@connect_to_database
def get_transactions_for_user(cursor, user_id):
    """
    Retrieves all transactions for a specific user.

    :param cursor: The database cursor to execute the SQL command.
    :param user_id: The ID of the user to retrieve transactions for.
    :return: A list of all transactions for the user.
    """
    return convert_transactions_datetime(get_data_from_db(TRANSACTIONS_TABLE, user_id))


def get_discount_for_random_users():
    """
    Generates random discounts for a random selection of users.

    :return: A dictionary where the keys are user IDs and the values are the corresponding discounts.
    """
    random_users_count = randint(MIN_USERS, min(len(get_users_ids()), MAX_USERS))
    users_with_discounts = {user_id: choice(DISCOUNTS) for user_id in sample(get_users_ids(), random_users_count)}
    logger.info('Users with discounts: %s.', users_with_discounts)
    return users_with_discounts


@connect_to_database
def get_users_with_debts(cursor):
    """
    Retrieves a list of users with negative account balances.

    :param cursor: The database cursor to execute the SQL command.
    :return: A list of tuples containing usernames and surnames for users with negative account balances.
    """
    cursor.execute('SELECT user_id FROM Accounts WHERE amount < 0')

    user_name = [(row[0], row[1]) for i in cursor.fetchall() for row in
                 cursor.execute('SELECT name, surname AS full_name FROM Users WHERE id = ?', (i[0],))]

    logger.debug('User names with debts: %s.', user_name)  # concat()

    return user_name


def get_full_names_of_users_with_debts():
    """
    Retrieves the full names of users with negative account balances.

    :return: A list of full names (name + surname) for users with negative account balances.
    """
    full_names = [f'{name} {surname}' for name, surname in get_users_with_debts()]

    logger.info('Users with debts: %s', full_names)
    return full_names


def get_bank_with_biggest_capital():
    """
    Retrieves the bank with the biggest capital based on the sum of account balances.

    :return: The name of the bank with the biggest capital or None if no banks are found.
    """
    accounts = get_data_from_db(ACCOUNTS_TABLE)
    banks = {account[BANK_ID]: account[AMOUNT] for account in accounts}

    return max(banks, key=banks.get)


def get_bank_serving_oldest_client():
    """
    Retrieves the bank serving the oldest client based on the client's birthdate.

    :return: The name of the bank serving the oldest client or None if no banks are found.
    """
    users = get_data_from_db(USERS_TABLE)
    accounts = get_data_from_db(ACCOUNTS_TABLE)
    oldest_user = min(users, key=lambda user: user[BIRTH_DAY])

    return next(account for account in accounts if account[USER_ID] == oldest_user[ID])[BANK_ID]


def get_bank_with_most_unique_outbound_transactions():
    """
    Retrieves the bank with the highest number of unique users who performed outbound transactions.

    :return: The name of the bank with the most unique users performing outbound transactions or None if no banks
    are found.
    """
    transactions = get_data_from_db(TRANSACTIONS_TABLE)
    banks = defaultdict(set)
    [banks[transaction['bank_sender_name']].add(transaction['account_sender_id']) for transaction in transactions]

    return max(banks, key=lambda bank: len(banks[bank]))


def delete_row(data_to_delete, del_user):
    """
    Deletes either user or account rows based on the input data.

    :param data_to_delete: A list of user IDs or account IDs to be deleted.
    :param del_user: If True, delete user rows; if False, delete account rows.
    """
    map(lambda i: delete_from_db(i, del_user), data_to_delete)
    logger.debug('Deleted data: %s', data_to_delete)


def delete_users_and_accounts_with_missing_info():
    """
    Deletes users and accounts with missing information (NULL values).
    """
    users = get_data_from_db(USERS_TABLE)
    accounts = get_data_from_db(ACCOUNTS_TABLE)

    users_to_delete = [user for user in users if None in user.values()]
    accounts_to_delete = [account for account in accounts if None in account.values()]

    map(lambda user: delete_row(user[ID], USERS_TABLE), users_to_delete)
    map(lambda account: delete_row(account[ID], ACCOUNTS_TABLE), accounts_to_delete)

    logger.info('Users and accounts data without all information has been successfully deleted.')


def convert_transactions_datetime(transactions):
    """
    Converts the datetime strings in a list of transactions to datetime objects.

    :param transactions: A list of transactions.
    :return: The same list of transactions, but with datetime strings replaced by datetime objects.
    """
    return [{**transaction, DATETIME: datetime.strptime(transaction[DATETIME], FORMAT)}
            for transaction in transactions]


def filter_transactions_past_3_months(user_id):
    """
    Filters transactions for the past 3 months.

    :param user_id: The ID of the user whose transactions to filter.
    :return: A list of transactions for the user in the past 3 months.
    """
    transactions = get_transactions_for_user(user_id)
    three_months_ago = datetime.now() - timedelta(days=90)

    return [transaction for transaction in transactions if transaction[DATETIME] >= three_months_ago]
