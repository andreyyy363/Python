from random import randint

print('Lab_1')
print('Var_20')
print('-----------------------------------')


# Generating array
def generating_random_array(row, col):
    # Random generating
    return [[randint(-10, 10) for _ in range(col)] for _ in range(row)]


# Printing array
def print_array(arr):
    print('Random array:')
    print('-----------------------------------')
    for i in arr:
        for j in i:
            print(f'{j:4}', end=' ')
        print()
    print('-----------------------------------')


# Exercise 1
def find_zero(arr, row, col):
    line = 0
    for i in arr:
        line += 1
        count = 0
        found = False
        for j in i:
            if j == 0:
                found = True
            if j < 0:
                count += 1

            print(f"Found {count} negative elements in series with 0 in {line} line." if found else f"There are no negative elements in series with 0 in {line} line.")


    print('-----------------------------------')


# Exercise 2
def saddle_points(arr, row, col):
    found = False
    print('Matrix saddle points:')
    for i in range(row):
        for j in range(col):
            min_index = 0
            min_value = 0
            for k in range(1, col):
                if arr[i][k] < min_value:
                    min_index = k
                    min_value = arr[i][k]

            max_index = 0
            max_value = 0
            for k in range(1, row):
                if arr[k][j] > max_value:
                    max_index = k
                    max_value = arr[k][j]

            if max_index == i and min_index == j:
                print('[', i + 1, '.', j + 1, ']:', arr[i][j])
                found = True

    if not found:
        print('There are no saddle points.')


n = input('Enter the number of rows: ')
m = input('Enter the number of columns: ')
array = generating_random_array(int(n), int(m))
print_array(array)
find_zero(array, int(n), int(m))
saddle_points(array, int(n), int(m))
