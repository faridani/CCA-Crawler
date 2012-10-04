import csv
import sys
import cPickle

#Run this on a sorted CSV file of Zappos products to index it

file = sys.argv[1]
out = sys.argv[2]
curr_index, prev_index, curr_id, prev_id = 0, 0, 0, 0
indices = {}	#dict containing {id# : tuple(start_id, end_id)}

#row numbers start from 1
with open(file, 'rb') as f:
	csv_reader = csv.reader(f)
	csv_reader.next()	#skip first line of fields
	prev_index += 1		#prev_index = 1
	curr_index += 1		#curr_index = 1
	#begin indexing loop
	first_item = csv_reader.next()	#initialize
	prev_index += 1					#prev_index = 2
	curr_index += 1					#curr_index = 2
	prev_id = first_item[1]
	for row in csv_reader:
		curr_index += 1
		curr_id = row[1]
		if curr_id != prev_id:		#hit the end of product id's b/c we see a new one
			indices[prev_id] = (prev_index, curr_index - 1)
			prev_index = curr_index
			prev_id = curr_id

#pickle indices dict
cPickle.dump(indices, open(out, 'wb'), cPickle.HIGHEST_PROTOCOL)