## Your name: David Nguyen (djnguyen)

## The option you've chosen: Option #2: Twitter/OMDB API Mashup

# Put import statements you expect to need here!

import unittest
import requests
import json
import tweepy
import twitter_info
import sqlite3
import collections
import itertools

##### TWEEPY SETUP CODE:
# Authentication information should be in a twitter_info file...
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and return it in a JSON format 
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

##### END TWEEPY SETUP CODE

CACHE_FNAME = "206_final_project_cache.json"


try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)

except:
    CACHE_DICTION = {}

def get_OMDB_WithCaching(baseURL, params={}):
  
  req = requests.Request(method = 'GET', url =baseURL, params = params )
  prepped = req.prepare()
  full_URL = prepped.url
  

  if full_URL not in CACHE_DICTION:
      
      response = requests.Session().send(prepped)
      CACHE_DICTION[full_URL] = response.text

      
      cache_file = open(CACHE_FNAME, 'w')
      cache_file.write(json.dumps(CACHE_DICTION, indent = 2))
      cache_file.close()


  return CACHE_DICTION[full_URL]

def get_OMDB_data(movie_title):

    base_url = "http://www.omdbapi.com/?"
    params_dict = {}
    params_dict['t'] = movie_title

    resp_text = get_OMDB_WithCaching(base_url, params_dict)

    processed_data = json.loads(resp_text)
    
    return processed_data

def get_twitter_director_handle(twitter_search_query):
    
    if twitter_search_query in CACHE_DICTION:
        tweet_results = CACHE_DICTION[twitter_search_query]

        twitter_handle = '@' + tweet_results[0]['screen_name']
        
        return twitter_handle

    else:
        params_dict = {}
        params_dict['per_page'] = 1
        params_dict['page'] = 1
        tweet_results = api.search_users(twitter_search_query, params = params_dict)
        CACHE_DICTION[twitter_search_query] = tweet_results

        dumping_results = open(CACHE_FNAME,'w')
        dumping_results.write(json.dumps(CACHE_DICTION, indent=2))
        dumping_results.close()

        twitter_handle = '@' + tweet_results[0]['screen_name']

        return twitter_handle




class Movie(object):

    def __init__(self, title):

        self.title = title

    def get_title(self):

        data = get_OMDB_data(self.title)

        self.title = data['Title']

        return self.title

    def get_director(self):

        data = get_OMDB_data(self.title)

        self.director = data['Director']

        return self.director

    def get_genre(self):

        data = get_OMDB_data(self.title)

        self.genre = data['Genre']

        return self.genre

    def get_ratings(self):

        data = get_OMDB_data(self.title)

        rating_source = []
        rating_score = []
        
        for x in data['Ratings']:
            rating_source.append(x['Source'])
            rating_score.append(x['Value'])

        ratings_dict = dict(zip(rating_source,rating_score))
            

        return ratings_dict

    def get_director_twitter_handle(self):

        data = get_OMDB_data(self.title)

        director = data['Director']

        twitter_handle = get_twitter_director_handle(director)

        self.director_handle = twitter_handle

        return self.director_handle


    def __str__(self):

        return "The movie {} is a {}, and was directed by {}. {} also has a Rotten Tomatoes Score of {}.".format(self.get_title(), self.get_genre(), self.get_director(), self.get_title(), self.get_ratings()["Rotten Tomatoes"])

# Write your test cases here.

d = Movie("Get Out")
print ("GET OUT")
print (d.get_director())
print (d.get_genre())
print (d.get_ratings()['Rotten Tomatoes'])
print (d.get_director_twitter_handle())


print ("---------------------")

e = Movie("Logan")
print ("LOGAN")
print (e.get_director())
print (e.get_genre())
print (e.get_ratings()['Rotten Tomatoes'])
print (e.get_director_twitter_handle())

print ("---------------------")


f = Movie("Mean Girls")
print ("MEAN GIRLS")
print (f.get_director())
print (f.get_genre())
print (f.get_ratings()['Rotten Tomatoes'])
print (f.get_director_twitter_handle())


class Testing_OMDB_API(unittest.TestCase):

    def test_title(self):
        mean_girls = get_OMDB_data("Mean Girls")
        self.assertEqual(mean_girls['Title'], "Mean Girls", "checking that title is the same")

    def test_director(self):
        mean_girls = get_OMDB_data("Mean Girls")
        self.assertEqual(mean_girls['Director'], "Mark Waters", 'checking for director')

    def test_genre(self):
        mean_girls = get_OMDB_data("Mean Girls")
        self.assertEqual(mean_girls['Genre'], "Comedy", 'checking for genre')

    def test_actors(self):
        mean_girls = get_OMDB_data("Mean Girls")
        self.assertEqual(type(mean_girls['Actors']), type(""))

class Testing_Movie_Class(unittest.TestCase):

    def test_title(self):
        m1 = Movie("Mean Girls")
        self.assertEqual(m1.title, "Mean Girls")

    def test_string(self):
        m2 = Movie("Mean Girls")
        self.assertEqual(m2.__str__(), "The movie Mean Girls is a Comedy, and was directed by Mark Waters. Mean Girls also has a Rotten Tomatoes Score of 84%.")

    def test_rotten_tomatos(self):
        m3 = Movie("Mean Girls")
        rating = m3.get_ratings()
        rotten_tomato = rating['Rotten Tomatoes']
        self.assertEqual(rotten_tomato, "84%")

    def test_Metacritic_score(self):
        m4 = Movie("Mean Girls")
        rating = m4.get_ratings()
        metacritic = rating['Metacritic']
        self.assertEqual(metacritic, "66/100")

    def test_director_twitter_handle(self):
        m5 = Movie("Get Out")
        self.assertEqual(m5.get_director_twitter_handle(), "@JordanPeele")

class Misc_Tests(unittest.TestCase):

    def test_caching(self):
        file = open("206_final_project_cache.json", 'r')
        file_contents = file.read()
        file.close()

        self.assertTrue("Mean Girls" in file_contents)


## Remember to invoke all your tests...
if __name__ == "__main__":
    unittest.main(verbosity=2)


#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
#MMMMMMM             MMMMMMMMMMMMMMMMM             MMMMMMMMM
#MMMMMMM              MMMMMMMMMMMMMMM              MMMMMMMMM
#MMMMMMM                MMMMMMMMMMM                MMMMMMMMM
#MMMMMMM                 MMMMMMMMM                 MMMMMMMMM
#MMMMMMM                  MMMMMMM                  MMMMMMMMM
#MMMMMMMMMMM               MMMMM                MMMMMMMMMMMM
#MMMMMMMMMMM                MMM                 MMMMMMMMMMMM
#MMMMMMMMMMM                 V                  MMMMMMMMMMMM
#MMMMMMMMMMM                                    MMMMMMMMMMMM
#MMMMMMMMMMM         ^               ^          MMMMMMMMMMMM
#MMMMMMMMMMM         MM             MM          MMMMMMMMMMMM
#MMMMMMMMMMM         MMMM         MMMM          MMMMMMMMMMMM
#MMMMMMMMMMM         MMMMM       MMMMM          MMMMMMMMMMMM
#MMMMMMMMMMM         MMMMMM     MMMMMM          MMMMMMMMMMMM
#MMMMMMM                MMMM   MMMM                MMMMMMMMM
#MMMMMMM                MMMMMVMMMMM                MMMMMMMMM
#MMMMMMM                MMMMMMMMMMM                MMMMMMMMM
#MMMMMMM                MMMMMMMMMMM                MMMMMMMMM
#MMMMMMM                MMMMMMMMMMM                MMMMMMMMM
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMMMM/-------------------------/MMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMMM/- SCHOOL OF INFORMATION -/MMMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMM/-------------------------/MMMMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM