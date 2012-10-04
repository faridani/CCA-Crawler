import csv
import sys
import libdistance
import cPickle
import itertools
import string
import time

#Run script on two CSV files of Zappos products sorted by id, compares them
#NOTE: This script uses itertools.islice(), which is a destructive function; the islice'd csv reader needs to be reinstantiated every time

file1 = sys.argv[1]
file2 = sys.argv[2]

#unpickle dict of key-value pairs {id : (start_index, end_index)}
#this dict must be the one associated with file2
indices_map = cPickle.load(open(sys.argv[3], 'rb'))

lev_threshold = 0.01	#CONSTANT: percent difference threshold for description comparison; modify until value is suitable
						#if percent difference is less than threshold, call it a match

#removes whitespaces and punctuations in a string ("punctuation" includes any non-alphabetical character besides integers), and then lowercases
def format_string (s):
	return s.replace(" ", "").translate(string.maketrans("", ""), string.punctuation).lower()

match_count = 0			#counter for number of matches
with open(file1, 'rb') as f1:
	reader1 = csv.reader(f1)
	reader1.next()				#skip first row containing field names
	start_time = time.time()

	row1_count = 0
	for row1 in reader1:
		##print row1_count, ":::", match_count
		##t2 = time.time()
		##print "row took:", t2 - t1
		##print "current match count:", match_count
		"""
		if t2 - t1 > 30:
			print "time elapsed:", t2 - start_time, "seconds"
			print match_count, "matches in", row1_count, "rows"
		t1 = t2
		"""
		row1_count += 1
		id = row1[1]
		if id in indices_map:	#if the id also present in the other file, go to correct index, and then loop through all products of same index
			reviewer1 = format_string(row1[3])
			#rev1len = len(reviewer1)		#calculated here to prevent redundant calculation in internal loop
			description1 = format_string(row1[5])
			des1len = len(description1)		#calculated here to prevent redundant calculation in internal loop
			#use islice to isolate chunk of same product id
			#loop through these products to check for match
			mapped_entry = indices_map[str(id)]		#tuple (start_index, end_index)
			start_index = mapped_entry[0]
			end_index = mapped_entry[1]
			#t1 = time.time()			#timer
			with open(file2, 'rb') as f2:
				#t2 = time.time()
				#print "islice took", t2 - t1, "seconds"
				#t1 = t2
				reader2 = csv.reader(f2)				#this insures that for every element in reader1 (outer loop), the reader to be compared to is reinstantiated and reinitialized
				reader2.next()
				for row2 in itertools.islice(reader2, start_index, end_index):
					reviewer2 = format_string(row2[3])
					description2 = format_string(row2[4])		#description not the same index as row1 in this case b/c second dataset does not contain "locations" field
					##rev_dist_perc = libdistance.levenshtein(reviewer1, reviewer2).ratio()				#percent difference
					##des_dist_perc = libdistance.levenshtein(description1, description2).ratio()			#percent difference
					##if rev_dist_perc == 0 and des_dist_perc < lev_threshold:
					if reviewer1 == reviewer2 and description1 == description2:
						print "-------------------------------------"
						print "d1:", description1
						print "d2:", description2
						match_count += 1
print match_count						