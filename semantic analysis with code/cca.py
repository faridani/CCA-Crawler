import csv
from time import sleep
import re
#from nltk.stem.wordnet import WordNetLemmatizer
#from nltk.corpus import wordnet
from nltk.stem.lancaster import LancasterStemmer
def main():
    with open('final104.csv', 'rb') as f:
        with open('cca.csv','wb') as g:
            reader = csv.reader(f)
            writer = csv.writer(g)
            header = reader.next()
            #writer.writerow([(header[6]), "Overall Rating", "Description Word Count"])
            readrow = reader.next()
            count = 0
            numlines = 0
            stop = []
            pstem = LancasterStemmer()
            stopfile = open('english.stop', 'r+')
            for line in stopfile:
                stop.append(line.strip())
            while (readrow != ''):
                try:
                    wordlist = frequency(readrow[1],stop,pstem)
                    ratings = '[readrow[0],readrow[3],readrow[4]]'
                    writer.writerow([wordlist,eval(ratings)])
                    #wordcount = len(readrow[1].split(None))
                    #writer.writerow([(readrow[6]),(readrow[4]), wordcount])
                    readrow = reader.next()
                    #count += wordcount
                    numlines += 1
                    #wordcount = 0
                except StopIteration:
                    g.close()
                    break

def frequency(description,stop,pstem):
    freq_dict = {}
    for word in (description.split(None)):
        if (re.match('\w+',word)):
            if (word not in stop):
                word = pstem.stem(word)
                if (freq_dict.has_key(word)):
                    freq_dict[word] = int(freq_dict.get(word)) + 1
                else:
                    freq_dict[word] = 1
    return freq_dict.items()

main()
