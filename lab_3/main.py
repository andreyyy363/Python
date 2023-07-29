import argparse
import logging
import os
import csv
import shutil
from datetime import datetime, timedelta
import urllib.request
import pytz


class UserData:
    """ Class to work with user database """
    def __init__(self):
        self.args = self.setting_argparse()
        self.destination = f'{self.args.destination}{self.args.filename}.csv'
        self.new_path = fr'{self.args.destination}\Data'
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
        sort_type.add_argument("--gender", type=str)
        sort_type.add_argument("--numb_of_rows", type=int)
        parser.add_argument('log_level', type=str)
        return parser.parse_args()

    def configure_logger(self):
        """
        Configures the logger for the class instance.
        This function sets up the logging configuration based on the log level provided
        in the command line arguments.
        """
        log_level = self.args.log_level.upper()
        logging.basicConfig(filename='file.log',
                            level=getattr(logging, log_level, logging.INFO),
                            format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
        logging.debug(self.args)

    def download_user_data(self):
        """
        Downloads user data from a remote API and saves it to a CSV file.
        This function downloads user data from the specified API endpoint in CSV format
        and saves it to the destination path provided in the command line arguments.
        """
        url = 'https://randomuser.me/api/?format=csv&results=5000'
        urllib.request.urlretrieve(url, self.destination)
        logging.info(f'File successfully downloaded from {url} and saved to {self.destination}')

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
            for row in reader:
                self.data.append(row)
        logging.info('Data successfully read from the file.')
        logging.debug(f'Fieldnames in data: {self.fieldnames}')
        logging.debug(f'Received data from the file: {self.data}')

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

        logging.info(f'Data successfully sorted by {"rows" if self.args.gender is None else "gender"}.')
        logging.debug(f'Sorted data: {self.sorted_data}')

    def add_and_change_some_data(self):
        """
        This method adds new columns to the data, fills the 'global.index' column with incremental indices,
        adds the 'current.time' column with the current time adjusted by the user's timezone, and performs
        some transformations on certain columns such as 'name.title', 'dob.date', and 'registered.date'.
        """
        # Add global index
        self.fieldnames.append('global.index')
        self.fieldnames.append('current.time')
        logging.info('New columns added to fieldnames.')

        for i, row in enumerate(self.sorted_data, start=1):
            row['global.index'] = i
        logging.info('Column "global.index" filled successfully.')

        for i in self.sorted_data:
            # Add current time
            timezone_str = i['location.timezone.offset']
            hours, minutes = map(int, timezone_str.split(':'))
            i['current.time'] = timedelta(hours=hours, minutes=minutes) + datetime.now(pytz.utc)
            logging.debug(f'Current time of user {i["login.username"]} is {i["current.time"]}.')

            # Change name.title
            if i['name.title'] == 'Mr':
                i['name.title'] = 'Mister'
            elif i['name.title'] == 'Ms':
                i['name.title'] = 'Miss'
            elif i['name.title'] == 'Mrs':
                i['name.title'] = 'Missis'
            elif i['name.title'] == 'Madame':
                i['name.title'] = 'Mademoiselle'
            logging.debug(f'Name title for user {i["login.username"]} has been changed to {i["name.title"]}.')

            # Convert dob.date
            dob_date = datetime.fromisoformat(i['dob.date'].replace('Z', '+00:00'))
            i['dob.date'] = dob_date.strftime('%m/%d/%Y')
            logging.debug(f'Dob date for user {i["login.username"]} has been converted to {i["dob.date"]}.')

            # Convert registered.date
            register_datetime = datetime.fromisoformat(i['registered.date'].replace('Z', '+00:00'))
            i['registered.date'] = register_datetime.strftime('%m-%d-%Y, %H:%M:%S')
            logging.debug(f'Register date for user {i["login.username"]} has been converted to {i["registered.date"]}.')

        logging.info('The sorted data was successfully modified.')
        logging.debug(f'Fieldnames with new columns in data: {self.fieldnames}')
        logging.debug(f'Changed sorted data: {self.sorted_data}')

    def save_data_to_csv(self):
        """ This method saves the sorted data to a CSV file at the destination. """
        with open(self.destination, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            for row in self.sorted_data:
                writer.writerow(row)

        logging.info(f'The sorted data was successfully saved to {self.destination}.')

    def create_new_working_dir(self):
        """ This method creates a new working directory and moves the sorted data file to that directory. """

        os.mkdir(fr'{self.args.destination}\Data')
        logging.info(f'The new folder was successfully created. His full path {self.new_path}')
        shutil.move(self.destination, self.new_path)
        logging.info(f'File with sorted data moved to {self.new_path}')
        os.chdir(self.new_path)
        logging.info(f'New working directory: {self.new_path}')

    def rearrange_the_data(self):
        """ This method rearranges the sorted data into a new format, grouped by decade and country. """
        for i in self.sorted_data:
            dob_date = datetime.strptime(i['dob.date'], '%m/%d/%Y')
            decade = f'{dob_date.year // 10 * 10}-th'
            country = i['location.country']
            if decade not in self.rearranged_data:
                self.rearranged_data[decade] = {}
            if country not in self.rearranged_data[decade]:
                self.rearranged_data[decade][country] = []
            self.rearranged_data[decade][country].append(i)

        for decade, decade_data in self.rearranged_data.items():
            for country, data in decade_data.items():
                self.rearranged_data[decade][country] = sorted(data, key=lambda x: (x['dob.date'],
                                                                                    x['location.country']))

        logging.info('The sorted date was successfully rebuilt to the new format.')
        logging.debug(f'Rearranged data: {self.rearranged_data}')

    def create_sub_folders_and_save_some_data(self):
        """
        This method creates sub folders for each decade and country and saves specific data
        for each group in CSV files.
        """
        id_names = []
        for decade, decade_data in self.rearranged_data.items():
            os.makedirs(decade)
            for country, users_data in decade_data.items():
                os.makedirs(os.path.join(decade, country))
                total_ages = 0
                max_age = 0
                for i in users_data:
                    if int(i['dob.age']) > max_age:
                        max_age = int(i['dob.age'])
                    total_ages += int(i['dob.age'])
                    id_names = [i['id.name']]

                avg_registered = int(total_ages / len(users_data))
                popular_id = max(set(id_names), key=id_names.count)

                file_name = f'max_age_{max_age}_avg_registered_{avg_registered}_popular_id_{popular_id}.csv'
                country_path = os.path.join(decade, country)
                file_path = os.path.join(country_path, file_name)

                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                    writer.writeheader()
                    writer.writerows(users_data)

                logging.info(f'File {file_name} created in {file_path}')

    def delete_decades_before_1960th(self):
        """ This method deletes all folders with a decade before the 1960s in the Data folder. """
        for i in os.listdir(fr'{self.new_path}'):
            if os.path.isdir(fr'{self.new_path}\{i}'):
                decade = int(i.split('-')[0])
                if decade < 1960:
                    shutil.rmtree(fr'{self.new_path}\{i}')
                    logging.debug(fr'The folder has been deleted in the path: {self.new_path}\{i}')
        logging.info('All folders with a decade before the 1960s have been deleted.')

    def log_full_folder_structure(self, path, numb_of_tabs=0):
        """
        This method logs the full folder structure with indentation.

        :param path: the path to the root folder from which the traversal begins
        :param numb_of_tabs: the number of tabs used for formatting the output
        """
        tab = '\t' * numb_of_tabs
        for i in os.listdir(path):
            i_path = os.path.join(path, i)
            if os.path.isdir(i_path):
                logging.info(f'{tab}Folder: {i}')
                self.log_full_folder_structure(i_path, numb_of_tabs + 1)
            else:
                logging.info(f'{tab}File: {i}')

    def save_all_data_to_zip(self):
        """ This method saves all data in the 'new_path' directory to a ZIP archive. """
        os.chdir(self.args.destination)
        shutil.make_archive('data', 'zip', fr'{self.new_path}')


if __name__ == '__main__':
    user_data = UserData()
    # (1) Setting up new file logger
    user_data.configure_logger()
    # (2) Downloading some data by URL
    user_data.download_user_data()
    user_data.get_user_data_from_csv()
    # (4) Sorting data by key
    user_data.sort_data()
    # (5) Adding some fields to the file and saving data to csv
    user_data.add_and_change_some_data()
    user_data.save_data_to_csv()
    # (6-7) Creating a new directory and assigning it to a working directory
    user_data.create_new_working_dir()
    # (8) Rearranging the data
    user_data.rearrange_the_data()
    # (9-11) Creating sub folders with special data
    user_data.create_sub_folders_and_save_some_data()
    # (12) Removing the data before 1960-th
    user_data.delete_decades_before_1960th()
    # (13) Logging full folder structure
    user_data.log_full_folder_structure(user_data.new_path)
    # (14) Archiving the destination folder
    user_data.save_all_data_to_zip()
