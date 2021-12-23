# SciPy_theory

Библиотека SciPy.

Функция scipy.optimize.minimize (при необходимости можно минимизировать -f(x))

Вид scipy.optimize.minimize(fun, x0, args=(), method=..., bounds=None)

fun - функция которую надо оптимизировать.

x0 - можно указать начальное значение для параметров функции.

args - доп аргументы для функции.

method - выбор метода оптимизации (понадобится когда можно будет понять примерный вид функции).

bounds - обьект класса bounds задающий пары min,max для каждой переменной.

Функция также принимает множество других параметров, которые зависят от выбранного способа оптимизации.
