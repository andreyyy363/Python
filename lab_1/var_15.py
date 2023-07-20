from random import randint

print('Lab_1')
print('Var_15')
print('-----------------------------------')


# Generating array
def generating_random_array(row, col):
    # Random generating
    return [[randint(-10, 10) for _ in range(col)] for _ in range(row)]


# Printing array
def print_array(arr):
    print('Random array:')
    print('-----------------------------------')
    output = '\n'.join([' '.join(f'{j:4}' for j in i) for i in arr])
    print(output)
    print('-----------------------------------')


# Exercise 1
def find_zero(arr, row, col):
    found = False
    for i in range(row):
        for j in range(col):
            if arr[i][j] == 0:
                print(f"First null element found in  {i + 1} line.")
                found = True
                break
        if found:
            break
    if not found:
        print('Null elements not found.')
    print('-----------------------------------')


# Exercise 2
def sum_of_negative_paired_elements(arr, row, col):
    sum_of_elements = [0] * row
    for i in range(row):
        for j in range(col):
            if arr[i][j] < 0 and arr[i][j] % 2 == 0:
                sum_of_elements[i] += arr[i][j]

    sum_of_elements.sort()
    print('Sum of even negative elements\narranged in descending order:')
    print(sum_of_elements)
    print('-----------------------------------')


n = input('Enter the number of rows: ')
m = input('Enter the number of columns: ')
array = generating_random_array(int(n), int(m))
print_array(array)
find_zero(array, int(n), int(m))
sum_of_negative_paired_elements(array, int(n), int(m))
