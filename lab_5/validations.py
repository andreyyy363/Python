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

    if not number.startswith("ID--") or not re.match(r'^[A-Za-z]{1,3}-\d+-', number[5:]):
        raise ValueError('Account number has the wrong format or broken ID pattern!')

    return number


##############################################################################################################

full_name = 'John123 Doe!?'
name, surname = validate_user_name(full_name)
print("Name:", name)
print("Surname:", surname)

###############################################################################################################

ALLOWED_ACCOUNT_TYPES = {'credit', 'debit'}
ALLOWED_CURRENCIES = {'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD'}
ALLOWED_STATUSES = {'gold', 'silver', 'platinum'}

try:
    account_type = 'savings'
    validate_field_with_strict_set_of_values(ALLOWED_ACCOUNT_TYPES, account_type, 'account_type')
except ValueError as e:
    print(e)

try:
    currency = 'INR'
    validate_field_with_strict_set_of_values(ALLOWED_CURRENCIES, currency, 'currency')
except ValueError as e:
    print(e)

try:
    status = 'iron'
    validate_field_with_strict_set_of_values(ALLOWED_STATUSES, status, 'status')
except ValueError as e:
    print(e)

#################################################################################################################

print(validate_current_time('2023-11-11 23:32:10'))

#################################################################################################################

try:
    account_number = 'ID--jq?43254765-99'
    number = validate_account_number(account_number)
    print("Account number is valid:", number)
except ValueError as e:
    print(e)
