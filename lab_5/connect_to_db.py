import sqlite3
from functools import wraps


def connect_to_database(func):
    @wraps(func)
    def wrap_func(*args, **kwargs):
        connection = sqlite3.connect('bank.db')
        cursor = connection.cursor()

        result = func(cursor, *args, **kwargs)

        connection.commit()
        connection.close()

        return result

    return wrap_func
