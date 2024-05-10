import os
import subprocess
from work_with_db import (add_data_from_csv, modify_data,
                          perform_transfer, get_discount_for_random_users, get_full_names_of_users_with_debts,
                          get_bank_serving_oldest_client, get_bank_with_biggest_capital,
                          get_bank_with_most_unique_outbound_transactions, delete_users_and_accounts_with_missing_info,
                          filter_transactions_past_3_months, delete_from_db)
from work_with_db import (split_full_name_in_dict, add_data)


def print_stripe():
    print('-' * 100)


def print_menu():
    print('Lab 5')
    print_stripe()
    print('Bank Menu')
    print_stripe()
    print('[1] - Add user/bank/account to the DB.')
    print('[2] - Add user/bank/account to the DB from CSV file.')
    print('[3] - Modify one particular user/bank/account row of data.')
    print('[4] - Delete one particular user/bank/account row of data.')
    print('[5] - Performs money transfer from one card to another.')
    print('[6] - Get discounts for random users.')
    print('[7] - Get users with debts.')
    print('[8] - Get bank name which operates the biggest capital.')
    print('[9] - Get bank name which serves the oldest client.')
    print('[10] - Get bank name with the highest number of unique users which performed outbound transactions.')
    print('[11] - Delete users and account that don’t have full information.')
    print('[12] - Get transactions of particular user for past 3 months.')
    print('[13] - Delete DB and stop program.')
    print('[14] - Stop program.')
    print_stripe()


def make_action():
    while True:
        print_menu()
        choice = input('Please, enter your choice: ')
        match int(choice):
            case 1:
                choice = input('What would you like to add ([1] - user, [2] - bank, [3] - account)? ')
                match int(choice):
                    case 1:
                        user_data_1 = {
                            'user_full_name': 'John Doe',
                            'birth_day': '1990-01-01',
                            'accounts': '123,456'
                        }
                        user_data_2 = {
                            'user_full_name': 'Jane Candy',
                            'birth_day': '1995-02-02',
                            'accounts': '789,012'
                        }
                        user_data_3 = {
                            'user_full_name': 'Katie Ellison',
                            'birth_day': '2000-08-03',
                            'accounts': '864,682'
                        }

                        user_data_1, user_data_2, user_data_3 = split_full_name_in_dict(user_data_1,
                                                                                        user_data_2, user_data_3)
                        add_data('User', user_data_1, user_data_2, user_data_3)
                    case 2:
                        bank_data_1 = {'name': 'Crazy Bank'}
                        bank_data_2 = {'name': 'Angry Bank'}

                        add_data('Bank', bank_data_1, bank_data_2)
                    case 3:
                        account_data = {'user_id': 1, 'type': 'credit', 'account_number': '12345678', 'bank_id': 1,
                                        'currency': 'USD', 'amount': -2000, 'status': 'gold'}

                        add_data('Account', account_data)
            case 2:
                add_data_from_csv(r'D:\Projects\Python\lab_5\test_data.csv')
            case 3:
                choice = input('What would you like to modify ([1] - user, [2] - bank, [3] - account)? ')
                match int(choice):
                    case 1:
                        new_user_data = {
                            'name': 'New Name',
                            'surname': 'New Surname',
                            'birth_day': '2000-01-01',
                            'accounts': '987,674',
                        }
                        modify_data('User', 1, new_user_data)
                    case 2:
                        new_bank_data = {'name': 'New Bank'}
                        modify_data('Bank', 4, new_bank_data)
                    case 3:
                        new_account_data = {
                            'user_id': 123,
                            'type': 'debit',
                            'account_number': '12345778',
                            'bank_id': 1,
                            'currency': 'USD',
                            'amount': -13400,
                            'status': 'gold'
                        }
                        modify_data('Account', 1, new_account_data)
            case 4:
                choice = input('What would you like to add ([1] - user, [2] - bank, [3] - account)? ')
                match int(choice):
                    case 1:
                        delete_from_db(2, 'User')
                    case 2:
                        delete_from_db(1, 'Bank')
                    case 3:
                        delete_from_db(1, 'Account')
            case 5:
                perform_transfer(3, 5, 100)
            case 6:
                print(get_discount_for_random_users())
            case 7:
                print(get_full_names_of_users_with_debts())
            case 8:
                print(get_bank_with_biggest_capital())
            case 9:
                print(get_bank_serving_oldest_client())
            case 10:
                print(get_bank_with_most_unique_outbound_transactions())
            case 11:
                delete_users_and_accounts_with_missing_info()
            case 12:
                print(filter_transactions_past_3_months(3))
                print(filter_transactions_past_3_months(1))
            case 13:
                os.remove('bank.db')
                break
            case 14:
                break


if __name__ == "__main__":
    if not os.path.exists('bank.db'):
        subprocess.run(['python', '001__initial_db_setup.py', '--uniqueness'], check=True)
    make_action()
