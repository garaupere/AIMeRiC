import json
import os
from collections import defaultdict, Counter

path = '../escansor/results/'
#path = '__test/results/'
cv_info_fq = {}
for file in os.listdir(path):
    if file.endswith('.json'):
        frequencies = defaultdict(Counter)
        cv_info_fq[file.replace('.json', '')] = {}
        data = json.load(open(path + file, encoding='utf-8'))
        for book in data['books']:
            if book != "n_verses":
                for poem in data['books'][book]['poems']:
                     for verse in data['books'][book]['poems'][poem]['verses']:
                        contactes = data['books'][book]['poems'][poem]['verses'][verse]['cv_info']
                        for key, values in contactes.items():
                            for value in values:
                                frequencies[key][value] += 1
        for key, counter in frequencies.items():
            #print(f"{key}:")
            key_lev = {}
            for cadena, freq in counter.items():
                #print(f"  {cadena}: {freq}")
                key_lev.update({cadena: freq})
                cv_info_fq[file.replace('.json', '')].update({key: key_lev})
print(cv_info_fq)

with open(path + 'cv_info_fq.cv_info', 'w', encoding='utf-8') as f:
    f.write('author,contacte,valor,freq\n')
    for author, contactes in cv_info_fq.items():
        for contacte, values in contactes.items():
            for value, freq in values.items():
                f.write(f"{author},{contacte},{value},{freq}\n")


