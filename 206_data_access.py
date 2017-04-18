###### INSTRUCTIONS ###### 

# An outline for preparing your final project assignment is in this file.

# Below, throughout this file, you should put comments that explain exactly what you should do for each step of your project. You should specify variable names and processes to use. For example, "Use dictionary accumulation with the list you just created to create a dictionary called tag_counts, where the keys represent tags on flickr photos and the values represent frequency of times those tags occur in the list."

# You can use second person ("You should...") or first person ("I will...") or whatever is comfortable for you, as long as you are clear about what should be done.

# Some parts of the code should already be filled in when you turn this in:
# - At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 
# - Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
# - Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.
# - At least enough code to load data into 1 of your dtabase tables (this should accord with your instructions/tests)

######### END INSTRUCTIONS #########

# Put all import statements you need here.
import unittest
import requests
import json
import tweepy
import twitter_info
import sqlite3
import collections
import itertools

# Begin filling in instructions....


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

### DEALING WITH CACHED FILES #################
CACHE_FNAME = "206_final_project_cache_data_access.json"


try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)

except:
    CACHE_DICTION = {}

### OMDB API WITH CACHING ###

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


### GET OMDB DATA ###

def get_OMDB_data(movie_title):


    base_url = "http://www.omdbapi.com/?"
    params_dict = {'t': movie_title,
    'plot': 'full'}
    # params_dict['t'] = movie_title
    # params_dict['plot'] = 'full'

    resp_text = get_OMDB_WithCaching(base_url, params_dict)

    processed_data = json.loads(resp_text)

    if 'Error' in processed_data.keys():
        return "{} is not a movie found on OMDB's API!".format(movie_title)

    return processed_data


### TWITTER API SEARCHING ###

def get_twitter_handle(twitter_search_query):
    
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

def searching_twitter(twitter_search_term):

    if twitter_search_term in CACHE_DICTION:
        tweet_results = CACHE_DICTION[twitter_search_term]

        return tweet_results

    else:
        try:
            tweet_results = api.search(q=twitter_search_term)

            CACHE_DICTION[twitter_search_term] = tweet_results

            dumping_results = open(CACHE_FNAME,'w')
            dumping_results.write(json.dumps(CACHE_DICTION, indent =2))
            dumping_results.close()
        except:
            print ("ERROR")
            exit()

        return tweet_results


### DEFINING MOVIE CLASS ###

class Movie(object):

    def __init__(self, OMDB_Dictionary = {}):

        try:


            self.title = OMDB_Dictionary['Title']
            self.plot = OMDB_Dictionary['Plot']
            self.director = OMDB_Dictionary['Director']
            self.genre = OMDB_Dictionary['Genre']
            self.ratings = OMDB_Dictionary['Ratings']
            self.actors = OMDB_Dictionary["Actors"]
            self.movie_id = OMDB_Dictionary['imdbID']

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

            actor_twitter_handle = get_twitter_handle(actor)

            self.actor_handle = actor_twitter_handle

            return self.actor_handle

        except:
            return "ERROR"


    def get_director_twitter_handle(self):

        try:

            director = self.director

            twitter_handle = get_twitter_handle(director)

            self.director_handle = twitter_handle

            return self.director_handle

        except:
            return "ERROR"

    def get_movie_ID(self):
        return self.movie_id

    def __str__(self):
        try:
            return "The movie {} is a {}, and was directed by {}. {} also has a Rotten Tomatoes Score of {}.".format(self.title, self.genre, self.director, self.title, self.get_specific_rating()['Rotten Tomatoes'])

        except:
            return "The Movie is Invalid"

### DEBUGGING PLACE ###

# get_out_movie = get_OMDB_data("Get Out")

# d = Movie(get_out_movie)

# print (d)


# mean_girls_movie = get_OMDB_data("Mean Girls")

# e = Movie(mean_girls_movie)

# print (e)
# print ("TOP ACTOR OF MEAN GIRLS IS: ")
# print (e.get_top_actor())
# print (e.get_top_actor_twitter_handle())
# print (e.get_movie_ID())

# wrong_movie = get_OMDB_data('fdsfadsfsafdas')

# print (wrong_movie) #{'Error': 'Movie not found!', 'Response': 'False'}

# f = Movie(wrong_movie)
# print (f)



### PUTTING IT ALL TOGETHER (ISH)

mean_girls_OMDB = get_OMDB_data("Mean Girls")
MG = Movie(mean_girls_OMDB)


mean_girls_twitter_search = searching_twitter(MG.get_top_actor())


#DATABSE TESTING

db_conn = sqlite3.connect('206_final_project.db')
cur = db_conn.cursor()

drop_table_statement_1 = 'DROP TABLE IF EXISTS Tweets'
cur.execute(drop_table_statement_1)

drop_table_statement_2 = 'DROP TABLE IF EXISTS Users'
cur.execute(drop_table_statement_2)

drop_table_statement_3 = 'DROP TABLE IF EXISTS Movies'
cur.execute(drop_table_statement_3)

create_movies_table = 'CREATE TABLE IF NOT EXISTS '
create_movies_table += 'Movies (movie_id TEXT PRIMARY KEY, title TEXT, genre TEXT, plot TEXT, top_actor TEXT, top_actor_twitter TEXT, director TEXT, director_twitter TEXT, rotten_tomato_rating TEXT)'
cur.execute(create_movies_table)

# create_users_table = 'CREATE TABLE IF NOT EXISTS '
# create_users_table += 'Users (user_id TEXT PRIMARY KEY, screen_name TEXT, num_favs INTEGER, description TEXT)'
# cur.execute(create_users_table)

# create_tweets_table = 'CREATE TABLE IF NOT EXISTS '
# create_tweets_table += 'Tweets (tweet_id TEXT PRIMARY KEY, text TEXT, user_id TEXT NOT NULL, time_posted TIMESTAMP, retweets INTEGER, '
# create_tweets_table += 'FOREIGN KEY (user_id) REFERENCES Users(user_id) on UPDATE SET NULL)'
# cur.execute(create_tweets_table)

db_conn.commit()


mean_girls_database_uploading = (MG.get_movie_ID(), MG.title, MG.genre, MG.plot, MG.get_top_actor(), MG.get_top_actor_twitter_handle(), MG.director, MG.get_director_twitter_handle(), MG.get_specific_rating()['Rotten Tomatoes'])

add_movie_statement = 'INSERT INTO Movies VALUES (?,?,?,?,?,?,?,?,?)'
cur.execute(add_movie_statement,mean_girls_database_uploading)

db_conn.commit()

# Put your tests here, with any edits you now need from when you turned them in with your project plan.

### TEST SUITE ###
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
        file = open("206_final_project_cache_data_access.json", 'r')
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





# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)