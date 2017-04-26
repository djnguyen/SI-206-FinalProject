# David Nguyen SI 206 Winter 2017 Final Project

This is my final project for SI 206 at the University of Michigan School of Information

## Option #2: API Mashup: Twitter & OMDB

This program searches through a list of movies and pulls data from the OMDB API. Also, the top actor is searched on Twitter through the Tweepy API and all of the data is stored into a database. There is some data manipulation also involved with this program and all of the results are outputted into a .txt file.

## Getting Started

Ensure that a twitter_info.py file is contained within the same directory and run the file 206_final_project.py

### Prerequisites

What things you need to run the program and how to install them

```
Modules to install include: requests, tweepy, sqlite3

Also, it is important to have a twitter_info.py file contining confidential information for a Twitter account
```


### Files Included
```
- 206_final_project.py (Contains the Python Program)
- 206_final_project_cached.json (Contains cached data to run program offline)
- 206_final_project_database.db (Contains the Databases)
```


### Functions

These are the following functions that are contained in 206_final_project.py

```
def get_OMDB_WithCaching():

Input: baseURL and Parameters
Behavior: Checks if the search query is in the cached file or makes a request to the OMDB API and then stores it within the cached file
Returns: JSON Object from OMDB API
```

```
def get_OMDB_data()
Input: movie_title (represents a movie as a string)
Behavior: Creates the URL for the API calling and calls get_OMDB_WithCaching function
Returns: JSON Object from OMDB API
```
```
def get_twitter_handle
Input: search query
Behavior: Makes a call to the Tweepy API and caches it. Obtains the twitter handle from the search query
Returns: Twitter Handle
```
```
def searching_twitter()
Input: search query
Behavior: Makes a call to the Tweepy API and caches it. Obtains the Twitter Search results in a JSON Format
Returns: JSON Object from Tweepy API
```
```
def searching_twitter()
Input: twitter_handle
Behavior: Makes a call to the Tweepy API and caches it. Obtains the Twitter User Information results in a JSON Format
Returns: JSON Object from Tweepy API
```


End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
