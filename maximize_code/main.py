import scipy.optimize
import numpy as np

arr_of_factors = [0, 2, 3]


def f(price):
    sales = price * arr_of_factors[0]
    for i in range(1, len(arr_of_factors)):
        sales += arr_of_factors[i]
    return sales


def g(arr_of_price):
    result = 0
    for i in range(0, len(arr_of_price)):
        result += f(arr_of_price[i]) * arr_of_price[i]
    return result


x0 = np.array([0, 0, 0])

max_x = scipy.optimize.minimize(lambda x: -g(x), x0)

print(g(max_x.x))



