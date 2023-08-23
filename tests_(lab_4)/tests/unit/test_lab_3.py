from lab_3.lab_3 import UserData
from unittest.mock import MagicMock, patch, mock_open
import pytest


@pytest.fixture(scope='function')
@patch.multiple('lab_3.lab_3.UserData',
                setting_argparse=MagicMock(**{'destination': 'test', 'filename': '1'}),
                get_logger=MagicMock(return_value=None))
def user_data_instance():
    return UserData()


def test_count_age(user_data_instance):
    input_data = [{'dob.age': '25'}, {'dob.age': '30'}]

    actual = user_data_instance.count_age(input_data)

    expected = (30, 27)
    assert actual == expected


@pytest.mark.parametrize('gender, num_rows, expected',
                         [
                             ('male', None, [{'gender': 'male'}, {'gender': 'male'}]),
                             (None, 2, [{'gender': 'male'}, {'gender': 'female'}]),
                             (None, None, [{'gender': 'male'}, {'gender': 'female'}, {'gender': 'male'}])
                         ])
def test_sort_data(user_data_instance, gender, num_rows, expected):
    user_data_instance.args = MagicMock(gender=gender, numb_of_rows=num_rows)
    user_data_instance.data = [{'gender': 'male'}, {'gender': 'female'}, {'gender': 'male'}]
    user_data_instance.sort_data()

    assert user_data_instance.sorted_data == expected


def test_convert_date_in_sorted_data(user_data_instance):

    actual = {'dob.date': '1990-01-15T08:00:00Z', 'registered.date': '2022-05-20T14:30:00Z'}
    expected = {'dob.date': '01/15/1990', 'registered.date': '05/20/2022, 14:30:00'}

    user_data_instance.convert_date_in_sorted_data(actual, 'dob.date')
    user_data_instance.convert_date_in_sorted_data(actual, 'registered.date')

    assert actual == expected


def test_rearrange_the_data(user_data_instance):
    input_data = [{'dob.date': '08/03/1990', 'location.country': 'USA'},
                  {'dob.date': '12/15/1985', 'location.country': 'Canada'},
                  {'dob.date': '05/21/1995', 'location.country': 'USA'}]
    user_data_instance.sorted_data = input_data

    actual = user_data_instance.rearrange_the_data()
    expected = {'1980-th': {'Canada': [{'dob.date': '12/15/1985', 'location.country': 'Canada'}]},
                '1990-th': {'USA': [{'dob.date': '05/21/1995', 'location.country': 'USA'},
                                    {'dob.date': '08/03/1990', 'location.country': 'USA'}]}}
    assert actual == expected


@patch('lab_3.lab_3.UserData.count_age', return_value=(30, 25))
@patch('lab_3.lab_3.UserData.find_most_popular_id', return_value='alice123')
def test_create_file_path(mock_ca, mock_fmpi, user_data_instance):
    input = ('1990-th', 'USA')

    actual = user_data_instance.create_file_path(None, input[0], input[1])
    expected = ('max_age_30_avg_registered_25_popular_id_alice123.csv',
                f'{input[0]}\\{input[1]}\\max_age_30_avg_registered_25_popular_id_alice123.csv')
    assert actual == expected


@patch('builtins.open', new_callable=mock_open)
@patch('csv.DictWriter')
def test_save_data_to_csv(mock_d_w, mock_o, user_data_instance):
    user_data_instance.fieldnames = ['id', 'name', 'age']
    data = [{'id': 1, 'name': 'John', 'age': 30}, {'id': 2, 'name': 'Jane', 'age': 25}]

    mock_o.return_value = mock_o()
    user_data_instance.save_data_to_csv(data, 'test.csv')

    mock_o.assert_called_with('test.csv', 'w', newline='', encoding='utf-8')
    mock_d_w.assert_called_once_with(mock_o(), fieldnames=user_data_instance.fieldnames)
    mock_d_w.return_value.writeheader.assert_called_once_with()
    mock_d_w.return_value.writerows.assert_called_once_with(data)
