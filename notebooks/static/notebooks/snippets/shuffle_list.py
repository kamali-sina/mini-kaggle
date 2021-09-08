from copy import deepcopy
from random import randint


def shuffle(lst):
    temp_lst = deepcopy(lst)
    counter = len(temp_lst)
    while counter:
        counter -= 1
        i = randint(0, counter)
        temp_lst[counter], temp_lst[i] = temp_lst[i], temp_lst[counter]
    return temp_lst


foo = [1, 2, 3]
shuffle(foo)  # [2, 3, 1], foo = [1, 2, 3]
