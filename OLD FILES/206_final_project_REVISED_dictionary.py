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

CACHE_FNAME = "206_final_project_cache_TEST.json"


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

    if 'Error' in processed_data.keys():
        return "{} is not a movie found on OMDB's API!".format(movie_title)

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

    def __init__(self, OMDB_Dictionary = {}):

        try:


            self.title = OMDB_Dictionary['Title']
            self.director = OMDB_Dictionary['Director']
            self.genre = OMDB_Dictionary['Genre']
            self.ratings = OMDB_Dictionary['Ratings']
            self.actors = OMDB_Dictionary["Actors"]

        except:
            return None

    def get_specific_rating(self):

        try:
            all_ratings = self.ratings

            rating_source = []
            rating_score = []

            for x in all_ratings:
                rating_source.append(x['Source'])
                rating_score.append(x['Value'])

            ratings_dict = dict(zip(rating_source,rating_score))

            return ratings_dict

        except:
            return "ERROR"

    def get_top_actor(self):

        try:

            string_of_actors = self.actors

            list_of_actors = string_of_actors.split(',')

            return list_of_actors[0]
 
        except:
            return "ERROR"

    def get_top_actor_twitter_handle(self):

        try:

            actor = self.get_top_actor()

            actor_twitter_handle = get_twitter_director_handle(actor)

            self.actor_handle = actor_twitter_handle

            return self.actor_handle

        except:
            return "ERROR"


    def get_director_twitter_handle(self):

        try:

            director = self.director

            twitter_handle = get_twitter_director_handle(director)

            self.director_handle = twitter_handle

            return self.director_handle

        except:
            return "ERROR"

    def __str__(self):
        try:
            return "The movie {} is a {}, and was directed by {}. {} also has a Rotten Tomatoes Score of {}.".format(self.title, self.genre, self.director, self.title, self.get_specific_rating()['Rotten Tomatoes'])

        except:
            return "The Movie is Invalid"

get_out_movie = get_OMDB_data("Get Out")

d = Movie(get_out_movie)

print (d)

mean_girls_movie = get_OMDB_data("Mean Girls")

e = Movie(mean_girls_movie)

print (e)
print ("TOP ACTOR OF MEAN GIRLS IS: ")
print (e.get_top_actor())
print (e.get_top_actor_twitter_handle())

wrong_movie = get_OMDB_data('fdsfadsfsafdas')

print (wrong_movie) #{'Error': 'Movie not found!', 'Response': 'False'}

f = Movie(wrong_movie)
print (f)


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
        mean_girls_movies = get_OMDB_data("Mean Girls")
        m1 = Movie(mean_girls_movies)
        self.assertEqual(m1.title, "Mean Girls")

    def test_string(self):
        mean_girls_movies = get_OMDB_data("Mean Girls")
        m2 = Movie(mean_girls_movies)
        self.assertEqual(m2.__str__(), "The movie Mean Girls is a Comedy, and was directed by Mark Waters. Mean Girls also has a Rotten Tomatoes Score of 84%.")

    def test_rotten_tomatos(self):
        mean_girls_movies = get_OMDB_data("Mean Girls")
        m3 = Movie(mean_girls_movies)
        rating = m3.get_specific_rating()
        rotten_tomato = rating['Rotten Tomatoes']
        self.assertEqual(rotten_tomato, "84%")

    def test_Metacritic_score(self):
        mean_girls_movies = get_OMDB_data("Mean Girls")
        m4 = Movie(mean_girls_movies)
        rating = m4.get_specific_rating()
        metacritic = rating['Metacritic']
        self.assertEqual(metacritic, "66/100")

    def test_director_twitter_handle(self):
        get_out = get_OMDB_data("Get Out")
        m5 = Movie(get_out)
        self.assertEqual(m5.get_director_twitter_handle(), "@JordanPeele")

class Misc_Tests(unittest.TestCase):

    def test_caching(self):
        file = open("206_final_project_cache_TEST.json", 'r')
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