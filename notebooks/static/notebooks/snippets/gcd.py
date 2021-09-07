from functools import reduce
from math import gcd as _gcd


def gcd(numbers):
    return reduce(_gcd, numbers)


gcd([8, 36, 28])  # 4
