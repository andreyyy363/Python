from random import randint

print('Lab_1')
print('Var_15')
print('-----------------------------------')


# Generating array
def generate_random_array(row, col):
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
def find_zero(arr):
    found = False
    line = 0
    for i in arr:
        line += 1
        for j in i:
            if j == 0:
                print(f"First null element found in  {line} line.")
                found = True
                break
        if found:
            break
    if not found:
        print('Null elements not found.')
    print('-----------------------------------')


# Exercise 2
def find_sum_of_negative_paired_elements(arr):
    sum_of_elements = []
    for i in arr:
        for j in i:
            if j < 0 and j % 2 == 0:
                sum_of_elements.append(j)

    sum_of_elements.sort()
    print('Sum of even negative elements\narranged in descending order:')
    print(sum_of_elements)
    print('-----------------------------------')


n = input('Enter the number of rows: ')
m = input('Enter the number of columns: ')
array = generate_random_array(int(n), int(m))
print_array(array)
find_zero(array)
find_sum_of_negative_paired_elements(array)
