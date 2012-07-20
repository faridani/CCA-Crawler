import urllib
import json
import csv
from sys import argv
from time import sleep


# Write column headers for CSV file
c = csv.writer(open("reviews2.csv", "wb"))
c.writerow(["style" , "Description" , "url" , "comfort" , "overall" , "width" , "product_id" , "reviewer" , 
            "size" , "arch" , "product_name" , "posted"])

# counting=True will tell getKey() to count and display how many requests to the API are made
counting = True
count = 1

verbose = False
keyCount = -1

# Fall-back key to use if reading 'keys.txt' doesn't work
defaultKey = '8b470026e6ac14dada4da31cf026dcb1e279aa7d'

# Import a list of keys 
# Try to read the keys in 'keys.txt' into the keys list
# If reading the file fails, revert to defaultKey
try: 
    keys = open('keys.txt').readlines()
    numKeys = len(keys)
    keysReadIn = True
except IOError: 
    keysReadIn = False 
    numKeys = 1
    

# Cycles through list of keys to avoid rate-limiting. 
# If keys.txt was not read, return the default key
def getKey():
    global counting
    if counting:
        global count
        print count
        count +=1 
    global numKeys
    sleep(.5/numKeys) # API is rate-limited to 2 requests per second per key. 
    if keysReadIn:
        global keyCount
        keyCount = (keyCount+1)%numKeys
        return keys[keyCount]
    else:
        return defaultKey
    
# Makes a request to the Zappos product API. 
# Input is a product ID. 
# Output is info about that product in a dict
def requestProductDict(product):
    try: 
        request = "http://api.zappos.com/Product/" + str(product) + "?includes=[\"styles\",%20\"defaultProductType\"]&key=" + getKey()
        q = json.loads(urllib.urlopen(request).read())
        return q['product']
    except KeyError:
        print "That product does not exist"

# Makes a request to the Zappos reviews API. 
# Input is a product ID. 
# Output is a list of all reviews, each of which is represented by a dict.
def requestReviewsDict(product):
    try:
        page = 1
        Reviews = []
        request = "http://api.zappos.com/Review?productId=" + str(product) + "&page=" + str(page) + "&key=" + getKey()
        q = json.loads(urllib.urlopen(request).read())
        Reviews.extend(q['reviews'])
        while len(q['reviews']) == 30: # Review requests can only return 30 reviews. While loop continues to make requests until all reviews are retrieved. 
            page += 1
            request = "http://api.zappos.com/Review?productId=" + str(product) + "&page=" + str(page) + "&key=" + getKey()
            q = json.loads(urllib.urlopen(request).read())
            Reviews.extend(q['reviews'])
        return Reviews
    except ValueError: # If an error occurs, return the reviews gathered so far for the given product. 
        print "Reached an error."
        return Reviews

# Makes a request to the Zappos search API. 
# Required input is a search term.
# Can also specify number of results, or choose to see all results
# Can specify sorting, and filter by category or gender. By default, no filters are imposed. 
# Output is a list of the search results as dicts.
def requestSearchDict(term, All=True, categoryFilter='', genderFilter='', num=100, sort='productRating'):
    try:
        if All:
            page = 1
            Results = []
            request = "http://api.zappos.com/Search?term=" + term + "&filters={%22productTypeFacet%22:[%22" + categoryFilter + "%22],%22txAttrFacet_Gender%22:[%22" + genderFilter + "%22]}&limit=100&page=" + str(page) + "&sort={%22" + sort + "%22:%22desc%22}&key=" + getKey()          
            q = json.loads(urllib.urlopen(request).read())
            Results.extend(q['results'])
            while len(q['results']) == 100: # Like the Reviews request, a Search request is limited to 100 results per request. Similar technique used to retrive all results.
                page += 1
                request = "http://api.zappos.com/Search?term=" + term + "&filters={%22productTypeFacet%22:[%22" + categoryFilter + "%22],%22txAttrFacet_Gender%22:[%22" + genderFilter + "%22]}&limit=100&page=" + str(page) + "&sort={%22" + sort + "%22:%22desc%22}&key=" + getKey()
                q = json.loads(urllib.urlopen(request).read())
                Results.extend(q['results'])
            Results = dict((x['productId'], x) for x in Results).values() # Remove dicts from Results whose product IDs are duplicates. 
            return Results
        else: # If All is False, then return num results. Loop through pages with 100 results, and then add results from the final page.
            lastPage = num % 100
            pages = (num / 100) +  1
            Results = []
            for i in range(1,pages):
                request = "http://api.zappos.com/Search?term=" + term + "&filters={%22productTypeFacet%22:[%22" + categoryFilter + "%22],%22txAttrFacet_Gender%22:[%22" + genderFilter + "%22]}&limit=100&page=" + str(page) + "&sort={%22" + sort + "%22:%22desc%22}&key=" + getKey()
                q = json.loads(urllib.urlopen(request).read())
                Results.extend(q['results'])
            if lastPage == 0: 
                Results = dict((x['productId'], x) for x in Results).values() # Remove duplicates.
                return Results
            else: 
                request = "http://api.zappos.com/Search?term=" + term + "&filters={%22productTypeFacet%22:[%22" + categoryFilter + "%22],%22txAttrFacet_Gender%22:[%22" + genderFilter + "%22]}&limit=100&page=" + str(page) + "&sort={%22" + sort + "%22:%22desc%22}&key=" + getKey()
                q = json.loads(urllib.urlopen(request).read())
                Results.extend(q['results'])
                Results = dict((x['productId'], x) for x in Results).values()
                return Results
    except IOError: # If an error occurs, return the results gathered so far for the search term.
            print "You have hit the rate limit. Either use a new key, or make API requests more slowly"
            return Results
        

# Review class
class Review:
    
    id = 0
    date = ''
    name = ''
    location = ''
    summary = ''
    overallRating = 0 
    comfortRating = 0
    lookRating = 0
    url = ''
    productName = ''
    shoeSize = ''
    shoeWidth = ''
    shoeArch = ''
    otherShoes = ''
    
    
    def __init__(self, id, date, author, location, summary, overallRating, comfortRating, 
                lookRating, url, productName, shoeSize = None, shoeWidth = None, shoeArch = None, otherShoes = None):
        self.id = id.encode('ascii', 'ignore')
        self.date = date.encode('ascii', 'ignore')
        self.author = author.encode('ascii', 'ignore')
        self.location = location.encode('ascii', 'ignore')
        self.summary = summary.encode('ascii', 'ignore')
        self.overallRating = overallRating.encode('ascii', 'ignore')
        self.comfortRating = comfortRating.encode('ascii', 'ignore')
        self.lookRating = lookRating.encode('ascii', 'ignore')
        self.url = url.encode('ascii', 'ignore')
        self.productName = productName.encode('ascii', 'ignore')
        self.shoeSize = shoeSize.encode('ascii', 'ignore')
        self.shoeWidth = shoeWidth.encode('ascii', 'ignore')
        self.shoeArch = shoeArch.encode('ascii', 'ignore')
        self.otherShoes = otherShoes.encode('ascii', 'ignore')
        
    def __str__(self):
        return "Author: " + self.author + ", Overall: " + str(self.overallRating) + ", Summary: " + self.summary 
    
    # Returns the product ID.
    def getReviewId(self):
        return self.id
        
    # Returns the date the review was posted.
    def getReviewDate(self):
        return self.date
    
    # Returns the name of the author of the review.
    def getReviewAuthor(self):
        return self.author
        
    # Returns the location of the author of the review.
    def getReviewLocation(self):
        return self.location
    
    # Returns the summary/description of review.
    def getReviewSummary(self):
        return self.summary
        
    # Returns the Overall rating for the review.
    def getOverallRating(self):
        return self.overallRating   

    # Returns the Comfort rating for the review.
    def getComfortRating(self):
        return self.comfortRating   
        
    # Returns the Look rating for the review.
    def getLookRating(self):
        return self.lookRating
    
    # Returns the URL of the product of the review.
    def getProductUrl(self):
        return self.url
    
    # Returns the name of the product of the review.        
    def getReviewProductName(self):
        return self.productName
        
    # Returns the fit rating on shoe size.
    def getReviewSize(self):
        return self.shoeSize
        
    # Returns the fit rating on shoe width.
    def getReviewWidth(self):
        return self.shoeWidth   
    
    # Returns the fit rating on shoe arch.
    def getReviewArch(self):
        return self.shoeArch        
    
    
# Product class 
class Product:
    
    productID = 0
    productName = ''
    brandName = ''
    originalPrice = ''
    price = ''
    productUrl = ''
    reviews = []
    
    
    # Get a list of reviews as dicts from the API with a product ID.
    # Use entries of dicts to create Review objects.
    # Return a list of Review objects.
    def getReviews(self):
        if verbose:
            print "Calling getReviews()"
        #if self.reviews == []:
        reviewDicts = requestReviewsDict(self.productID)
        reviewObjs = []
        for i in range(len(reviewDicts)):
            CurrentReview = Review(reviewDicts[i]['id'],reviewDicts[i]['date'], reviewDicts[i]['name'], reviewDicts[i]['location'], 
                                    reviewDicts[i]['summary'], reviewDicts[i]['overallRating'], reviewDicts[i]['comfortRating'], 
                                    reviewDicts[i]['lookRating'], self.productUrl, self.productName, reviewDicts[i]['shoeSize'], reviewDicts[i]['shoeWidth'], 
                                    reviewDicts[i]['shoeArch'], reviewDicts[i]['otherShoes'])
            reviewObjs.append(CurrentReview)
        return reviewObjs

    # By default, this will also request the reviews for the product, but if shouldGetReviews=False, it won't (since this requires an extra API call).
    def __init__(self, ID, productName, brandName, productUrl, shouldGetReviews=True):
        if verbose:
            print "Calling Product Constructor"
        self.productID = ID
        self.productName = productName
        self.brandName = brandName
        self.productUrl = productUrl
        self.reviews = []
        if shouldGetReviews:
            self.reviews = self.getReviews()
    
    
    def __str__(self):
        return "Product: " + self.brandName + " " + self.productName + ", ID: " + str(self.productID)
        
    # Returns the name of the product.
    def getProductName(self):
        if verbose:
            print "Calling getProductName()"
        return self.productName
    
    # Returns the brand of the product. 
    def getBrandName(self):
        if verbose:
            print "Calling getBrandName()"
        return self.brandName
        
    # Returns the product URL of the product.
    def getProductUrl(self):
        if verbose:
            print "Calling getProductUrl()"
        return self.productUrl
    
    # Returns the number of reviews.    
    def getNumReviews(self):
        return len(self.reviews)
    
    # Returns the review object with the highest Overall rating.    
    def getMaxRating(self):
        if verbose: 
            print "Calling getMaxRating()"
        max = self.reviews[0].getOverallRating()
        max_index = 0
        NumReviews = self.getNumReviews()
        for i in range(1, NumReviews):
            if self.reviews[i].getOverallRating() > max:
                max = self.reviews[i].getOverallRating()
                max_index = i
        return self.reviews[max_index]
        
    # Returns the review object with the lowest Overall rating. 
    def getMinRating(self):
        if verbose: 
            print "Calling getMinRating()"
        min = self.reviews[0].getOverallRating()
        min_index = 0
        NumReviews = self.getNumReviews()
        for i in range(1, NumReviews):
            if self.reviews[i].getOverallRating() < min:
                min = self.reviews[i].getOverallRating()
                min_index = i
        return self.reviews[min_index]
    
    # Returns the average Overall rating. Returns 0 if there are no reviews.
    def getAvgRating(self):
        if verbose:
            print "Calling getAvgRating()"
        overallRatings = []
        NumReviews = self.getNumReviews()
        if NumReviews == 0: 
            return 0
        else:
            for i in range(NumReviews):
                overallRatings.append(int(self.reviews[i].getOverallRating()))
            return float(sum(overallRatings))/float(len(overallRatings))
    
    # Returns a dict whose keys are Overall ratings (1 through 5) and whose values are the number of times they appear. 
    def getRatingFreqs(self):
        if verbose:
            print "Calling getRatingFreqs()"
        RatingFreqs = {1:0 ,2:0 ,3:0 ,4:0, 5:0}
        NumReviews = self.getNumReviews()
        for i in range(NumReviews):
            RatingFreqs[int(self.reviews[i].getOverallRating())] += 1
        return RatingFreqs

        
# Returns a product object from a product ID.
def createProduct(ID):
    prodDict = requestProductDict(ID)
    return Product(ID, prodDict[0]['productName'], prodDict[0]['brandName'], prodDict[0]['brandId'],
                       prodDict[0]['defaultProductUrl'], prodDict[0]['defaultProductType'])


# Note: For all search-related methods below, you can use an empty string for the term argument to retrieve all results, given the filter arguments.
# For example, to receive all women's shoes, use term='', categoryFilter='Shoes', and genderFilter='Women'.


# Returns total number of unique results in a search.       
def getNumResults(term, All=True, categoryFilter='', genderFilter=''):
    if verbose:
        print "Calling getNumResults()"
    d = requestSearchDict(term, All, categoryFilter, genderFilter)
    return len(d)

# Returns search results as a list of product objects.
# Creates product object directly from search results, rather than making another API request.  
def getProductObjs(term, All=True, categoryFilter='', genderFilter='', num=100, sort='productRating'):
    if verbose:
        print "Calling getProductObjs()" 
    d = requestSearchDict(term, All, categoryFilter, genderFilter, num, sort)   
    ProductList = []
    for i in d:
        CurrentProduct = Product(i['productId'], i['productName'], i['brandName'], i['productUrl'])
        ProductList.append(CurrentProduct)
    return ProductList

# Returns search result with the highest average Overall rating. 
def getHighestRated(term, All=True, categoryFilter='', genderFilter='', num=100, sort='productRating'):
    if verbose:
        print "Calling getHighestRated()" 
    L = requestSearchDict(term, All, categoryFilter, genderFilter, num, sort)
    return L[0]

# Returns a list of all reviews across all unique products from a search.   
def searchAllReviews(term, All=True, categoryFilter='', genderFilter='', num=100):
    Reviews = []
    Products = getProductObjs(term, All, categoryFilter, genderFilter, num)
    print "The number of products is " + str(len(Products))
    for p in Products:
        newReviews = p.reviews
        Reviews.extend(newReviews)
    return Reviews
    
# Writes all reviews of a search into a CSV.
def WriteCSV(term, All=True, categoryFilter='', genderFilter='', num=100):
    try:
        allReviews = searchAllReviews(term, All, categoryFilter, genderFilter, num)
        print "Done compiling the reviews. There are " + str(len(allReviews)) + " reviews. Now adding them to the csv."
        global c
        for i in allReviews:
            c.writerow([i.getLookRating(), i.getReviewSummary(), i.getProductUrl(), i.getComfortRating(), i.getOverallRating(), i.getReviewWidth(), 
                        i.getReviewId(), i.getReviewAuthor(), i.getReviewSize(), i.getReviewArch(), i.getReviewProductName(), i.getReviewDate()])
    except IOError:
        print "Connection issue"


#WriteCSV('', True, 'Shoes', 'Women') # Write all reviews across all women's shoes into a CSV.
