
import collections
def get_key(key):
    try:
        return int(key)
    except ValueError:
        return key
a = {'100':12,'6':5,'88':3,'test':34, '67':7,'1':64 }
b = collections.OrderedDict(sorted(a.items(), key=lambda t: get_key(t[0])))
print(b)