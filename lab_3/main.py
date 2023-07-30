import argparse
import logging
import os
import csv
import shutil
from datetime import datetime, timedelta
import urllib.request
import pytz
from collections import Counter


class UserData:
    """ Class to work with user database """
    URL = 'https://randomuser.me/api/?format=csv&results=100'
    
    def __init__(self):
        self.args = self.setting_argparse()
        self.logger = self.get_logger()
        self.destination = f'{self.args.destination}{self.args.filename}.csv'
        self.new_path = os.path.join(self.args.destination, 'Data')
        self.data = []
        self.fieldnames = None
        self.sorted_data = []
        self.rearranged_data = {}

    def setting_argparse(self):
        """
        Parses the command-line arguments using the `argparse` module.
        :return parser.parse_args(): an object containing the parsed command-line arguments
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--destination', type=str, required=True)
        parser.add_argument('--filename', type=str, default='output')
        sort_type = parser.add_mutually_exclusive_group()
        sort_type.add_argument('--gender', type=str)
        sort_type.add_argument('--numb_of_rows', type=int)
        parser.add_argument('log_level', type=str)
        return parser.parse_args()

    def get_logger(self):
        """
        Create and configure a logger for logging application events.
        :return logger:  a logger instance configured for logging
        """
        logger = logging.getLogger('logger')
        logger.setLevel(self.args.log_level.upper())
        file_handler = logging.FileHandler('file.log', encoding='utf-8')
        file_handler.setLevel(self.args.log_level.upper())
        formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def download_user_data(self):
        """
        Downloads user data from a remote API and saves it to a CSV file.
        This function downloads user data from the specified API endpoint in CSV format
        and saves it to the destination path provided in the command line arguments.
        """
        urllib.request.urlretrieve(self.URL, self.destination)
        self.logger.info(f'File successfully downloaded from {self.URL} and saved to {self.destination}')

    def get_user_data_from_csv(self):
        """
        Reads user data from a CSV file and stores it in the object.
        This function reads user data from the CSV file specified by the 'destination'
        attribute of the object. The data is stored as a list of dictionaries, with each
        dictionary representing a row in the CSV file.
        """
        with open(self.destination, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.fieldnames = reader.fieldnames
            self.data = list(reader)

        self.logger.info('Data successfully read from the file.')
        self.logger.debug(f'Fieldnames in data: {self.fieldnames}')
        self.logger.debug(f'Received data from the file: {self.data}')

    def sort_data(self):
        """
        Sorts the user data based on specified criteria.
        This function sorts the user data based on the sorting criteria provided by the user
        through the command-line arguments. The sorting criteria can be either 'male' or 'female'
        to filter data by gender, or an integer value to filter data by the number of rows.
        """
        # Filter by gender
        if self.args.numb_of_rows is None:
            reverse = True if self.args.gender.lower() == 'male' else \
                False if self.args.gender.lower() == 'female' else None
            self.sorted_data = sorted(self.data, key=lambda x: x['gender'], reverse=reverse)

        # Filter by number of rows
        elif self.args.gender is None:
            self.sorted_data = self.data[:self.args.numb_of_rows]

        self.logger.info(f'Data successfully sorted by {"rows" if self.args.gender is None else "gender"}.')
        self.logger.debug(f'Sorted data: {self.sorted_data}')

    def add_index_to_sorted_data(self):
        # Add global index
        for i, row in enumerate(self.sorted_data, start=1):
            row['global.index'] = i
        self.logger.info('Column "global.index" filled successfully.')

    def add_current_time_to_sorted_data(self, i):
        # Add current time
        timezone_str = i['location.timezone.offset']
        hours, minutes = map(int, timezone_str.split(':'))
        i['current.time'] = timedelta(hours=hours, minutes=minutes) + datetime.now(pytz.utc)
        self.logger.debug(f'Current time of user {i["login.username"]} is {i["current.time"]}.')

    def change_title_name_in_sorted_data(self, i):
        # Change name.title
        match i['name.title']:
            case 'Mr':
                i['name.title'] = 'Mister'
            case 'Ms':
                i['name.title'] = 'Miss'
            case 'Mrs':
                i['name.title'] = 'Missis'
            case 'Madame':
                i['name.title'] = 'Mademoiselle'
        self.logger.debug(f'Name title for user {i["login.username"]} has been changed to {i["name.title"]}.')

    def convert_date_in_sorted_data(self, i, date_type):
        date = datetime.fromisoformat(i[date_type].replace('Z', '+00:00'))
        i[date_type] = date.strftime(f'%m/%d/%Y{", %H:%M:%S" if date_type == "registered.date" else ""}')

    def update_some_data(self):
        """
        This method adds new columns to the data, fills the 'global.index' column with incremental indices,
        adds the 'current.time' column with the current time adjusted by the user's timezone, and performs
        some transformations on certain columns such as 'name.title', 'dob.date', and 'registered.date'.
        """
        self.fieldnames.append('global.index')
        self.fieldnames.append('current.time')
        self.logger.info('New columns added to fieldnames.')

        self.add_index_to_sorted_data()
        for i in self.sorted_data:
            self.add_current_time_to_sorted_data(i)
            self.change_title_name_in_sorted_data(i)

            # Convert dob.date
            self.convert_date_in_sorted_data(i, 'dob.date')
            self.logger.debug(f'Dob date for user {i["login.username"]} has been converted to {i["dob.date"]}.')

            # Convert registered.date
            self.convert_date_in_sorted_data(i, 'registered.date')
            self.logger.debug(f'Register date for user {i["login.username"]} '
                              f'has been converted to {i["registered.date"]}.')

        self.logger.info('The sorted data was successfully modified.')
        self.logger.debug(f'Fieldnames with new columns in data: {self.fieldnames}')
        self.logger.debug(f'Changed sorted data: {self.sorted_data}')
        self.save_data_to_csv(self.sorted_data, self.destination)

    def save_data_to_csv(self, data, destination):
        """ This method saves the sorted data to a CSV file at the destination. """
        with open(destination, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(data)

        self.logger.info(f'The data was successfully saved to {destination}.')

    def create_new_working_dir(self):
        """ This method creates a new working directory and moves the sorted data file to that directory. """
        os.mkdir(os.path.join(self.args.destination, 'Data'))
        self.logger.info(f'The new folder was successfully created. His full path {self.new_path}')

        shutil.move(self.destination, self.new_path)
        self.logger.info(f'File with sorted data moved to {self.new_path}')

        os.chdir(self.new_path)
        self.logger.info(f'New working directory: {self.new_path}')

    def rearrange_the_data(self):
        """ This method rearranges the sorted data into a new format, grouped by decade and country. """
        for i in self.sorted_data:
            dob_date = datetime.strptime(i['dob.date'], '%m/%d/%Y')
            decade = f'{dob_date.year // 10 * 10}-th'
            country = i['location.country']
            self.rearranged_data.setdefault(decade, {}).setdefault(country, [])
            self.rearranged_data[decade][country].append(i)

        for decade, decade_data in self.rearranged_data.items():
            for country, data in decade_data.items():
                self.rearranged_data[decade][country] = sorted(data, key=lambda x: (x['dob.date'],
                                                                                    x['location.country']))

        self.logger.info('The sorted date was successfully rebuilt to the new format.')
        self.logger.debug(f'Rearranged data: {self.rearranged_data}')

    def count_age(self, users_data):
        # Count max age and average age
        ages = [int(i['dob.age']) for i in users_data]
        max_age = max(ages)
        total_ages = sum(ages)
        avg_registered = int(total_ages / len(users_data))
        return max_age, avg_registered

    def find_most_popular_id(self, users_data):
        # Find most popular id
        id_names = [i['id.name'] for i in users_data]
        name_counter = Counter(id_names)
        popular_id = name_counter.most_common(1)[0][0]
        return popular_id

    def create_file_path(self, users_data, decade, country):
        max_age, avg_registered = self.count_age(users_data)
        popular_id = self.find_most_popular_id(users_data)

        file_name = f'max_age_{max_age}_avg_registered_{avg_registered}_popular_id_{popular_id}.csv'
        country_path = os.path.join(decade, country)
        file_path = os.path.join(country_path, file_name)
        return file_name, file_path

    def create_sub_folders_with_data(self):
        """
        This method creates sub folders for each decade and country and saves specific data
        for each group in CSV files.
        """
        for decade, decade_data in self.rearranged_data.items():
            os.makedirs(decade)
            for country, users_data in decade_data.items():
                os.makedirs(os.path.join(decade, country))
                file_name, file_path = self.create_file_path(users_data, decade, country)
                self.save_data_to_csv(users_data, file_path)
                self.logger.info(f'File {file_name} created in {file_path}')

    def delete_decades_before_1960th(self):
        """ This method deletes all folders with a decade before the 1960s in the Data folder. """
        for i in os.listdir(self.new_path):
            if os.path.isdir(os.path.join(self.new_path, i)) and int(i.split('-')[0]) < 1960:
                shutil.rmtree(os.path.join(self.new_path, i))
                self.logger.debug(fr'The folder has been deleted in the path: {os.path.join(self.new_path, i)}')
        self.logger.info('All folders with a decade before the 1960s have been deleted.')

    def log_full_folder_structure(self, path, numb_of_indents=0):
        """
        This method logs the full folder structure with indentation.

        :param path: the path to the root folder from which the traversal begins
        :param numb_of_indents: the number of tabs used for formatting the output
        """
        indent = '\t' * numb_of_indents
        for i in os.listdir(path):
            i_path = os.path.join(path, i)
            if os.path.isdir(i_path):
                self.logger.info(f'{indent}Folder: {i}')
                self.log_full_folder_structure(i_path, numb_of_indents + 1)
            else:
                self.logger.info(f'{indent}File: {i}')

    def save_all_data_to_zip(self):
        """ This method saves all data in the 'new_path' directory to a ZIP archive. """
        os.chdir(self.args.destination)
        shutil.make_archive('data', 'zip', fr'{self.new_path}')


if __name__ == '__main__':
    user_data = UserData()
    # (1) Setting up new file logger
    user_data.get_logger()
    # (2) Downloading some data by URL
    user_data.download_user_data()
    user_data.get_user_data_from_csv()
    # (4) Sorting data by key
    user_data.sort_data()
    # (5) Adding some fields to the file and saving data to csv
    user_data.update_some_data()
    # (6-7) Creating a new directory and assigning it to a working directory
    user_data.create_new_working_dir()
    # (8) Rearranging the data
    user_data.rearrange_the_data()
    # (9-11) Creating sub folders with special data
    user_data.create_sub_folders_with_data()
    # (12) Removing the data before 1960-th
    user_data.delete_decades_before_1960th()
    # (13) Logging full folder structure
    user_data.log_full_folder_structure(user_data.new_path)
    # (14) Archiving the destination folder
    user_data.save_all_data_to_zip()
