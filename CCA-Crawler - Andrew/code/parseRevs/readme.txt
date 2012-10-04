NOTES: deb_fin.csv is the "correct" output files.

Some formatting errors still exist, such as some discreptancy in space characters in the description field.
However, when doing comparisons, this can be solved by simply removing all space characters in the description.

EDIT (10/1/2012): New validation method.

Relevant files to method:
	1. deb_fin.sorted.csv = deb_fin.csv sorted by product_id (done using MS Excel)
	2. reviews2True.sorted.csv = reviews2True.csv sorted by product_id (done using MS Excel)
		NOTE: reviews2True does not contain a location field.
	3. comparehash.py = the main comparison script that prints the number of matches.
	4. matches.csv = the rows in deb_fin.sorted.csv that have matches in reviews2True.sorted.csv
	
Methodology:
	1. Hash descriptions in file2 into a set a concatenation of product_id and description.
	2. Iterate through file1, hashing each product as done with file2, and checking for collisions with hash set from file2.
	3. O(2n) runtime
	
Reasons for not using Levenshtein's Edit Distance to check for matches:
	1. Levenshtein's algorithm grows proportionally to the sizes of the strings being compared. In our case, descriptions can be quite long.
	2. For our purpose, we can assume that if two reviews are the same, their descriptions must be identical after we remove non-alphabetical characters and all whitespaces.
	   Thus, considering a collision as a match suffices.
	   
Results:
	running the script as such:
	
			python comparehash.py deb_fin.sorted.csv reviews2True.sorted.csv
			
	returns that there are 105875 matches (or collisions).
	The total number of products in deb_fin.sorted.csv is 188162.
	105875/188162 = 0.5627
	So, approximately 56% of the products procured using Scrapy 
	
Possible cause of error:
	If there are any discrepancies in how the descriptions were scraped in the two methods (Zappos API and Scrapy), this method will miss some matches.
	A future objective could be to implement Levenshtein's as an alternative, so that if there is no collision, we resort to Levenshtein's.