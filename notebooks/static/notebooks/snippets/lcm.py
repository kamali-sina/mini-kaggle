from functools import reduce
from math import gcd


def lcm(numbers):
    return reduce((lambda x, y: int(x * y / gcd(x, y))), numbers)


lcm([12, 7])  # 84
lcm([1, 3, 4, 5])  # 60
