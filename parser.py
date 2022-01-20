f = open('name.txt','r')
a = f.readlines()
res=[]
for i in range(1,len(a)):
    s=a[i]
    s = list(s.split('"'))
    s = s[1::2]
    s[0]=int(s[0])
    res.append(s)
print(res)

# парсер в массив для большинства файлов(сначала надо а txt перевести)

# для prices_history_daily надо
# '"' заменить на ';'
# и убрать s = s[1::2]
