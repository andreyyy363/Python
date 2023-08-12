import csv
import re
import random
from connect_to_db import connect_to_database
from datetime import datetime, timedelta
import freecurrencyapi

API_KEY = 'fca_live_T6dRB6eXL7imXrxOpBdiZiUTaXjnzigIAeLL4cDi'


def split_user_full_name(user_full_name):
    name, surname = re.split(r'\W+', user_full_name)
    return name, surname


def insert_user_info(cursor, name, surname, birth_day, accounts):
    cursor.execute('INSERT INTO User (name, surname, birth_day, accounts) VALUES (?, ?, ?, ?)',
                   (name, surname, birth_day, accounts))


@connect_to_database
def add_user(cursor, *args):
    for i in args:
        if isinstance(i, dict):
            name, surname = split_user_full_name(i.get('user_full_name'))
            insert_user_info(cursor, name, surname, i.get('birth_day'), i.get('accounts'))

        elif isinstance(i, tuple) and len(i) == 3:
            name, surname = split_user_full_name(i[0])
            insert_user_info(cursor, name, surname, i[1], i[2])
    return cursor.lastrowid


def insert_bank_name(cursor, bank_name):
    cursor.execute('INSERT INTO Bank (name) VALUES (?)', (bank_name,))


@connect_to_database
def add_bank(cursor, *args):
    for i in args:
        if isinstance(i, dict):
            insert_bank_name(cursor, i.get('name'))

        elif isinstance(i, str):
            insert_bank_name(cursor, i)
    return cursor.lastrowid


def insert_account_info(cursor, account_data):
    cursor.execute('INSERT INTO Account (User_id, Type, Account_Number, Bank_id, Currency, Amount, Status) '
                   'VALUES (?, ?, ?, ?, ?, ?, ?)', account_data)


@connect_to_database
def add_account(cursor, *args):
    for i in args:
        if isinstance(i, dict):
            data = (i.get('user_id'), i.get('type'), i.get('account_number'), i.get('bank_id'),
                    i.get('currency'), i.get('amount'), i.get('status'))

            insert_account_info(cursor, data)

        elif isinstance(i, tuple) and len(i) == 7:
            insert_account_info(cursor, i)


# CSV
def read_csv_and_add_data(path):
    with open(path, 'r', newline='') as csvfile:
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


# Change info
###################################################################################################################
@connect_to_database
def modify_user(cursor, user_id, new_data):
    cursor.execute('UPDATE User SET name=?, surname=?, birth_day=?, accounts=? WHERE id=?',
                   (new_data['name'], new_data['surname'], new_data['birth_day'], new_data['accounts'], user_id))


@connect_to_database
def modify_bank(cursor, bank_id, new_data):
    cursor.execute('UPDATE Bank SET name=? WHERE id=?', (new_data['bank_name'], bank_id))


@connect_to_database
def modify_account(cursor, account_id, new_data):
    cursor.execute('UPDATE Account SET user_id=?, type=?, account_number=?, bank_id=?, currency=?, amount=?, status=? '
                   'WHERE Id=?',
                   (new_data['user_id'], new_data['type'], new_data['account_number'], new_data['bank_id'],
                    new_data['currency'], new_data['amount'], new_data['status'], account_id))


#######################################################################################################################
# Delete row
@connect_to_database
def delete_user(cursor, user_id):
    cursor.execute('DELETE FROM User WHERE id = ?', (user_id,))


@connect_to_database
def delete_bank(cursor, bank_id):
    cursor.execute('DELETE FROM Bank WHERE id = ?', (bank_id,))


@connect_to_database
def delete_account(cursor, account_id):
    cursor.execute('DELETE FROM Account WHERE id = ?', (account_id,))

#################################################################################################


@connect_to_database
def get_balance(cursor, id):
    cursor.execute('SELECT amount, currency, bank_id FROM Account WHERE id = ?', (id,))
    user_data = cursor.fetchone()
    return (user_data[0], user_data[1], user_data[2]) if user_data else (None, None, None)


@connect_to_database
def update_balance(cursor, id, new_balance):
    cursor.execute('UPDATE Account SET amount = ? WHERE id = ?', (new_balance, id))


@connect_to_database
def get_bank_name(cursor, bank_id):
    cursor.execute('SELECT name FROM Bank WHERE Id = ?', (bank_id,))
    bank_name = cursor.fetchone()
    return bank_name[0] if bank_name else None


@connect_to_database
def insert_transaction(cursor, transaction_data):
    cursor.execute('INSERT INTO Transactions (bank_sender_name, account_sender_id, bank_receiver_name, '
                   'account_receiver_id, sent_currency, sent_amount, datetime) VALUES (?, ?, ?, ?, ?, ?, '
                   'datetime("now"))', (get_bank_name(transaction_data[0]), transaction_data[1],
                                        get_bank_name(transaction_data[2]), transaction_data[3],
                                        transaction_data[4], transaction_data[5]))


def perform_transfer(sender_id, receiver_id, amount):
    sender_balance, sender_currency, sender_bank_id = get_balance(sender_id)
    receiver_balance, receiver_currency, receiver_bank_id = get_balance(receiver_id)

    #######################################################################
    if sender_balance is None or receiver_balance is None:
        print("Account not found.")
        return

    if sender_balance < amount:
        print("Insufficient balance.")
        return
    #######################################################################

    if sender_currency != receiver_currency:
        client = freecurrencyapi.Client(API_KEY)
        print(client.status())  # lOG
        exchange_rates = client.latest()
        print(exchange_rates)  # LOG

        if sender_currency in exchange_rates['data'] and receiver_currency in exchange_rates['data']:
            exchange_rate = exchange_rates['data'][receiver_currency] / exchange_rates['data'][sender_currency]
            amount_in_receiver_currency = amount * exchange_rate
        else:
            print("Currency conversion not available.")
            return
    else:
        amount_in_receiver_currency = amount

    new_sender_balance = sender_balance - amount
    new_receiver_balance = receiver_balance + amount_in_receiver_currency

    update_balance(sender_id, new_sender_balance)
    update_balance(receiver_id, new_receiver_balance)
    insert_transaction((sender_bank_id, sender_id, receiver_bank_id, receiver_id, sender_currency, amount))


@connect_to_database
def get_users_ids(cursor):
    cursor.execute('SELECT user_id FROM Account')
    return [i[0] for i in cursor.fetchall()]


def get_discount_for_random_users():
    discounts = (25, 30, 50)
    user_ids = get_users_ids()

    num_users = random.randint(1, min(len(user_ids), 10))
    lucky_users = random.sample(user_ids, num_users)

    return {user_id: random.choice(discounts) for user_id in lucky_users}


@connect_to_database
def get_users_with_debts(cursor):
    cursor.execute('SELECT user_id FROM Account WHERE amount < 0')
    for i in cursor.fetchall():
        cursor.execute('SELECT name, surname FROM User WHERE id = ?', (i[0],))
        user_name = cursor.fetchall()
    return user_name


def get_full_names_of_users_with_debts():
    full_names = []
    for name, surname in get_users_with_debts():
        full_names.append(name + ' ' + surname)
    return full_names


@connect_to_database
def get_bank_with_biggest_capital(cursor):
    cursor.execute('''SELECT b.name FROM Bank b JOIN Account a ON b.id = a.bank_id GROUP BY b.id 
                        ORDER BY SUM(a.amount) DESC LIMIT 1''')

    bank_with_biggest_capital = cursor.fetchone()[0]
    print(bank_with_biggest_capital)

    return bank_with_biggest_capital if bank_with_biggest_capital else None


@connect_to_database
def get_bank_serving_oldest_client(cursor):
    cursor.execute('''SELECT b.name FROM Bank b JOIN Account a ON b.id = a.bank_id JOIN User u ON a.user_id = u.id
                        ORDER BY u.birth_day ASC LIMIT 1''')

    bank_serving_oldest_client = cursor.fetchone()[0]
    return bank_serving_oldest_client if bank_serving_oldest_client else None


@connect_to_database
def get_bank_with_most_unique_outbound_transactions(cursor):
    cursor.execute('''SELECT b.name FROM Bank b JOIN Account a ON b.Id = a.bank_id 
                        JOIN Transactions t ON a.Id = t.account_sender_id WHERE t.bank_sender_name = b.name 
                        GROUP BY b.id ORDER BY COUNT(DISTINCT a.user_id) DESC LIMIT 1''')

    bank_with_most_unique_users = cursor.fetchone()[0]
    return bank_with_most_unique_users if bank_with_most_unique_users else None


def delete_user_or_account_row(data_to_delete, del_user):
    for i in data_to_delete:
        delete_user(i) if del_user else delete_account(i)


@connect_to_database
def delete_users_and_accounts_with_missing_info(cursor):
    cursor.execute('''SELECT id FROM User WHERE name IS NULL OR surname IS NULL OR birth_day IS NULL''')
    delete_user_or_account_row([i[0] for i in cursor.fetchall()], True)

    cursor.execute('''SELECT id FROM Account WHERE user_id IS NULL OR type IS NULL OR account_Number IS NULL 
                        OR bank_id IS NULL OR currency IS NULL OR amount IS NULL OR status IS NULL ''')
    delete_user_or_account_row([i[0] for i in cursor.fetchall()], False)


@connect_to_database
def search_transactions_for_user_past_3_months(cursor, user_id):
    cursor.execute('''SELECT * FROM Transactions WHERE account_sender_id OR account_receiver_id = ? 
    AND datetime >= ?''', (user_id, datetime.now() - timedelta(days=90)))
    return cursor.fetchall()


#####################################################################################
# Example usage
user_data_1 = {
    'user_full_name': 'John Doe',
    'birth_day': '1990-01-01',
    'accounts': '123,456'
}

user_data_2 = ('Jane Candy', '1995-02-02', '789,012')

user_data_3 = ('Katie Ellison', '2000-08-03', '864,682')

bank = ['Bank 8', 'Bank po']

dat = {
    'user_id': 1,
    'type': 'credit',
    'account_number': '12345678',
    'bank_id': 1,
    'currency': 'USD',
    'amount': -2000,
    'status': 'gold'
}
###################################################################################

add_user(user_data_1, user_data_2, user_data_3)
add_bank(*bank)
add_account(dat)

# CSV
read_csv_and_add_data(r'D:\Projects\Python\lab_5\test_data.csv')

# Modify


data = {
    'name': 'New Name',  # Modify this field based on your requirements
    'surname': 'New Surname',  # Modify this field based on your requirements
    'birth_day': '2000-01-01',  # Modify this field based on your requirements
    'accounts': '987,674',  # Modify this field based on your requirements
    'bank_name': 'Ggbank',
    'user_id': 123,
    'type': 'debit',
    'account_number': '12345778',
    'bank_id': 1,
    'currency': 'USD',
    'amount': -13400,
    'status': 'gold'
}

# modify_user(1, data)
#
# modify_bank(4, data)
#
# modify_account(1, data)
#
#
# # Del
#
# delete_user(2)
# delete_bank(1)
# delete_account(3)

# Transfer

perform_transfer(3, 4, 23)

##############Part 4#########################################################
## 1
get_discount_for_random_users()
## 2
get_full_names_of_users_with_debts()
## 3
print(get_bank_with_biggest_capital())
## 4
print(get_bank_serving_oldest_client())
## 5
print(get_bank_with_most_unique_outbound_transactions())

## 6
# delete_users_and_accounts_with_missing_info()

print(search_transactions_for_user_past_3_months(3))
print(search_transactions_for_user_past_3_months(4))
