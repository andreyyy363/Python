import csv
import tempfile
import os
from lab_3.lab_3 import UserData
from unittest.mock import MagicMock, patch


@patch('lab_3.lab_3.UserData.__init__', return_value=None)
def test_count_age(mock_i):
    user_data = UserData()

    input_data = [{'dob.age': '25'}, {'dob.age': '30'}, {'dob.age': '22'}, {'dob.age': '40'}, {'dob.age': '18'}]

    actual_max_age, actual_avg_age = user_data.count_age(input_data)
    expected_max_age = 40
    expected_avg_age = 27
    assert actual_max_age == expected_max_age
    assert actual_avg_age == expected_avg_age


@patch('lab_3.lab_3.UserData.__init__', return_value=None)
def test_sort_data(mock_i):
    user_data = UserData()
    # Check for filtering by gender
    user_data.args = MagicMock(gender='male', numb_of_rows=None)
    user_data.data = [{'gender': 'male'}, {'gender': 'female'}, {'gender': 'male'}]
    user_data.sort_data()
    expected_len = 2
    assert len(user_data.sorted_data) == expected_len
    for row in user_data.sorted_data:
        assert row['gender'] == 'male'

    # Check for filtering by number of rows
    user_data.args = MagicMock(gender=None, numb_of_rows=2)
    user_data.data = [{'gender': 'male'}, {'gender': 'female'}, {'gender': 'unknown'}]
    user_data.sort_data()
    expected_len = 2
    assert len(user_data.sorted_data) == expected_len

    # Check for filtering without parameters
    user_data.args = MagicMock(gender=None, numb_of_rows=None)
    user_data.data = [{'gender': 'male'}, {'gender': 'female'}, {'gender': 'unknown'}]
    user_data.sort_data()
    expected_len = 3
    assert len(user_data.sorted_data) == expected_len


@patch('lab_3.lab_3.UserData.__init__', return_value=None)
def test_convert_date_in_sorted_data(mock_i):
    user_data = UserData()

    actual = {'dob.date': '1990-01-15T08:00:00Z', 'registered.date': '2022-05-20T14:30:00Z'}
    expected = {'dob.date': '01/15/1990', 'registered.date': '05/20/2022, 14:30:00'}

    user_data.convert_date_in_sorted_data(actual, 'dob.date')
    user_data.convert_date_in_sorted_data(actual, 'registered.date')

    assert actual == expected


@patch('lab_3.lab_3.UserData.__init__', return_value=None)
def test_rearrange_the_data(mock_i):
    user_data = UserData()
    input_data = [{'dob.date': '08/03/1990', 'location.country': 'USA'},
                  {'dob.date': '12/15/1985', 'location.country': 'Canada'},
                  {'dob.date': '05/21/1995', 'location.country': 'USA'}]
    user_data.sorted_data = input_data

    actual = user_data.rearrange_the_data()
    expected = {'1980-th': {'Canada': [{'dob.date': '12/15/1985', 'location.country': 'Canada'}]},
                '1990-th': {'USA': [{'dob.date': '05/21/1995', 'location.country': 'USA'},
                                    {'dob.date': '08/03/1990', 'location.country': 'USA'}]}}
    assert actual == expected


@patch('lab_3.lab_3.UserData.__init__', return_value=None)
@patch('lab_3.lab_3.UserData.count_age', return_value=(30, 25))
@patch('lab_3.lab_3.UserData.find_most_popular_id', return_value='alice123')
def test_create_file_path(mock_i, mock_ca, mock_fmpi):
    user_data = UserData()
    input_users_data = [{'name': 'Alice', 'dob.age': '25'}, {'name': 'Bob', 'dob.age': '30'}]
    input_decade = '1990-th'
    input_country = 'USA'

    actual_file_name, actual_file_path = user_data.create_file_path(input_users_data, input_decade, input_country)
    expected_file_name = f'max_age_30_avg_registered_25_popular_id_alice123.csv'
    expected_file_path = f'{input_decade}\\{input_country}\\{expected_file_name}'
    assert actual_file_name == expected_file_name
    assert actual_file_path == expected_file_path


@patch('lab_3.lab_3.UserData.__init__', return_value=None)
def test_save_data_to_csv(mock_i):
    with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', encoding='utf-8') as temp_csv:
        input_data = [{'id': 1, 'name': 'John', 'age': 30}, {'id': 2, 'name': 'Jane', 'age': 25}]
        user_data = UserData()
        user_data.fieldnames = ['id', 'name', 'age']
        user_data.save_data_to_csv(input_data, temp_csv.name)

        with open(temp_csv.name, 'r', newline='', encoding='utf-8') as saved_csv:
            reader = csv.DictReader(saved_csv)
            actual = [row for row in reader]
            expected = [{'id': '1', 'name': 'John', 'age': '30'}, {'id': '2', 'name': 'Jane', 'age': '25'}]
            assert actual == expected

    os.remove(temp_csv.name)
