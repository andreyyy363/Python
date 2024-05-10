import sqlite3
import argparse


def set_argparse():
    """
    Parses command-line arguments to check if the 'uniqueness' flag is set.

    :return: (bool) True if the 'uniqueness' flag is set, False otherwise.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--uniqueness', action='store_true')
    args = parser.parse_args()
    return args.uniqueness


def create_tables(unique_fields):
    """
    Creates tables in the SQLite database 'bank.db'.
    The tables created are 'Bank', 'Transactions', 'User', and 'Account'.

    :param unique_fields: (bool) If True, the 'name' and 'surname' fields in the 'User' table will be unique.
    :return: None
    """
    conn = sqlite3.connect('bank.db')

    # Table "Bank"
    conn.execute('''CREATE TABLE IF NOT EXISTS Banks (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE)''')

    # Table "Transactions"
    conn.execute('''CREATE TABLE IF NOT EXISTS Transactions (
                    id INTEGER PRIMARY KEY,
                    bank_sender_name TEXT NOT NULL,
                    account_sender_id INTEGER NOT NULL,
                    bank_receiver_name TEXT NOT NULL,
                    account_receiver_id INTEGER NOT NULL,
                    sent_currency TEXT NOT NULL,
                    sent_amount REAL NOT NULL,
                    datetime TEXT)''')

    # Table "User"
    unique = 'UNIQUE' if unique_fields else ''
    conn.execute(f'''CREATE TABLE IF NOT EXISTS Users (
                        id INTEGER PRIMARY KEY, 
                        name TEXT NOT NULL {unique}, 
                        surname TEXT NOT NULL {unique}, 
                        birth_day TEXT, 
                        accounts TEXT NOT NULL)''')

    # Table "Account"
    conn.execute('''CREATE TABLE IF NOT EXISTS Accounts (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    account_number INTEGER NOT NULL UNIQUE,
                    bank_id INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT)''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_tables(set_argparse())
