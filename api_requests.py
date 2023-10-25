import os, requests, datetime, random
from dotenv import load_dotenv
from mysecrets import API_SECRET_KEY
# from mysecrets import get_secret

API_BASE_URL = 'https://api.themoviedb.org/3/'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500/'
YOUTUBE_BASE_URL = 'https://www.youtube.com/embed/'
load_dotenv()

API_KEY = os.environ.get('API_KEY', API_SECRET_KEY)

# Get suggested movies data from the API
def get_movie(id):
    url = (API_BASE_URL+'movie/{movie_id}%?api_key={api_key}&append_to_response=videos,images,credits,watch/providers,reviews').format(api_key=API_KEY, movie_id=id)

    try:     
        res = requests.get(url)
    except:
        raise ('not connected to internet or movidb issue')
    
    response = res.json()

    return response



# Get casts data from the API
def get_cast(id):
    url = (API_BASE_URL+'person/{person_id}%?api_key={api_key}&append_to_response=images,movie_credits').format(api_key=API_KEY, person_id=id)

    try:     
        res = requests.get(url)
    except:
        raise ('not connected to internet or movidb issue')
    
    response = res.json()

    return response



# Get movies data based on genre from the API
def get_movie_by_genre(id):
    url1 = (API_BASE_URL+'discover/movie?api_key={api_key}&language=en-US&page=1&sort_by=popularity.desc&with_genres={genre_id}').format(api_key=API_KEY, genre_id=id)
    url2 = (API_BASE_URL+"genre/movie/list?api_key={api_key}&language=en").format(api_key=API_KEY)
    
    try:     
        res1 = requests.get(url1)
        res2 = requests.get(url2)
    except:
        raise ('not connected to internet or movidb issue')
    
    response = res1.json()
    genres = res2.json()


    return [response, genres]


# Get trending movies list from the API
def get_trending_movies():
    url = (API_BASE_URL+"trending/movie/week?api_key={api_key}&language=en-US&page1").format(api_key=API_KEY)
   
    try:     
        res = requests.get(url)
    except:
        raise ('not connected to internet or movidb issue')
    
    response = res.json()

    return response




# Retrieve movie's detail
def get_movie_detail(id):
        
        resp = get_movie(id)

        id = id
        title = resp['title']
        if resp['images']['posters']:
            poster_path = resp['images']['posters'][0]['file_path']
            img_url = IMAGE_BASE_URL + poster_path
        else:
            img_url = "/static/images/noImage.jpg"
        if resp['popularity']:        
            popularity = round(float(resp['popularity']), 2)
        if resp['overview']:
            overview = resp['overview']
        else:
            overview = "No information available."
        if resp['runtime']:
            runtime = resp['runtime']
        else:
            runtime = "No information available."
        if resp['genres']:
            genres = resp['genres']
        casts = []
        if resp['credits']['cast']:
            casts = resp['credits']['cast']
        crews = []
        if resp['credits']['crew']:
            crews = resp['credits']['crew']
        
        director = {}
        for crew in crews:
            if crew['job'] == 'Director':
                director[crew['id']] = crew['name']

        if resp['release_date']:
            date = resp['release_date']
            datetime_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            # Change the format of the datetime object
            release_date = datetime_obj.strftime("%B %d, %Y")
        else:
            release_date = 'Unknown'

        videos = None
        # Check if there are videos
        if resp['videos']['results']:
            videos = resp['videos']['results']
        
        video_urls = []
        if videos:
            # Check if there is a trailer available from YouTube
            for video in videos:
                if video['type'] == 'Trailer' and video['site'] == 'YouTube': 
                    video_urls.append(video['key'])
                              
        
        if video_urls:
            video_url = YOUTUBE_BASE_URL+video_urls[0]
        else:
            video_url = None
        
        movie = {
        id: {
            'title': title,
            'img_url': img_url,
            'popularity': popularity,
            'overview': overview,
            'runtime': runtime,
            'genres': genres,
            'casts': casts,
            'director': director,
            'release_date': release_date,
            'video_url': video_url,
            }
        }
        
        return movie


# Retrieve cast's detail
def get_cast_detail(id):

    resp = get_cast(id)
    
    id=id
    name =  resp['name']
    if resp['images']['profiles']: 
        img_url = IMAGE_BASE_URL + resp['images']['profiles'][0]['file_path']
    else:
        img_url = "/static/images/noImage.jpg"
    if resp['biography']:
        biography = resp['biography']
    else:
        biography = "No information available."
    movies = resp['movie_credits']['cast']
    movies.sort(key=lambda x: x['popularity'], reverse=True)
    
    if movies:
        max_pop = movies[0]['popularity']
        for movie in movies:
            movie['popularity'] = int(round((movie['popularity'] / max_pop) * 100))
      
    cast = {
        id: {
            'name': name,
            'img_url': img_url,
            'biography': biography,
            'movies': movies,
        }
    }

    return cast



# Retrieve movie ids by genre
def get_ids_by_genre(id):

    resp = get_movie_by_genre(id)

    
    movie_ids = [movie['id'] for movie in resp[0]['results']]
    genre = [genre['name'] for genre in resp[1]['genres'] if str(genre['id']) == id]
      
    return [movie_ids, genre]



# Retrieve movie reviews
def get_reviews(id):

    resp = get_movie(id)
    reviews = resp['reviews']['results']
    
    for review in reviews:
        avatar_path = review['author_details']['avatar_path']
        if avatar_path:
            if avatar_path.startswith('/https'):
                corrected_path = avatar_path[1:]
                review['author_details']['avatar_path'] = corrected_path
            else:
                review['author_details']['avatar_path'] = IMAGE_BASE_URL+avatar_path
                
    return reviews



# Retrieve trending movies data
def get_trending_movies_info():

    resp = get_trending_movies()

    resp = random.sample(resp['results'], 10)
    trending = {}
    for index, movie in enumerate(resp):
        if index >= 10:
            break
        if movie['poster_path']:
            movie_id = movie['id']
            title = movie['title']            
            img_url = IMAGE_BASE_URL + movie['poster_path']

            trending[movie_id] = {
                'title': title,
                'img_url': img_url}

        # backup movie
        else:
            movie_id = 840326
            title = "Sisu"
            img_url = IMAGE_BASE_URL + "ygO9lowFMXWymATCrhoQXd6gCEh.jpg"

            trending[movie_id] = {
                'title': title,
                'img_url': img_url}            
    
    return trending