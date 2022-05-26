import math
import scipy.optimize
import numpy as np

def to_date(lin):
    day = lin[0] + lin[1]
    month = lin[3] + lin[4]
    year = lin[6] + lin[7]
    return year + month + day


class product:
    params = [-1, -1]
    percent = 0
    product_id = 0
    store_id = 0
    product_number = 0
    last_price = 0
    min_price = -1
    purchase_price = 0
    max_price = -1

    def percentCounter(self):
        self.percent = self.last_price / 100.0;

    def minPriceCounter(self):
        self.min_price = max(self.last_price - 50 * self.percent, self.purchase_price)

    def maxPriceCounter(self):
        self.max_price = min(self.last_price + 50 * self.percent, self.purchase_price * 2)

type_of_model = ''
model_file = ''
output_file = ''
type_of_optimization = ''
step = 0
start = 1.0
bound_mar_rev_min = -1e18
bound_mar_rev_max = 1e18
number_of_steps = 1

def getInfo():
    global type_of_model
    type_of_model = input("Print model type: ")
    global model_file
    model_file = input("Print name of the model file: ")
    global output_file
    output_file = input("Print name of the output file: ")
    global type_of_optimization
    type_of_optimization = input("Print type of optimization: ")
    global start
    start = float(input("Print start of optimization number: "))
    global step
    if(type_of_optimization == 'revenue'):
        step = float(input("Print margin bounds coef: "))
    if (type_of_optimization == 'margin'):
        step = float(input("Print revenue bounds coef: "))
    global number_of_steps
    number_of_steps = int(input("Print number of steps: "))

getInfo()
fil = open(output_file, 'w')



products_dict = dict()
# начало парсинга
f = open('COSTS.txt', 'r')
a = f.readlines()
names = dict()
for i in range(1, len(a)):
    s = a[i]
    s = list(s.split('"'))
    s = s[1::2]
    s[0] = int(s[0])
    s[0] = 100 * s[0] + int(s[3][2::])
    products_dict[s[0]] = product()
    products_dict[s[0]].purchase_price = float(s[1])
    products_dict[s[0]].store_id = s[3]
    products_dict[s[0]].product_id = s[0] // 100
# вторая таблица
f = open('INVENTORY_HISTORY.txt', 'r')
a = f.readlines()
res = []
for i in range(1, len(a)):
    s = a[i]
    s = list(s.split('"'))
    s = s[1::2]
    s[0] = int(s[0])
    res.append(s)
res = sorted(res, key=lambda x: to_date(x[1]))
for i in range(0, len(res)):
    res[i][0] = 100 * res[i][0] + int(res[i][3][2::])
    if (not (res[i][0] in products_dict.keys())):
        products_dict[res[i][0]] = product()
        products_dict[res[i][0]].product_id = res[i][0] // 100
    products_dict[res[i][0]].product_number = float(res[i][2])

# третья таблица

f = open('PRICES_HISTORY_DAILY.txt', 'r')
a = f.readlines()
res = []
for i in range(1, len(a)):
    s = a[i]
    s = list(s.split(';'))
    s[0] = int(s[0])
    res.append(s)
res = sorted(res, key=lambda x: to_date(x[1]))
for i in range(0, len(res)):
    res[i][0] = 100 * res[i][0] + int(res[i][4][2::])
    if (res[i][3] != "PROMO"):
        if (not (res[i][0] in products_dict.keys())):
            products_dict[res[i][0]] = product()
            products_dict[res[i][0]].product_id = res[i][0] // 100
        products_dict[res[i][0]].last_price = float(res[i][2])

for i in products_dict.keys():
    products_dict[i].percentCounter()
    products_dict[i].minPriceCounter()
    products_dict[i].maxPriceCounter()

# таблица формул

f = open(model_file, 'r')
a = f.readlines()
res = []
for i in range(1, len(a)):
    s = a[i]
    s = list(s.split(','))
    s[2] = int(s[2]) * 100 + 1 + int(s[3])
    products_dict[s[2]].params = [float(s[0]), float(s[1])]

can_opt = []
for i in products_dict.keys():
    if (products_dict[i].min_price != -1 and products_dict[i].max_price != -1 and products_dict[i].params != [-1, -1]):
        can_opt.append(i);

def val(curr_price, pr_id):
    if(type_of_model == 'linear'):
        m = curr_price + 5
        return max(0, products_dict[pr_id].params[0] + m * products_dict[pr_id].params[1])

    if(type_of_model == 'log10'):
        if (curr_price + 5 <= 0):
            return -1e9
        mlog = -1e18
        if (curr_price + 5 >= 1):
            mlog = math.log10(curr_price + 5)
        return max(0, products_dict[pr_id].params[0] + mlog * products_dict[pr_id].params[1])

    if (type_of_model == 'loge'):
        if (curr_price + 5 <= 0):
            return -1e9
        mlog = -1e18
        if (curr_price + 5 >= 1):
            mlog = math.log(curr_price + 5)
        return max(0, products_dict[pr_id].params[0] + mlog * products_dict[pr_id].params[1])


def revenue(curr_price):
    if (type_of_optimization == 'revenue'):
        if (-margin(curr_price) > bound_mar_rev_max or -margin(curr_price) < bound_mar_rev_min):
            return 1e9
    res = 0
    for i in range (len(can_opt)):
        res += val(curr_price[i], can_opt[i]) * curr_price[i]
    return -res

def margin(curr_price):
    if(type_of_optimization == 'margin'):
        if(-revenue(curr_price) > bound_mar_rev_max or -revenue(curr_price) < bound_mar_rev_min):
            return 1e9
    res = 0
    for i in range (len(can_opt)):
        res += val(curr_price[i], can_opt[i]) * (curr_price[i]-products_dict[can_opt[i]].purchase_price)
    return -res

curr_prices = []
first_price = []
elements_bounds = ()


for i in can_opt:
    curr_prices.append(float (products_dict[i].min_price) + 0.000001)
    first_price.append(products_dict[i].last_price)
    if(products_dict[i].min_price >= products_dict[i].max_price):
        products_dict[i].min_price, products_dict[i].max_price = products_dict[i].max_price, products_dict[i].min_price
    elements_bounds = elements_bounds + ((products_dict[i].min_price, products_dict[i].max_price), )
first_price = np.array(first_price)
fil.write('[')
fil.write(str(-revenue(first_price)) + ",")
fil.write(str(-margin(first_price)) + ",")
margin0 = margin(first_price)
revenue0 = revenue(first_price)
for i in range(number_of_steps):
    if (type_of_optimization == 'revenue'):
        bound_mar_rev_max = - (start + step) * margin0  # вычисляем ограничение на margin на данном шаге
        bound_mar_rev_min = - start * margin0
        for j in range(len(can_opt)):  # находим набор цен для которых margin попадает в ограничения
            # пытаемся увеличить цену на товар с целью увеличения margin и его попадания в границы
            while ((curr_prices[j] - products_dict[can_opt[j]].purchase_price) * val(curr_prices[j], can_opt[j]) <
                   (curr_prices[j] + products_dict[can_opt[j]].max_price / 1000 - products_dict[
                       can_opt[j]].purchase_price) *
                   val(curr_prices[j] + products_dict[can_opt[j]].max_price / 1000, can_opt[j]) and
                   -margin(np.array(curr_prices)) <
                   (bound_mar_rev_min + bound_mar_rev_max) / 2 and
                   (curr_prices[j] + products_dict[can_opt[j]].max_price / 1000) < products_dict[can_opt[j]].max_price):
                curr_prices[j] += products_dict[can_opt[j]].max_price / 1000
            # пытаемся уменьшить цену на товар с целью увеличения margin и его попадания в границы
            while ((curr_prices[j] - products_dict[can_opt[j]].purchase_price) * val(curr_prices[j], can_opt[j]) <
                   (curr_prices[j] - products_dict[can_opt[j]].max_price / 1000 - products_dict[
                       can_opt[j]].purchase_price) *
                   val(curr_prices[j] - products_dict[can_opt[j]].max_price / 1000, can_opt[j]) and
                   -margin(np.array(curr_prices)) <
                   (bound_mar_rev_min + bound_mar_rev_max) / 2 and
                   (curr_prices[j] - products_dict[can_opt[j]].max_price / 1000) >
                   products_dict[can_opt[j]].min_price):
                curr_prices[j] -= products_dict[can_opt[j]].max_price / 1000
        max_x = scipy.optimize.minimize(revenue, np.array(curr_prices), bounds=elements_bounds) # находим допустимый набор цен с наибольшим revenue

    if (type_of_optimization == 'margin'):
        bound_mar_rev_max = - (start + step) * revenue0  # вычисляем ограничение на revenue на данном шаге
        bound_mar_rev_min = - start * revenue0
        for j in range(len(can_opt)):  # находим набор цен для которых revenue попадает в ограничения
            # пытаемся увеличить цену на товар с целью увеличения revenue и его попадания в границы
            while ((curr_prices[j]) * val(curr_prices[j], can_opt[j]) <
                   (curr_prices[j] + products_dict[can_opt[j]].max_price / 1000) *
                   val(curr_prices[j] + products_dict[can_opt[j]].max_price / 1000, can_opt[j]) and
                   -margin(np.array(curr_prices)) <
                   (bound_mar_rev_min + bound_mar_rev_max) / 2 and
                   (curr_prices[j] + products_dict[can_opt[j]].max_price / 1000) < products_dict[can_opt[j]].max_price):
                curr_prices[j] += products_dict[can_opt[j]].max_price / 1000
            # пытаемся уменьшить цену на товар с целью увеличения revenue и его попадания в границы
            while ((curr_prices[j]) * val(curr_prices[j], can_opt[j]) <
                   (curr_prices[j] - products_dict[can_opt[j]].max_price / 1000) *
                   val(curr_prices[j] - products_dict[can_opt[j]].max_price / 1000, can_opt[j]) and
                   -margin(np.array(curr_prices)) <
                   (bound_mar_rev_min + bound_mar_rev_max) / 2 and
                   (curr_prices[j] - products_dict[can_opt[j]].max_price / 1000) >
                   products_dict[can_opt[j]].min_price):
                curr_prices[j] -= products_dict[
                                      can_opt[j]].max_price / 1000
        max_x = scipy.optimize.minimize(margin, np.array(curr_prices), bounds=elements_bounds)  # находим допустимый набор цен с наибольшим margin
    new_x = max_x.x
    for j in range(len(can_opt)):
        if(abs(new_x[j]-products_dict[can_opt[j]].last_price) < products_dict[can_opt[j]].percent):
            new_x[j]=products_dict[can_opt[j]].last_price
    fil.write(str(-revenue(new_x)) + ",")
    fil.write(str(-margin(new_x)) + ",")
    start += step
fil.write(']')