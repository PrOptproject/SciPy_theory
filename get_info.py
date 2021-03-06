import math
import scipy.optimize
import numpy as np

def to_date(lin):
    day = lin[0]+lin[1]
    month = lin[3]+lin[4]
    year = lin[6] + lin[7]
    return year + month + day

class product:
    params = [-1,-1]
    percent = 0
    product_id = 0
    store_id = 0
    product_number = 0
    last_price = 0
    min_price = -1
    purchase_price = 0
    max_price = -1
    def percentCounter(self):
        self.percent = self.purchase_price / 100.0;
    def minPriceCounter(self):
        self.min_price = max(self.last_price - 50 * self.percent, self.purchase_price)
    def maxPriceCounter(self):
        self.max_price = min(self.last_price + 50 * self.percent, self.purchase_price * 2)
    
     
d = dict()
# начало парсинга
f = open('COSTS.txt','r')
a = f.readlines()
for i in range(1,len(a)):
    s=a[i]
    s = list(s.split('"'))
    s = s[1::2]
    s[0]=int(s[0])
    s[0] = 100 * s[0] + int(s[3][2::])
    d[s[0]] = product()
    d[s[0]].purchase_price = float(s[1])
    d[s[0]].store_id = s[3]
    d[s[0]].product_id = s[0]//100
# вторая таблица
f = open('INVENTORY_HISTORY.txt','r')
a = f.readlines()
res=[]
for i in range(1,len(a)):
    s=a[i]
    s = list(s.split('"'))
    s = s[1::2]
    s[0]=int(s[0])
    res.append(s)
res = sorted(res, key = lambda x: to_date(x[1]))
for i in range(0,len(res)):
     res[i][0] = 100 * res[i][0] + int(res[i][3][2::])
     if(not (res[i][0] in d.keys())):
         d[res[i][0]] = product()
         d[res[i][0]].product_id = res[i][0]//100
     d[res[i][0]].product_number = float(res[i][2])
     
# третья таблица
     
f = open('PRICES_HISTORY_DAILY.txt','r')
a = f.readlines()
res=[]
for i in range(1,len(a)):
    s=a[i]
    s = list(s.split(';'))
    s[0]=int(s[0])
    res.append(s)
res = sorted(res, key = lambda x: to_date(x[1]))
for i in range(0,len(res)):
    res[i][0] = 100 * res[i][0] + int(res[i][4][2::])
    if(res[i][3] != "PROMO"):
        if(not (res[i][0] in d.keys())):
            d[res[i][0]] = product()
            d[res[i][0]].product_id = res[i][0]//100
        d[res[i][0]].last_price = float(res[i][2])
         
         
for i in d.keys():
    d[i].percentCounter()
    d[i].minPriceCounter()
    d[i].maxPriceCounter()
    #d[i].min_price = max(d[i].min_price(),abs((d[i].product_number/7-d[i].params[1])/d[i].params[0]))

#таблица формул

f = open('third1.txt','r')
a = f.readlines()
res=[]
for i in range(1,len(a)):
    s=a[i]
    s = list(s.split(','))
    s[2]=int(s[2])*100 + 1 + int(s[3])
    d[s[2]].params=[float(s[0]),float(s[1])]

can_opt = []
for i in d.keys():
    if(d[i].min_price != -1 and d[i].max_price != -1 and d[i].params != [-1,-1]):
        can_opt.append(i);
def val(x,pr_id):
    return d[pr_id].params[0] + math.log(x) * d[pr_id].params[1]

def f(*args):
    res=0
    for i in (len(can_opt)):
        res +=val(args[i],can_opt[i]) * args[i]
    return -res

x0 = []
bounds=[]
for i in can_opt:
    x0.append((d[i].min_price+d[i].max_price)//2)
    bounds.append(scipy.optimize.Bounds(d[i].min_price,d[i].max_price))
max_x = scipy.optimize.minimize(lambda x: f, x0)
