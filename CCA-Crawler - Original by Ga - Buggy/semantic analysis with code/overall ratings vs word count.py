'''import xlrd
import os

curpath = os.path.abspath(os.curdir)
print ("Current path is %s : " % curpath)

wb = xlrd.open_workbook('final104.csv')
wb.sheet_names()

sh = wb.sheet_by_index(0)

for rownum in range (2):
    print sh.row_values(rownum)'''

import csv
with open('final104.csv', 'rb') as f:
    with open('analyze.csv','wb') as g:
        reader = csv.reader(f)
        writer = csv.writer(g)
        header = reader.next()
        writer.writerow([(header[6]), "Overall Rating", "Description Word Count"])
        readrow = reader.next()
        count = 0
        numlines = 0
        while (readrow != ''):
            try:
                wordcount = len(readrow[1].split(None))
                writer.writerow([(readrow[6]),(readrow[4]), wordcount])
                readrow = reader.next()
                count += wordcount
                numlines += 1
                wordcount = 0
            except StopIteration:
                g.close()
                break
        print(count/numlines)
