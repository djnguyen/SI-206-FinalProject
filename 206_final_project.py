# Put all import statements you need here.

import unittest
import requests
import json
import tweepy
import twitter_info
import sqlite3
import collections
import itertools
import re

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

CACHE_FNAME = "206_final_project_cached.json"


try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)

except:
    CACHE_DICTION = {}

# MOVIE SELECTION

### OMDB API WITH CACHING ###

#This function caches data from the OMDB Database

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

        twitter_handle = '@' + tweet_results[0]['screen_name'] ## can we check if it is verified?

        return twitter_handle

def searching_twitter(twitter_search_term):

    some_identifier = "twitter_search_{}".format(twitter_search_term)

    if some_identifier in CACHE_DICTION:
        tweet_results = CACHE_DICTION[some_identifier]

        return tweet_results

    else:
        try:
            tweet_results = api.search(q=twitter_search_term)

            CACHE_DICTION[some_identifier] = tweet_results

            dumping_results = open(CACHE_FNAME,'w')
            dumping_results.write(json.dumps(CACHE_DICTION, indent =2))
            dumping_results.close()
        except:
            print ("ERROR")
            exit()

        return tweet_results


def twitter_user_info(twitter_handle):

    some_identifier = 'twitter_user_{}'.format(twitter_handle)

    if some_identifier in CACHE_DICTION:
        user_info = CACHE_DICTION[some_identifier]

        return user_info

    else:
        try: 
            user_info = api.get_user(screen_name = twitter_handle)

            CACHE_DICTION[some_identifier] = user_info

            dumping_results = open(CACHE_FNAME, 'w')
            dumping_results.write(json.dumps(CACHE_DICTION, indent = 2))
            dumping_results.close()

        except:
            print ("ERROR")
            exit()

        return user_info

### DEFINING MOVIE CLASS ###


class Movie(object):

    def __init__(self, OMDB_Dictionary = {}):

        try:
            self.title = OMDB_Dictionary['Title']
            self.plot = OMDB_Dictionary['Plot']
            self.director = OMDB_Dictionary['Director'].split(',')[0]
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

    def get_rotten_tomato_rating(self):
        
        try:
            all_ratings = self.ratings

            rating_source = []
            rating_score = []

            for x in all_ratings:
                rating_source.append(x['Source'])
                rating_score.append(x['Value'])

            ratings_dict = dict(zip(rating_source,rating_score))

            rotten_tomato_unparsed = ratings_dict['Rotten Tomatoes']

            rotten_tomato_number = rotten_tomato_unparsed.split('%')

            return int(rotten_tomato_number[0])

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


# i also defined a class named tweet that will iterate throught the dictionary that is returned from the 
# Twitter Search API and put them into a list using list comprehension.


class Tweet(object):
    def __init__(self, TWITTER_DICT = {}):


        self.tweet_query = TWITTER_DICT['search_metadata']['query']
        self.tweet_id = [x['id_str'] for x in TWITTER_DICT['statuses']]
        self.screen_name = [x['user']['screen_name'] for x in TWITTER_DICT['statuses']]
        self.favorites = [x['favorite_count'] for x in TWITTER_DICT['statuses']]
        self.retweets = [x['retweet_count'] for x in TWITTER_DICT['statuses']]
        self.text = [x['text'] for x in TWITTER_DICT['statuses']]
        self.user_id = [x['user']['id'] for x in TWITTER_DICT['statuses']]


class TwitterUser(object):
    def __init__(self, TWITTER_DICT = {}):

        self.id = TWITTER_DICT['id']
        self.handle = "@" + TWITTER_DICT['screen_name']
        self.followers = TWITTER_DICT['followers_count']
        self.favorites = TWITTER_DICT['favourites_count']
        self.description = TWITTER_DICT['description']


list_of_movies = ["Mean Girls", "White Chicks", "The Secret Life of Pets", "The Fate of the Furious", "Logan", "Good Will Hunting", "Inception"]


movie_tuple = []
tweet_tuple = []
user_tuple = []
mentioned_tuple = []

actor_twitter = []
tweeter = []

def uploading_databases():

    for a_movie in list_of_movies:

        m = Movie(get_OMDB_data(a_movie))

        some_tuple = (m.get_movie_ID(),m.title, m.genre, m.plot, m.get_top_actor(), m.get_top_actor_twitter_handle(), m.director, m.get_director_twitter_handle(), m.get_rotten_tomato_rating())

        actor_twitter.append(m.get_top_actor_twitter_handle())

        movie_tuple.append(some_tuple)

        t = Tweet(searching_twitter(m.get_top_actor()))

        another_tuple = list(zip(t.tweet_id, t.screen_name, t.user_id, t.favorites, t.retweets, t.text))

        tweeter.append(t.screen_name)

        final_tweet_list = []

        for a_tuple in another_tuple:
            
            d = m.get_movie_ID()

            search_title = t.tweet_query

            new = a_tuple + (d,) + (search_title, )

            final_tweet_list.append(new)

        tweet_tuple.append(final_tweet_list)

        user = TwitterUser(twitter_user_info(m.get_top_actor_twitter_handle()))

        user_info_tuple = (user.id, user.handle, user.followers, user.favorites, user.description)

        user_tuple.append(user_info_tuple)

        mentioned_tuple.append(t.text)

uploading_databases()

ALL_TWEETERS = []

for tweet in tweeter:
    for x in tweet:
        final = "@" + x
        ALL_TWEETERS.append(final)


combined = actor_twitter + ALL_TWEETERS

individual_tweet = []
mentioned_users = []
final_user_database = []

for x in mentioned_tuple:
    for y in x:
        individual_tweet.append(y)

def unique_handle(some_list):
    for x in some_list:
        if x not in combined:
                mentioned_users.append(x)

for a_tweet in individual_tweet:

    if "@" in a_tweet:
        a_user = re.findall(r"(@[A-Za-z0-9_]+)", a_tweet)

        unique_handle(a_user)

final_user_list = combined + mentioned_users

ALMOST_FINAL_USERS_NO_DUPLICATES = set(final_user_list)
FINAL_USERS_NO_DUPLICATES = list(ALMOST_FINAL_USERS_NO_DUPLICATES) 

for x in FINAL_USERS_NO_DUPLICATES:
    user = TwitterUser(twitter_user_info(x))
    user_info_tuple_2 = (user.id, user.handle, user.followers, user.favorites, user.description)

    final_user_database.append(user_info_tuple_2)



#DATABASE CODE

db_conn = sqlite3.connect('206_final_project_database.db') #created a database
cur = db_conn.cursor()

drop_table_statement_1 = 'DROP TABLE IF EXISTS Tweets'
cur.execute(drop_table_statement_1)

drop_table_statement_2 = 'DROP TABLE IF EXISTS Users'
cur.execute(drop_table_statement_2)

drop_table_statement_3 = 'DROP TABLE IF EXISTS Movies'
cur.execute(drop_table_statement_3)

create_movies_table = 'CREATE TABLE IF NOT EXISTS '
create_movies_table += 'Movies (movie_id TEXT PRIMARY KEY, title TEXT, genre TEXT, plot TEXT, top_actor TEXT, top_actor_twitter TEXT, director TEXT, director_twitter TEXT, rotten_tomato_rating INTEGER)'
cur.execute(create_movies_table)

create_users_table = 'CREATE TABLE IF NOT EXISTS '
create_users_table += 'Users (user_id TEXT PRIMARY KEY, screen_name TEXT, followers INTEGER, num_favs INTEGER, description TEXT)'
cur.execute(create_users_table) 

create_tweets_table = 'CREATE TABLE IF NOT EXISTS '
create_tweets_table += 'Tweets (tweet_id TEXT PRIMARY KEY, screen_name TEXT, user_id TEXT, favorites INTEGER, retweets INTEGER, text TEXT, movie_id TEXT, search_query TEXT, '
create_tweets_table += 'FOREIGN KEY (user_id) REFERENCES Users(user_id) on UPDATE SET NULL, FOREIGN KEY (movie_id) REFERENCES Movies(movie_id) on UPDATE SET NULL)'
cur.execute(create_tweets_table) 

db_conn.commit()

# creating statements to upload to the movies table


add_movie_statement = 'INSERT OR IGNORE INTO Movies VALUES (?,?,?,?,?,?,?,?,?)'

for x in movie_tuple:
    cur.execute(add_movie_statement, x)

db_conn.commit()

# creating statements to upload to the tweets table

add_tweet_statement = 'INSERT OR IGNORE INTO Tweets VALUES (?,?,?,?,?,?,?,?)'

for x in tweet_tuple:
    for y in x:
        cur.execute(add_tweet_statement,y)

db_conn.commit()

# creating statements to upload to the users table

add_user_statement = 'INSERT OR IGNORE INTO Users VALUES (?,?,?,?,?)'

for x in final_user_database:
    cur.execute(add_user_statement,x)

db_conn.commit()



## Task 3: Database Queries + Data Manupulation

query_1 = 'SELECT Movies.top_actor, Users.screen_name FROM Tweets INNER JOIN Users ON Tweets.user_id = Users.user_id INNER JOIN Movies ON Tweets.movie_id = Movies.movie_id WHERE Users.followers > 1000'

cur.execute(query_1)
users_info = cur.fetchall()

user_dictionary = {user[0]: user[1] for user in users_info}

#print (user_dictionary)


query_2 = 'SELECT text FROM Tweets'
cur.execute(query_2)
tweet_text = [thing[0] for thing in cur.fetchall()]

#print(tweet_text)

tweet_words = {word for some_string in tweet_text for word in some_string.split()}


characters_list = [] # all of the characters 

for description in tweet_words:
    characters = re.findall(r"[a-zA-Z0-9]", description) #using regX to search for the words
    for character in characters:
        characters_list.append(character)

most_common_char = collections.Counter(characters_list).most_common(1)[0] #using Counter in the Collections Library


query_3 = 'SELECT title, plot, rotten_tomato_rating FROM Movies'
cur.execute(query_3)
movie_list = cur.fetchall()

sorted_ratings = sorted(movie_list, key=lambda x: x[2], reverse = True)

top_movie_w_rating = sorted_ratings[0]



all_plots = []
final_plots = []

for x in movie_list:
    all_plots.append(x[1])


for x in all_plots:
    for y in x.split():
        final_plots.append(y)

common_plot_word = collections.Counter(final_plots)



#Task 4: Text File Summary


# #CREATING A TXT FILE
outfile = open('206_final_project.txt', 'w')
outfile.write("David's Summary Statistics for Movies & Twitter as of April 25, 2017 \n \n \n \n")

outfile.write("The Movies that I obtained data on are: \n")

for x in list_of_movies:
    outfile.write("    - {} \n".format(x))

outfile.write("\n\n\n\nHere are some of the information of the movies that I gathered:\n")

for x in movie_tuple:

    outfile.write("---------------------------------------------------------\n")
    outfile.write("Title: {}\n\n".format(x[1]))
    outfile.write("Genre: {}\n\n".format(x[2]))
    outfile.write("Plot: {}\n\n".format(x[3]))
    outfile.write("Top Actor: {}\n\n".format(x[4]))
    outfile.write("Top Actor Twiter Handle: {}\n\n".format(x[5]))
    outfile.write("Director: {}\n\n".format(x[6]))
    outfile.write("Rotten Tomato Rating: {}/100\n\n".format(x[8]))

outfile.write("---------------------------------------------------------\n")

outfile.write("Looking at all of the tweets from all of these mentions of the actors, here is a list of words used in the tweet:\n\n")

outfile.write('{}\n'.format(tweet_words))

outfile.write("---------------------------------------------------------\n")

outfile.write("The Most Common Character in all of the Tweets is:\n\n")
outfile.write('The Character: \'{}\' with {} occurances\n\n'.format(most_common_char[0],most_common_char[1]))

outfile.write("---------------------------------------------------------\n")

outfile.write("It's also important to look for the most popular movie based on Rotten Tomatoes Ratings!\n\n")

outfile.write("The Top Rated Movie out of the list of movies above is: {} with a rating of {}/100! \n\n".format(top_movie_w_rating[0],top_movie_w_rating[2]))

outfile.write("---------------------------------------------------------\n")

outfile.write("Also looking at the plot of ALL the movies in the list above, we looked for the two most common words in the plot: \n\n")

outfile.write("Those two words are: \n")

outfile.write("\'{}\' with {} occurances\n\n".format(common_plot_word.most_common()[0][0], common_plot_word.most_common()[0][1]))
outfile.write("and\n\n")
outfile.write("\'{}\' with {} occurances\n\n".format(common_plot_word.most_common()[1][0], common_plot_word.most_common()[1][1]))


outfile.write("---------------------------------------------------------\n")

outfile.write("Thanks for running my program! Have an aMAIZEing day!")
outfile.close()

db_conn.close()



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

    def test_rotten_tomatoes_2(self):
        mean_girls_movies = get_OMDB_data("Mean Girls")
        m3 = Movie(mean_girls_movies)
        rating = m3.get_rotten_tomato_rating()
        self.assertEqual(rating, 84)

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


class Testing_TwitterUser_Class(unittest.TestCase):

    def test_handle(self):
        david = TwitterUser(twitter_user_info("@TheDavidNguyen"))
        self.assertEqual(david.description, "no matter where the world takes you, ho〽️e is never that far away | International Academy '15 University of Michigan School of Information '18 ΚΘΠ | ΑΦ wannabe")

class Testing_Tweet_Class(unittest.TestCase):

    def test_text(self):
        t = Tweet(searching_twitter("Jordan Peele"))
        self.assertEqual(type(t.screen_name), type([]))


class Misc_Tests(unittest.TestCase):

    def test_caching(self):
        file = open("206_final_project_cached.json", 'r')
        file_contents = file.read()
        file.close()

        self.assertTrue("Mean Girls" in file_contents)

class Database_Testing(unittest.TestCase):

    def test_db_1(self):
        conn = sqlite3.connect('206_final_project_database.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM Movies');
        result = cur.fetchall()
        self.assertTrue(len(result[1])==9,"Testing that there are 9 columns in the Movies table")
        conn.close()


## Remember to invoke all your tests...
# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)
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