print('Lab_1')
print('Var_5')
print('-----------------------------------')


# Generating array
def generating_random_array(s):
    # Random generating
    from random import randint
    arr = [[randint(-5, 10) for _ in range(s)] for _ in range(s)]
    return arr


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
def sum_of_positive_elements(arr, arr_size):
    sum_of_positive = [0] * arr_size
    for j in range(arr_size):
        for i in range(arr_size):
            if arr[i][j] >= 0:
                sum_of_positive[j] += arr[i][j]
            else:
                sum_of_positive[j] = 0
                break
    print('Sum of positive elements in columns:')
    print(sum_of_positive)
    print('-----------------------------------')
    return sum_of_positive


# Exercise 2
def min_sum(arr, arr_size):
    sum_of_diagonals = [0] * (2 * arr_size - 1)
    diagonal_index = None
    for k in range(2 * arr_size - 1):
        if k != arr_size - 1:
            sum_of_diagonals[k] = 0
            j = k
            for i in range(k + 1):
                if i + j == k and j < arr_size and i < arr_size:
                    sum_of_diagonals[k] += abs(arr[i][j])
                j -= 1
        else:
            diagonal_index = k
    sum_of_diagonals.pop(diagonal_index)

    min_s = sum_of_diagonals[0]
    for k in range(2 * arr_size - 2):
        if min_s > sum_of_diagonals[k]:
            min_s = sum_of_diagonals[k]
    print('Sums of diagonal elements parallel\nto the side diagonal:')
    print(sum_of_diagonals, '- min:', min_s)
    print('-----------------------------------')
    return min_s
