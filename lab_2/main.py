import requests
import textwrap
import csv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pprint import pprint
from collections import Counter


class MovieData:
    api_path = 'https://api.themoviedb.org/3'
    genre_url = f'{api_path}/genre/movie/list?language=en'
    data_url = api_path + '/discover/movie?include_adult=false&include_video=false&sort_by=popularity.desc&page={!!!!}'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8'
    }

    def __init__(self):
        pages = input("Please, enter the number of pages you want to work with: ")
        self.pages = int(pages)

    def fetch_some_data(self, print_with_indexes):
        params = {'page': 1}
        data = {}
        if print_with_indexes:
            start_index = 3
            ebd_index = 19
            step = 4
        else:
            start_index = None
            ebd_index = None
            step = None

        for i in range(self.pages):
            response = requests.get(self.data_url, params=params, headers=self.headers)
            data = response.json()
            print(f"\nPage {data['page']}")
            count = 1
            for j in data['results'][start_index:ebd_index:step]:
                print(f"Film #{count}")
                print('*' * 95)
                print('The title of the movie:')
                print(j['original_title'])
                print('-' * 95)
                print('Brief description:')
                for overview in textwrap.wrap(j['overview'], width=95):
                    print(overview)
                print('*' * 95)
                count += 1
            params['page'] += 1
        return data

    def fetch_all_data(self):
        params = {'page': 1}
        data = {}
        for i in range(self.pages):
            response = requests.get(self.data_url, params=params, headers=self.headers)
            data = response.json()
            data.update(response.headers)
            pprint(data)
        return data

    def find_popular_title(self):
        params = {'page': 1}
        popular_title = None
        max_popularity = float('-inf')
        while True:
            response = requests.get(self.data_url, params=params, headers=self.headers)
            data = response.json()
            for j in data['results']:
                current_popularity = j['popularity']
                if current_popularity > max_popularity:
                    max_popularity = current_popularity
                    popular_title = j['original_title']
            if params['page'] < self.pages:
                params['page'] += 1
            else:
                break
        print(f"Name of the most popular title: {popular_title} ({max_popularity})")
        return popular_title

    def find_film_with_keyword(self):
        keyword = input('Please, enter the keyword for which you want to search for a movie: ')
        print('Movies in which the keyword is found:')
        params = {'page': 1}
        title_list = []
        for i in range(self.pages):
            response = requests.get(self.data_url, params=params, headers=self.headers)
            data = response.json()
            for j in data['results']:
                if keyword in j['overview']:
                    title_list = j['original_title']
                    print(j['original_title'])
        return title_list

    def get_unique_collections(self):
        response = requests.get(self.genre_url, headers=self.headers)
        genres = response.json()
        print('Unique film genres:')
        for i in genres['genres']:
            print(f"{i['name']} (id:{i['id']})")
        return genres

    def delete_films_with_genre(self):
        data = {}
        genre_name_for_delete = input('Please, enter the name of the genre you want to delete: ')
        genre_id_for_delete = None
        params = {'page': 1}
        response = requests.get(self.genre_url, headers=self.headers)
        genres = response.json()
        for i in genres['genres']:
            if i['name'].lower() == genre_name_for_delete.lower():
                genre_id_for_delete = i['id']

        print('Films without deleted genre: ')
        for i in range(self.pages):
            response = requests.get(self.data_url, params=params, headers=self.headers)
            data = response.json()
            print(f"\nPage {data['page']}")
            count = 0
            for j in data['results']:
                if genre_id_for_delete in j['genre_ids']:
                    data['results'].pop(count)
                    count += 1
            pprint(data)
        return data

    def find_most_popular_genre(self):
        params = {'page': 1}
        response = requests.get(self.genre_url, headers=self.headers)
        genres = response.json()
        genre_names = {}
        all_genres = []

        for i in range(self.pages):
            response = requests.get(self.data_url, params=params, headers=self.headers)
            data = response.json()
            for j in data['results']:
                all_genres += j['genre_ids']

        for j in genres['genres']:
            genre_names[j['id']] = j['name']

        most_common_genres = Counter(all_genres).most_common()

        for i, count in most_common_genres:
            popular_genre_names = genre_names.get(i)
            print(f"Genre {popular_genre_names} found {count} times.")

    def get_grouped_film_collection(self):
        params = {'page': 1}
        data = {}
        for i in range(self.pages):
            response = requests.get(self.data_url, params=params, headers=self.headers)
            data = response.json()
        response = requests.get(self.genre_url, headers=self.headers)
        genres = response.json()
        genre_names = {}

        for j in genres['genres']:
            genre_names[j['id']] = j['name']

        sorted_film = {}
        for i in data['results']:
            for j in i['genre_ids']:
                if j not in sorted_film:
                    sorted_film[j] = []
                sorted_film[j].append(i['title'])

        for genre_id, titles in sorted_film.items():
            print(f"{genre_names[genre_id]}:")
            for i in titles:
                print(f" - {i}")
        return sorted_film

    def get_some_data_to_file(self):
        params = {'page': 1}
        film_collection = []
        for i in range(self.pages):
            response = requests.get(self.data_url, params=params, headers=self.headers)
            data = response.json()
            for j in data['results']:
                title = j['original_title']
                popularity = format(j['popularity'], '.1f')
                score = format(j['vote_average'], '.0f')
                release_date = datetime.strptime(j['release_date'], '%Y-%m-%d')
                day_in_cinema = release_date
                day_in_cinema += relativedelta(months=2) + timedelta(days=14)
                film_data = {
                    'title': title,
                    'popularity': popularity,
                    'score': score,
                    'release_date': release_date.date(),
                    'last day in cinema': day_in_cinema.date()
                }
                film_collection.append(film_data)
                print('')
                print('*' * 95)
                print(f"The title of the movie: {title}")
                print(f"Popularity: {popularity}")
                print(f"Score: {score}")
                print(f"Release date: {release_date.date()}")
                print(f"Last day in cinema: {day_in_cinema.date()}")
                print('*' * 95)
            params['page'] += 1
        film_collection.sort(key=lambda x: (x['score'], x['popularity']))
        return film_collection

    def get_copy_and_modified_copy(self):
        params = {'page': 1}
        data = {}
        broken_data = {}
        for i in range(self.pages):
            response = requests.get(self.data_url, params=params, headers=self.headers)
            data = response.json()
            broken_data = data
            for j in broken_data['results']:
                j['genre_ids'][0] = 22
        pprint(broken_data)
        return data, broken_data

    def save_some_data_to_file(self, film_collection):
        path_to_file = input('Please, enter the path to the file you want to save this (Example: C: Path to file): ')
        with open(path_to_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'popularity', 'score', 'release_date', 'last day in cinema']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(film_collection)
        print('Successful!')

    def print_menu(self):
        print('-' * 95)
        print('Actions with the movie database:')
        print('-' * 95)
        print('[1]  - Fetch the data from desired amount of pages.')
        print('[2]  - Fetch all data.')
        print('[3]  - Fetch all data about movies with indexes from 3 till 19 with step 4.')
        print('[4]  - Get a name of the most popular title.')
        print('[5]  - Get a names of titles which has in description key words.')
        print('[6]  - Get a unique collection.')
        print('[7]  - Delete all movies with a specified genre.')
        print('[8]  - Get names of most popular genres with numbers of time the appear in the data.')
        print('[9]  - Get collection of film titles  grouped in pairs by common genres.')
        print('[10] - Return and copy initial data where first id in list of film genres was replaced with 22.')
        print('[11] - Get collection of structures with part of initial data and write it to a csv file.')
        print('[12] - Stop program.')
        print('-' * 95)

    def choose_action(self):
        while True:
            self.print_menu()
            choice = input('Please, enter your choice: ')
            if int(choice) == 1:
                self.fetch_some_data(False)

            elif int(choice) == 2:
                self.fetch_all_data()

            elif int(choice) == 3:
                self.fetch_some_data(True)

            elif int(choice) == 4:
                self.find_popular_title()

            elif int(choice) == 5:
                self.find_film_with_keyword()

            elif int(choice) == 6:
                self.get_unique_collections()

            elif int(choice) == 7:
                self.delete_films_with_genre()

            elif int(choice) == 8:
                self.find_most_popular_genre()

            elif int(choice) == 9:
                self.get_grouped_film_collection()

            elif int(choice) == 10:
                self.get_copy_and_modified_copy()

            elif int(choice) == 11:
                self.save_some_data_to_file(self.get_some_data_to_file())

            elif int(choice) == 12:
                break


print('Lab_2')
print('-----------------------------------------------------------------------------------------------')

movies = MovieData()
movies.choose_action()
