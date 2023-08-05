import sqlite3
import argparse


def set_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--uniqueness', action='store_true')
    args = parser.parse_args()
    return args.uniqueness


def create_tables(unique_fields):
    conn = sqlite3.connect('bank.db')

    # Table "Bank"
    conn.execute('''CREATE TABLE IF NOT EXISTS Bank (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )''')

    # Table "Transactions"
    conn.execute('''CREATE TABLE IF NOT EXISTS Transactions (
                    id INTEGER PRIMARY KEY,
                    bank_sender_name TEXT NOT NULL,
                    account_sender_id INTEGER NOT NULL,
                    bank_receiver_name TEXT NOT NULL,
                    account_receiver_id INTEGER NOT NULL,
                    sent_currency TEXT NOT NULL,
                    sent_amount REAL NOT NULL,
                    datetime TEXT
                )''')

    # Table "User"
    conn.execute('''CREATE TABLE IF NOT EXISTS User (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL {unique_name},
                    surname TEXT NOT NULL {unique_surname},
                    birth_day TEXT,
                    accounts TEXT NOT NULL
                )'''.format(unique_name='UNIQUE' if unique_fields else '',
                            unique_surname='UNIQUE' if unique_fields else ''))

    # Table "Account"
    conn.execute('''CREATE TABLE IF NOT EXISTS Account (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    account_Number INTEGER NOT NULL UNIQUE,
                    bank_id INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT
                )''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_tables(set_argparse())
