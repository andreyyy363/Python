import re
from datetime import datetime


def validate_user_name(user_full_name):
    """
    Cleans the user's full name and separates it into first name and surname.

    :param user_full_name: (str) The full name of the user.
    :return: (tuple) A tuple containing the first name and surname.
    """
    cleaned_full_name = re.sub(r'[^a-zA-Z\s]', '', user_full_name)
    separated_full_name = cleaned_full_name.split()

    if len(separated_full_name) < 2:
        raise ValueError('Surname is missing')

    user_name = separated_full_name[0]
    user_surname = separated_full_name[1]

    return user_name, user_surname


def validate_field_with_strict_set_of_values(allowed_values, field_value, field_name):
    """
    Checks if the field value is in the set of allowed values.

    :param allowed_values: (set) A set of allowed values for the field.
    :param field_value: (str) The value of the field to be checked.
    :param field_name: (str) The name of the field.
    :raises: ValueError: If the field value is not in the set of allowed values.
    """
    if field_value not in allowed_values:
        raise ValueError(f'Not allowed value {field_value} for field {field_name}!')


def validate_current_time(date_time):
    """
    Checks if the date_time is None. If it is, returns the current time.

    :param date_time: (str) The date and time to be checked.
    :return: (str) The current date and time if date_time is None, else returns date_time.
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S') if date_time is None else date_time


def validate_account_number(number):
    """
    Validates the account number by checking its length and format.

    :param number: (str) The account number to be validated.
    :return: (str) The validated account number.
    :raises: ValueError: If the account number does not meet the required format or length.
    """
    number = re.sub(r'[%#_?&]', '-', number)

    if len(number) != 18:
        raise ValueError(f'Too {"many" if len(number) > 18 else "little" if len(number) < 18 else ""} '
                         'chars in account number!')

    if not number.startswith("ID--"):
        raise ValueError('Account number has the wrong format')
    if not re.match(r'^[A-Za-z]{1,3}-\d+-', number[5:]):
        raise ValueError('Account number has broken ID pattern!')

    return number


def validate_balance(user_data, account_id, amount):
    if user_data is None:
        raise ValueError(f'Account with id {account_id} not found.')

    if user_data[0] < amount:
        raise ValueError('Insufficient balance.')


def run_all_validations():
    FULL_NAME_1 = 'John123 Doe!?'
    FULL_NAME_2 = 'John123!?'
    try:
        name, surname = validate_user_name(FULL_NAME_1)
        print("Name:", name)
        print("Surname:", surname)
    except ValueError as e:
        print(e)

    try:
        name, surname = validate_user_name(FULL_NAME_2)
        print("Name:", name)
        print("Surname:", surname)
    except ValueError as e:
        print(e)

    ALLOWED_ACCOUNT_TYPES = {'credit', 'debit'}
    ALLOWED_CURRENCIES = {'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD'}
    ALLOWED_STATUSES = {'gold', 'silver', 'platinum'}

    try:
        ACCOUNT_TYPE = 'savings'
        validate_field_with_strict_set_of_values(ALLOWED_ACCOUNT_TYPES, ACCOUNT_TYPE, 'account_type')
    except ValueError as e:
        print(e)

    try:
        CURRENCY = 'INR'
        validate_field_with_strict_set_of_values(ALLOWED_CURRENCIES, CURRENCY, 'currency')
    except ValueError as e:
        print(e)

    try:
        STATUS = 'iron'
        validate_field_with_strict_set_of_values(ALLOWED_STATUSES, STATUS, 'status')
    except ValueError as e:
        print(e)

    print(validate_current_time('2023-11-11 23:32:10'))
    print(validate_current_time(None))

    try:
        account_number = validate_account_number('ID--AB-12345679012')
        print('Account number is valid:', account_number)
    except ValueError as e:
        print(e)
