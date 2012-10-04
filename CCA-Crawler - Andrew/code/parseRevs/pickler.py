import cPickle
import string
import csv
import sys
import time

#helper removes whitespaces and punctuations (including symbols)
def normalize (s):
    return s.replace(" ", "").translate(string.maketrans("", ""), string.punctuation).lower()

file = sys.argv[1]
hash = {}
t1 = time.time()
with open(file, 'rb') as f:
    print "pickling..."
    reader = csv.reader(f)
    keys = reader.next()
    hash = dict.fromkeys(keys, [])  #use first row of fields as sequence of keys for dict
    row_count = 0
    for row in reader:
        row_count += 1
        t2 = time.time()
        if (t2 - t1) > 60:
            print "on row: ", row_count
            t1 = t2
        hash[keys[0]] = hash[keys[0]] + [normalize(row[0])]     #product_name
        hash[keys[1]] = hash[keys[1]] + [row[1]]                #product_id
        hash[keys[2]] = hash[keys[2]] + [row[2]]                #posted
        hash[keys[3]] = hash[keys[3]] + [row[3]]                #reviewer
        hash[keys[4]] = hash[keys[4]] + [row[4]]                #location
        hash[keys[5]] = hash[keys[5]] + [normalize(row[5])]     #description
        hash[keys[6]] = hash[keys[6]] + [row[6]]                #overall
        hash[keys[7]] = hash[keys[7]] + [row[7]]                #comfort
        hash[keys[8]] = hash[keys[8]] + [row[8]]                #style
        hash[keys[9]] = hash[keys[9]] + [row[9]]                #size
        hash[keys[10]] = hash[keys[10]] + [row[10]]             #arch
        hash[keys[11]] = hash[keys[11]] + [row[11]]             #width
        hash[keys[12]] = hash[keys[12]] + [row[12]]             #url

#dump dictionary into pickle file
print "dumping..."
cPickle.dump(hash, open("andrew_revs2.p", "wb"))