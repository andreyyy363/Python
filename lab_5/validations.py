import re
from datetime import datetime


def validate_user_name(user_full_name):
    cleaned_full_name = re.sub(r'[^a-zA-Z\s]', '', user_full_name)
    separated_full_name = cleaned_full_name.split()

    user_name = separated_full_name[0] if len(separated_full_name) >= 2 else cleaned_full_name
    user_surname = separated_full_name[1] if len(separated_full_name) >= 2 else ''

    return user_name, user_surname


def validate_field_with_strict_set_of_values(allowed_values, field_value, field_name):
    if field_value not in allowed_values:
        raise ValueError(f'Not allowed value {field_value} for field {field_name}!')


def validate_current_time(date_time):
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S') if date_time is None else date_time


def validate_account_number(number):
    number = re.sub(r'[%#_?&]', '-', number)

    if len(number) != 18:
        raise ValueError(f'Too {"many" if len(number) > 18 else "little" if len(number) < 18 else ""} '
                         f'chars in account number!')

    if not number.startswith("ID--"):
        raise ValueError('Account number has the wrong format')
    if not re.match(r'^[A-Za-z]{1,3}-\d+-', number[5:]):
        raise ValueError('Account number has broken ID pattern!')

    return number


##############################################################################################################

FULL_NAME = 'John123 Doe!?'
name, surname = validate_user_name(FULL_NAME)
print("Name:", name)
print("Surname:", surname)

###############################################################################################################

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
    account_number = validate_account_number('ID--jq?43254765-99')
    print("Account number is valid:", account_number)
except ValueError as e:
    print(e)
