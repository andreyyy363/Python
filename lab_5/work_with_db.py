import csv
import re
import random
import logging
from datetime import datetime, timedelta
import freecurrencyapi
from connect_to_db import connect_to_database


API_KEY = 'fca_live_T6dRB6eXL7imXrxOpBdiZiUTaXjnzigIAeLL4cDi'
logging.basicConfig(filename='file.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')


def split_user_full_name(user_full_name):
    """
    Split a user's full name into first name and surname.

    :param user_full_name: The full name of the user containing both first name and surname.
    :return name, surname: The first name and surname as separate strings.
    """
    name, surname = re.split(r'\W+', user_full_name)
    logging.info(f'Full name ({user_full_name}) has been successfully split into name: {name} and surname: {surname}.')
    return name, surname


def insert_user_info(cursor, name, surname, birth_day, accounts):
    """
    Insert user information into the database.

    :param cursor: The database cursor to execute the SQL command.
    :param name: The user's name.
    :param surname: The user's surname.
    :param birth_day: The user's birthday.
    :param accounts: The number of accounts associated with the user.
    """
    cursor.execute('INSERT INTO User (name, surname, birth_day, accounts) VALUES (?, ?, ?, ?)',
                   (name, surname, birth_day, accounts))
    logging.debug(f'User data: {name, surname, birth_day, accounts}')


@connect_to_database
def add_user(cursor, *args):
    """
    Add user information to the database.

    :param cursor: The database cursor to execute the SQL command.
    :param args: Variable number of arguments, each containing user info in either a dictionary or a tuple format.
    """
    for i in args:
        if isinstance(i, dict):
            name, surname = split_user_full_name(i.get('user_full_name'))
            insert_user_info(cursor, name, surname, i.get('birth_day'), i.get('accounts'))

        elif isinstance(i, tuple) and len(i) == 3:
            name, surname = split_user_full_name(i[0])
            insert_user_info(cursor, name, surname, i[1], i[2])

    logging.info('User data successfully added.')


def insert_bank_name(cursor, bank_name):
    """
    Insert bank name into the database.

    :param cursor: The database cursor to execute the SQL command.
    :param bank_name: The name of the bank.
    """
    cursor.execute('INSERT INTO Bank (name) VALUES (?)', (bank_name,))
    logging.debug(f'Inserted bank name: {bank_name}')


@connect_to_database
def add_bank(cursor, *args):
    """
    Add bank information to the database.

    :param cursor: The database cursor to execute the SQL command.
    :param args: Variable number of arguments, each containing bank information.
    """
    for i in args:
        if isinstance(i, dict):
            insert_bank_name(cursor, i.get('name'))

        elif isinstance(i, str):
            insert_bank_name(cursor, i)

    logging.info('Bank data successfully added.')


def insert_account_info(cursor, account_data):
    """
    Insert account information into the database.

    :param cursor: The database cursor to execute the SQL command.
    :param account_data: A tuple containing account information.
    """
    cursor.execute('INSERT INTO Account (User_id, Type, Account_Number, Bank_id, Currency, Amount, Status) '
                   'VALUES (?, ?, ?, ?, ?, ?, ?)', account_data)
    logging.debug(f'Inserted account data: {account_data}')


@connect_to_database
def add_account(cursor, *args):
    """
    Add account information to the database.

    :param cursor: The database cursor to execute the SQL command.
    :param args: Variable number of arguments, each containing account information.
    """
    for i in args:
        if isinstance(i, dict):
            account_data = (i.get('user_id'), i.get('type'), i.get('account_number'), i.get('bank_id'),
                            i.get('currency'), i.get('amount'), i.get('status'))

            insert_account_info(cursor, account_data)

        elif isinstance(i, tuple) and len(i) == 7:
            insert_account_info(cursor, i)

    logging.info('Account data successfully added.')


def add_data_from_csv(path):
    """
    Add data from a CSV file to the database.

    :param path: The path to the CSV file containing data.
    """
    with open(path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for i in reader:
            user_id = i.get('user_id')
            birth_day = i.get('birth_day')
            accounts = i.get('account_number')
            bank_id = i.get('bank_id')
            bank_name = i.get('bank_name')

            account_type = i.get('type')
            account_number = i.get('account_number')
            currency = i.get('currency')
            amount = i.get('amount')
            status = i.get('status')

            add_user((i.get('user_full_name'), birth_day, accounts))
            add_bank(bank_name)
            add_account((user_id, account_type, account_number, bank_id, currency, amount, status))

    logging.info('All data from CSV file was successfully added.')


def logging_modified_data(name, modified_id, modified_data):
    """
    Log the modification of data with relevant information.

    :param name: The name of the entity making the data modification.
    :param modified_id: The identifier for the user whose data has been modified.
    :param modified_data: The modified data.
    """
    logging.info(f'{name} data {modified_id} successfully changed.')
    logging.debug(f'Modified data: {modified_data}')


@connect_to_database
def modify_user(cursor, user_id, new_data):
    """
    Modify user information in the database.

    :param cursor: The database cursor to execute the SQL command.
    :param user_id: The user's ID to identify which user's data to modify.
    :param new_data: A dictionary containing the updated user data.
    """
    cursor.execute('UPDATE User SET name=?, surname=?, birth_day=?, accounts=? WHERE id=?',
                   (new_data['name'], new_data['surname'], new_data['birth_day'], new_data['accounts'], user_id))
    logging_modified_data('User', user_id, new_data)


@connect_to_database
def modify_bank(cursor, bank_id, new_data):
    """
    Modify bank information in the database.

    :param cursor: The database cursor to execute the SQL command.
    :param bank_id: The bank's ID to identify which bank's data to modify.
    :param new_data: A dictionary containing the updated bank data.
    """
    cursor.execute('UPDATE Bank SET name=? WHERE id=?', (new_data['bank_name'], bank_id))
    logging_modified_data('Bank', bank_id, new_data)


@connect_to_database
def modify_account(cursor, account_id, new_data):
    """
    Modify account information in the database.

    :param cursor: The database cursor to execute the SQL command.
    :param account_id: The account's ID to identify which account's data to modify.
    :param new_data: A dictionary containing the updated account data.
    """
    cursor.execute('UPDATE Account SET user_id=?, type=?, account_number=?, bank_id=?, currency=?, amount=?, status=? '
                   'WHERE Id=?',
                   (new_data['user_id'], new_data['type'], new_data['account_number'], new_data['bank_id'],
                    new_data['currency'], new_data['amount'], new_data['status'], account_id))
    logging_modified_data('Account', account_id, new_data)


def logging_deleted_id(name, deleted_id):
    """
    Log the deletion of data with relevant information.

    :param name: The name of the entity that has been deleted.
    :param deleted_id: The ID of the deleted entity.

    """
    logging.info(f'{name} data {deleted_id} successfully deleted')


@connect_to_database
def delete_user(cursor, user_id):
    """
    Delete a user from the database.

    :param cursor: The database cursor to execute the SQL command.
    :param user_id: The ID of the user to be deleted.
    """
    cursor.execute('DELETE FROM User WHERE id = ?', (user_id,))
    logging_deleted_id('User', user_id)


@connect_to_database
def delete_bank(cursor, bank_id):
    """
    Delete a bank record from the database.

    :param cursor: The database cursor to execute the SQL command.
    :param bank_id: The ID of the bank to be deleted.
    """
    cursor.execute('DELETE FROM Bank WHERE id = ?', (bank_id,))
    logging_deleted_id('Bank', bank_id)


@connect_to_database
def delete_account(cursor, account_id):
    """
    Delete an account record from the database.

    :param cursor: The database cursor to execute the SQL command.
    :param account_id: The ID of the account to be deleted.
    """
    cursor.execute('DELETE FROM Account WHERE id = ?', (account_id,))
    logging_deleted_id('Account', account_id)


@connect_to_database
def get_balance(cursor, account_id):
    """
    Get the balance information for an account from the database.

    :param cursor: The database cursor to execute the SQL command.
    :param account_id: The ID of the account for which to get the balance.
    :return balance_info: A tuple containing (balance_amount, currency, bank_id)
                          or (None, None, None) if the account is not found.
    """
    cursor.execute('SELECT amount, currency, bank_id FROM Account WHERE id = ?', (account_id,))
    user_data = cursor.fetchone()
    balance_info = (user_data[0], user_data[1], user_data[2]) if user_data else (None, None, None)
    logging.debug(f'Received information from account {account_id}: {user_data}')
    return balance_info


@connect_to_database
def update_balance(cursor, account_id, new_balance):
    """
    Update the balance of an account in the database.

    :param cursor: The database cursor to execute the SQL command.
    :param account_id: The ID of the account for which to update the balance.
    :param new_balance: The new balance amount to set for the account.
    """
    cursor.execute('UPDATE Account SET amount = ? WHERE id = ?', (new_balance, account_id))
    logging.info(f'The balance for account {account_id} has been successfully updated to {new_balance}.')


@connect_to_database
def get_bank_name(cursor, bank_id):
    """
    Get the name of a bank from the database.

    :param cursor: The database cursor to execute the SQL command.
    :param bank_id: The ID of the bank for which to retrieve the name.
    :return bank_name: The name of the bank if found, or None if not found.
    """
    cursor.execute('SELECT name FROM Bank WHERE Id = ?', (bank_id,))
    name = cursor.fetchone()
    bank_name = name[0] if name else None
    return bank_name


@connect_to_database
def insert_transaction(cursor, transaction_data):
    """
    Insert a transaction record into the database.

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
    logging.debug(f'Inserted transaction data: {transaction_data}')


def perform_transfer(sender_id, receiver_id, amount):
    """
    Perform a transfer of funds between two accounts.

    :param sender_id: The ID of the sender's account.
    :param receiver_id: The ID of the receiver's account.
    :param amount: The amount to transfer.
    """
    sender_balance, sender_currency, sender_bank_id = get_balance(sender_id)
    receiver_balance, receiver_currency, receiver_bank_id = get_balance(receiver_id)

    logging.debug(f'Sender: id - {sender_id}, bank - {sender_bank_id}, '
                  f'balance - {sender_balance}, currency - {sender_currency}')

    logging.debug(f'Receiver: id - {receiver_id}, bank - {receiver_bank_id}, '
                  f'balance - {receiver_balance}, currency - {receiver_currency}')

    if sender_balance is None or receiver_balance is None:
        logging.info('Account not found.')
        return

    if sender_balance < amount:
        logging.info('Insufficient balance.')
        return

    if sender_currency != receiver_currency:
        client = freecurrencyapi.Client(API_KEY)
        exchange_rates = client.latest()

        logging.debug(client.status())
        logging.debug(f'Exchange rates: {exchange_rates}')

        if sender_currency in exchange_rates['data'] and receiver_currency in exchange_rates['data']:
            exchange_rate = exchange_rates['data'][receiver_currency] / exchange_rates['data'][sender_currency]
            amount_in_receiver_currency = amount * exchange_rate
        else:
            logging.info('Currency conversion not available.')
            return
    else:
        amount_in_receiver_currency = amount

    new_sender_balance = sender_balance - amount
    new_receiver_balance = receiver_balance + amount_in_receiver_currency

    logging.debug(f'New sender balance: {new_sender_balance}, new receiver balance: {new_receiver_balance}')

    update_balance(sender_id, new_sender_balance)
    update_balance(receiver_id, new_receiver_balance)
    insert_transaction((sender_bank_id, sender_id, receiver_bank_id, receiver_id, sender_currency, amount))

    logging.info('Transaction has been successfully completed.')


@connect_to_database
def get_users_ids(cursor):
    """
    Get a list of user IDs from the database.

    :param cursor: The database cursor to execute the SQL command.
    :return list[int]: A list of user IDs.
    """
    cursor.execute('SELECT user_id FROM Account')
    return [i[0] for i in cursor.fetchall()]


def get_discount_for_random_users():
    """
    Generate random discounts for a random selection of users.

    :return users_with_discounts: Generate random discounts for a random selection of users.
    """
    users_with_discounts = {user_id: random.choice((25, 30, 50))
                            for user_id in random.sample(get_users_ids(), random.randint(1,
                                                         min(len(get_users_ids()), 10)))}
    logging.info(f'Users with discounts: {users_with_discounts}.')
    return users_with_discounts


@connect_to_database
def get_users_with_debts(cursor):
    """
    Get a list of users with negative account balances.

    :param cursor: The database cursor to execute the SQL command.
    :return user_name: A list of tuples containing usernames and surnames for users with negative account balances.
    """
    cursor.execute('SELECT user_id FROM Account WHERE amount < 0')
    user_name = []
    for i in cursor.fetchall():
        cursor.execute('SELECT name, surname FROM User WHERE id = ?', (i[0],))
        user_name = cursor.fetchall()
    logging.debug(f'User names with debts: {user_name}.')
    return user_name


def get_full_names_of_users_with_debts():
    """
    Get the full names of users with negative account balances.

    :return full_names: A list of full names (name + surname) for users with negative account balances.
    """
    full_names = []
    for name, surname in get_users_with_debts():
        full_names.append(name + ' ' + surname)
    logging.info(f'Users with debts: {full_names}')
    return full_names


@connect_to_database
def get_bank_with_biggest_capital(cursor):
    """
    Get the bank with the biggest capital based on the sum of account balances.

    :param cursor: The database cursor to execute the SQL command.
    :return bank_with_biggest_capital: The name of the bank with the biggest capital or None if no banks are found.
    """
    cursor.execute('''SELECT b.name FROM Bank b JOIN Account a ON b.id = a.bank_id GROUP BY b.id 
                        ORDER BY SUM(a.amount) DESC LIMIT 1''')

    bank_with_biggest_capital = cursor.fetchone()[0]
    logging.info(f'Bank which operates the biggest capital: {bank_with_biggest_capital}.')
    return bank_with_biggest_capital if bank_with_biggest_capital else None


@connect_to_database
def get_bank_serving_oldest_client(cursor):
    """
    Get the bank serving the oldest client based on the client's birthdate.

    :param cursor: The database cursor to execute the SQL command.
    :return bank_serving_oldest_client: The name of the bank serving the oldest client or None if no banks are found.
    """
    cursor.execute('''SELECT b.name FROM Bank b JOIN Account a ON b.id = a.bank_id JOIN User u ON a.user_id = u.id
                        ORDER BY u.birth_day ASC LIMIT 1''')

    bank_serving_oldest_client = cursor.fetchone()[0]
    logging.info(f'Bank which serves the oldest client: {bank_serving_oldest_client}')
    return bank_serving_oldest_client if bank_serving_oldest_client else None


@connect_to_database
def get_bank_with_most_unique_outbound_transactions(cursor):
    """
    Get the bank with the highest number of unique users who performed outbound transactions.

    :param cursor: The database cursor to execute the SQL command.
    :return bank_with_most_unique_users: The name of the bank with the unique users performing
                                         outbound transactions or None if no banks are found.
    """
    cursor.execute('''SELECT b.name FROM Bank b JOIN Account a ON b.Id = a.bank_id 
                        JOIN Transactions t ON a.Id = t.account_sender_id WHERE t.bank_sender_name = b.name 
                        GROUP BY b.id ORDER BY COUNT(DISTINCT a.user_id) DESC LIMIT 1''')

    bank_with_most_unique_users = cursor.fetchone()[0]
    logging.info(f'Bank with the highest number of unique users which performed outbound transactions: '
                 f'{bank_with_most_unique_users}')
    return bank_with_most_unique_users if bank_with_most_unique_users else None


def delete_user_or_account_row(data_to_delete, del_user):
    """
    Delete either user or account rows based on the input data.

    :param data_to_delete: A list of user IDs or account IDs to be deleted.
    :param del_user: If True, delete user rows; if False, delete account rows.
    """
    for i in data_to_delete:
        delete_user(i) if del_user else delete_account(i)
    logging.debug(f'Deleted data: {data_to_delete}')


@connect_to_database
def delete_users_and_accounts_with_missing_info(cursor):
    """
    Delete users and accounts with missing information (NULL values) from the database.

    :param cursor: The database cursor to execute the SQL commands.
    """
    cursor.execute('''SELECT id FROM User WHERE name IS NULL OR surname IS NULL OR birth_day IS NULL''')
    delete_user_or_account_row([i[0] for i in cursor.fetchall()], True)

    cursor.execute('''SELECT id FROM Account WHERE user_id IS NULL OR type IS NULL OR account_Number IS NULL 
                        OR bank_id IS NULL OR currency IS NULL OR amount IS NULL OR status IS NULL ''')
    delete_user_or_account_row([i[0] for i in cursor.fetchall()], False)

    logging.info('Users data without all information has been successfully deleted.')


@connect_to_database
def search_transactions_for_user_past_3_months(cursor, user_id):
    """
    Search for transactions of a user for the past 3 months.

    :param cursor: The database cursor to execute the SQL command.
    :param user_id: The ID of the user to search for transactions.
    :return transactions: A list of transactions for the user in the past 3 months.
    """
    cursor.execute('''SELECT * FROM Transactions WHERE account_sender_id OR account_receiver_id = ? 
    AND datetime >= ?''', (user_id, datetime.now() - timedelta(days=90)))
    transactions = cursor.fetchall()
    logging.info(f'Transactions of user {user_id} for past 3 months: {transactions}.')
    return transactions
