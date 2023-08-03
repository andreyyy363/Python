import requests
import csv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import Counter
import copy


class MovieData:
    API_PATH = 'https://api.themoviedb.org/3'
    GENRE_URL = f'{API_PATH}/genre/movie/list?language=en'
    DATA_URL = API_PATH + '/discover/movie?include_adult=false&include_video=false&sort_by=popularity.desc&page={!!!!}'
    HEADERS = {
        'accept': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8'
    }
    FIELDNAMES = ['title', 'popularity', 'score', 'release_date', 'last_day_in_cinema']

    def __init__(self, numb_of_pages):
        self.genres = None
        self.genre_dict = None
        self.genre_names = None
        self.pages = numb_of_pages
        self.data = []

    def fetch_all_data_in_pages(self):
        for i in range(self.pages):
            response = requests.get(self.DATA_URL, params={'page': i + 1}, headers=self.HEADERS)
            self.data.extend(response.json()['results'])

    def give_data(self):
        return self.data

    def give_data_with_indexes(self):
        return self.data[3:19:4]

    def find_popular_title(self):
        return max(self.data, key=lambda x: x['popularity'])['original_title']

    def find_film_with_keyword(self, keyword):
        return [j['original_title'] for j in self.data if keyword in j['overview']]

    def get_genres_data(self):
        response = requests.get(self.GENRE_URL, headers=self.HEADERS)
        self.genres = response.json()['genres']
        self.genre_dict = {i['id']: i['name'] for i in self.genres}

    def get_unique_collections(self):
        all_genres = set()
        genre_names = [self.genre_dict[j] for i in self.data for j in i['genre_ids'] if j in self.genre_dict]
        all_genres.update(genre_names)
        self.genre_names = {genre['id']: genre['name'] for genre in self.genres}
        return all_genres

    def delete_films_with_genre(self, genre_name_for_delete):
        genre_id_for_delete = next(i['id'] for i in self.genres if i['name'].lower() == genre_name_for_delete.lower())
        self.data = [i for i in self.data if genre_id_for_delete not in i['genre_ids']]
        return self.data

    def find_most_popular_genre(self):
        all_genres = [genre_id for i in self.data for genre_id in i['genre_ids']]
        popular_genres = [{'genre_name': self.genre_names[i], 'count': count}
                          for i, count in Counter(all_genres).most_common()]
        return popular_genres

    def get_grouped_film_collection(self):
        film_collections = [[film_1, film_2] for i, film_1 in enumerate(self.data) for film_2 in self.data[i + 1:]
                            if set(film_1['genre_ids']) & set(film_2['genre_ids'])]
        return film_collections

    def get_copy_and_modified_copy(self):
        broken_data = copy.deepcopy(self.data)
        for j in broken_data:
            j['genre_ids'][0] = 22 if j['genre_ids'] else j['genre_ids'].append(22)
        return self.data, broken_data

    def format_film_data(self, i):
        title = i['original_title']
        popularity = format(i['popularity'], '.1f')
        score = format(i['vote_average'], '.0f')
        release_date = datetime.strptime(i['release_date'], '%Y-%m-%d')
        day_in_cinema = release_date + relativedelta(months=2) + timedelta(days=14)

        return {
            'title': title,
            'popularity': popularity,
            'score': score,
            'release_date': release_date.date(),
            'last_day_in_cinema': day_in_cinema.date()
        }

    def get_some_data_to_file(self):
        film_collection = list(map(self.format_film_data, self.data))
        return film_collection.sort(key=lambda x: (x['score'], x['popularity']))

    def save_some_data_to_file(self, film_collection, path_to_file):
        with open(path_to_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            writer.writerows(film_collection)


print('Lab_2')
print('-----------------------------------------------------------------------------------------------')
pages = input("Please, enter the number of pages you want to work with: ")
movies = MovieData(int(pages))
# (1) Fetch the data from desired amount of pages.
movies.fetch_all_data_in_pages()
# (2) Give all data
movies.give_data()
# (3) Give all data about movies with indexes from 3 till 19 with step 4
movies.give_data_with_indexes()
# (4) Get name of the most popular title
movies.find_popular_title()
# (5) Get names of titles which has in description keywords which a user put as parameters
word = input('Please, enter the keyword for which you want to search for a movie: ')
movies.find_film_with_keyword(word)
# (6) Get unique collection of present genres
movies.get_genres_data()
movies.get_unique_collections()
# (7) Delete all movies with user provided genre
genre_name = input('Please, enter the name of the genre you want to delete: ')
movies.delete_films_with_genre(genre_name)
# (8) Get names of most popular genres with numbers of time they appear in the data
movies.find_most_popular_genre()
# (9) Get collection of film titles  grouped in pairs by common genres
movies.get_grouped_film_collection()
# (10) Return initial data and copy of initial data where first id in list of film genres was replaced with 22
movies.get_copy_and_modified_copy()
# (11 - 12) Get collection of structures with part of initial data and write information to a csv file using path
path = input('Please, enter the path to the file you want to save this (Example: C: Path to file): ')
movies.save_some_data_to_file(movies.get_some_data_to_file(), path)
