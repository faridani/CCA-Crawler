import csv
import sys
import string
import time
import md5

#Run this script on two CSV files of Zappos products sorted by product_id
#NOTE: This script uses md5 hashing to check whether one product is in the other csv file.
#Methodology:
#	1. Hash descriptions in file2 into a set a concatenation of product_id and description.
#	2. Iterate through file1, hashing each product as done with file2, and checking for collisions with hash set from file2.
#	O(2n) runtime

file1 = sys.argv[1]
file2 = sys.argv[2]

#removes whitespaces and punctuations in a string ("punctuation" includes any non-alphabetical character besides integers),
#and then lowercases
def format_string (s):
	return s.replace(" ", "").translate(string.maketrans("", ""), string.punctuation).lower()

match_count = 0						#counter for number of matches
file2_description_hash = set()		#a set of hashes of reviews

#FIRST we hash all the descriptions and reviewers of file1
with open(file2, 'rb') as f2:
	reader2 = csv.reader(f2)
	reader2.next()				#skip first row containing field names
	print "hashing..."
	for row2 in reader2:
		id2 = row2[1]
		description2 = format_string(row2[4])
		to_be_hashed = str(description2)
		hash = md5.new()
		hash.update(to_be_hashed)
		file2_description_hash.add(hash.hexdigest())

with open(file1, 'rb') as f1:
	with open("matches.csv", 'wb') as matchesFile:
		writer1 = csv.writer(matchesFile)
		reader1 = csv.reader(f1)
		fields = reader1.next()
		writer1.writerow(fields)
		print "matching..."
		for row1 in reader1:
			id1 = row1[1]
			description1 = format_string(row1[5])
			to_be_hashed = str(description1)
			hash = md5.new()
			hash.update(to_be_hashed)
			if hash.hexdigest() in file2_description_hash:
				writer1.writerow(row1)
				match_count += 1

print match_count