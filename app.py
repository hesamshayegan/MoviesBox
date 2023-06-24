import os, random
from dotenv import load_dotenv
from flask import Flask, render_template, flash, redirect, url_for, session, g, request
from flask_debugtoolbar import DebugToolbarExtension

from forms import AddUserForm, LoginForm, MovieReccomend, EditUserForm, ReviewForm, Confirmation
from models import db, connect_db, User, FavoriteCasts, FavoriteMovies
from sqlalchemy.exc import IntegrityError
from movie_recommender import movie_suggestions, cosine_sim2
from api_requests import get_movie_detail, get_cast_detail, get_ids_by_genre, get_reviews, get_trending_movies_info


CURR_USER_KEY = "curr_user"
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'


app = Flask(__name__)
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://esnegxrc:2qSG3PHWxUKMp_eO5TuTjOj86fQylCcR@mahmud.db.elephantsql.com/esnegxrc'
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "Chicken6768"
# toolbar = DebugToolbarExtension(app)

app.app_context().push()
connect_db(app)



##############################################################################
# User signup/login/logout routes
##############################################################################

@app.before_request
def add_user_to_g():
    """ If logged in, add curr user to Flask global. """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """ User signup process: Create and add a new user to the database.
    If the form is invalid, display the form again.
    If a user with the same username already exists, show a flash message and display the form again. """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = AddUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_profile=form.image_profile.data or User.image_profile.default.arg,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        signup_msg = "Welcome to MoviesBox! We hope you enjoy your time."
        return redirect(url_for("show_homepage", signup_msg=signup_msg ))

    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """ Handle user login. """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            welcome_msg = f"Hi {user.username}! Hope you find perfect movies to watch tonight."
            return redirect(url_for("show_homepage", welcome_msg=welcome_msg ))

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """ Handle logout of user. """

    do_logout()

    flash("Hope you had a great time. See you soon!", 'success')
    return redirect("/login")



@app.route('/users/<int:user_id>')
def users_show_profile(user_id):
    """ Show user profile. """

    user = User.query.get_or_404(user_id)

    return render_template('users/user_profile.html', user=user)



##############################################################################
# Edit user profile
##############################################################################
@app.route('/users/edit', methods = ["GET", "POST"])
def user_edit_profile():
    """ Update profile for current user. """

    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")

    user = g.user
    form = EditUserForm(obj=user)
    
    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_profile = form.image_profile.data or "/static/images/default-pic.png"

            db.session.commit()
            return redirect(f"/users/{user.id}")
                
        flash("Wrong password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)



##############################################################################
# Delete user profile
##############################################################################
@app.route('/users/delete', methods=["GET", "POST"])
def delete_user():
    """ Delete the user acccount. """

    form = Confirmation()

    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")

    if form.validate_on_submit():
        confirmation = form.confirmation.data
        if confirmation == 'yes':
            do_logout()
            db.session.delete(g.user)
            db.session.commit()
            flash("Account has been deleted. Hope to see you soon again!", "success")
            return redirect("/signup")
        
        else:
            flash("Account deletion canceled.", "info")
            return redirect(f"/users/{g.user.id}")

    return render_template("users/confirmation.html", form=form)



##############################################################################
# Homepage route
##############################################################################
@app.route('/')
def home():
    """ Redirect to the homepage """

    return redirect('/homepage')



##############################################################################
# Homepage route
##############################################################################
@app.route('/homepage', methods = ["GET", "POST"])
def show_homepage():
    """ Show homepage. """

    welcome_msg = request.args.get("welcome_msg", "")
    signup_msg  =  request.args.get("signup_msg", "")
    
    form = MovieReccomend()

    trending = get_trending_movies_info()
    
    if form.validate_on_submit():
        favorite_title = form.movie_title.data
        
        if form.content.data == 'overview':
            suggested_titles = movie_suggestions(favorite_title)
            
        else:
            suggested_titles = movie_suggestions(favorite_title, cosine_sim2)

        # if the user input doesn't exist in the database 
        if isinstance(suggested_titles, str):
            error_msg = suggested_titles
            return render_template('public/homepage.html', form=form, trending=trending, error_msg=error_msg)
        
        session['suggested_titles'] = suggested_titles
        return redirect(url_for('show_suggestions', suggested_titles=suggested_titles))
          
    else: 
        return render_template('public/homepage.html', form=form, trending=trending,
                                welcome_msg=welcome_msg, signup_msg=signup_msg)
                               
   

##############################################################################
# Movie suggesions route
##############################################################################
@app.route('/suggestions')
def show_suggestions():
    """ Show movie suggestions. """
    
    # genre status is deactive here
    genre = ""

    # Retrieve the suggested_titles from the session
    suggested_titles = session.get('suggested_titles')
    
    for id in suggested_titles.keys():
        
        movie = get_movie_detail(id)
        title = movie[id]['title']
        img_url = movie[id]['img_url']
        popularity = movie[id]['popularity']

        # Update suggested_titles with movies' image urls and popularity (%)     
        suggested_titles[id] = (title, img_url, popularity)
        
         
    return render_template('public/show.html', suggested_titles=suggested_titles,
                           genre=genre)
                        


##############################################################################
# Movie detail route
##############################################################################
@app.route('/movie_detail/<id>')
def show_movie_detail(id):
    """ Show movie detail. """
    
    movie = get_movie_detail(id)
  
    return render_template('public/movie_detail.html', movie=movie,
                           IMAGE_BASE_URL=IMAGE_BASE_URL)



##############################################################################
# Favorite movies route
##############################################################################
@app.route('/favorite_movies')
def favorite_movies():
    """ Show favorite movies. """ 

    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")

    else:
        movies = FavoriteMovies.query.filter_by(user_id = g.user.id).all()
        
        movies_info = []
        if movies:
            for movie in movies:
                movies_info.append(get_movie_detail(movie.id))
        
        return render_template('favorites/favorite_movies.html', movies_info=movies_info)



##############################################################################
# Add a new movie to favorites 
##############################################################################
@app.route('/favorite_movie_new/<id>')
def favorite_movie_new(id):
    """ Save a movie into FavoriteMovies db. """
    
    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")
    
    else:
        try: 
            movie = get_movie_detail(id)
            title = movie[id]['title']
            new_movie = FavoriteMovies(id=id, title=title, user_id=g.user.id)
            
            db.session.add(new_movie)
            db.session.commit()

            flash("Movie added", 'success')
            return redirect(url_for('show_movie_detail', id=id))
            
        except IntegrityError as e:
                flash("Movie already added", 'danger')
                return redirect(url_for('show_movie_detail', id=id))



##############################################################################
# Delete a movie from favorites
##############################################################################
@app.route('/favorite_movies/<id>/delete')
def favorite_movie_delete(id):
    """ Delete a favorite movie. """ 
    
    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")
    
    else:
        movie = FavoriteMovies.query.filter_by(id=id, user_id=g.user.id).first_or_404()
        db.session.delete(movie)
        db.session.commit()
        
        flash("Movie deleted", 'success')
        return redirect('/favorite_movies')



##############################################################################
# Movie suggesions by genre route
##############################################################################
@app.route('/genre_suggestions/<id>')
def genre_suggestions(id):
    """ Generates genre-specific movie suggestions based on the provided 'id'. """

    
    movie_info = get_ids_by_genre(id)
    random_ids = random.sample(movie_info[0], 12)
    genre = "".join(movie_info[1]).lower()
    
    suggested_titles = {}
    for id in random_ids:
        
        movie = get_movie_detail(id)
        title = movie[id]['title']
        img_url = movie[id]['img_url']
        popularity = movie[id]['popularity']
     
        suggested_titles[id] = (title, img_url, popularity)
        

    return render_template('public/show.html', suggested_titles=suggested_titles,
                           genre=genre)



##############################################################################
# Movie create review route
##############################################################################
@app.route('/review_movie/<id>', methods=["GET", "POST"])
def create_movie_review(id):
    """ Create movie review. """

    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")
    
    else:
        movie = FavoriteMovies.query.filter_by(id=id, user_id=g.user.id).first_or_404()
        form = ReviewForm()
        
        if form.validate_on_submit():
                movie.review = form.review.data
                db.session.commit()
                
                flash("Review added", 'success')
                return redirect('/favorite_movies')
            
        else:
                return render_template('favorites/create_movie_review.html', form=form)



##############################################################################
# Movie review route
##############################################################################
@app.route('/reviews/<id>')
def show_movie_review(id):
    """ Show movie reviews. """

    movies = FavoriteMovies.query \
                                .filter_by(id=id) \
                                .filter(FavoriteMovies.review.isnot(None)) \
                                .order_by(FavoriteMovies.pk.desc()) \
                                .all() 

    # Reviews from external sources
    ex_reviews = get_reviews(id)

    return render_template('public/movie_reviews.html', movies=movies, id=id,
                           ex_reviews=ex_reviews)



##############################################################################
# User reviews route
##############################################################################
@app.route('/users/<id>/reviews')
def show_user_reviews(id):
    """ Shows all the reviews that the user wrote. """
    
    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")
    
    else:        
        movies = FavoriteMovies.query \
                                    .filter_by(user_id=id) \
                                    .filter(FavoriteMovies.review.isnot(None)) \
                                    .order_by(FavoriteMovies.pk.desc()) \
                                    .all() 

        return render_template('favorites/user_reviews.html', id = int(id), movies=movies)



##############################################################################
# Edit review route
##############################################################################
@app.route('/reviews/<id>/edit', methods = ["GET", "POST"])
def edit_movie_review(id):
    """ Edit a movie review. """

    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")
    
    else:
        user = g.user
        movie = FavoriteMovies.query.filter_by(id=id, user_id=g.user.id).first_or_404()
        form = ReviewForm(obj=movie)
    
    if form.validate_on_submit():
            movie.review = form.review.data
            db.session.commit()

            flash("Review edited", 'success')
            return redirect(f"/users/{user.id}/reviews")

    return render_template('favorites/edit_movie_review.html', form=form, user_id=user.id)



##############################################################################
# Delete review route
##############################################################################
@app.route('/reviews/<id>/delete')
def delete_movie_review(id):
    """ Delete a movie review. """ 

    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")
    
    else:
        movie = FavoriteMovies.query.filter_by(id=id, user_id=g.user.id).first_or_404()
                
        movie.review = None
        db.session.commit()
        
        flash("Review deleted", 'success')
        return redirect(f"/users/{g.user.id}/reviews")



##############################################################################
# All reviews route
##############################################################################
@app.route('/all_reviews')
def show_all_reviews():
    """ Show selected reviews from random users. """
    
    movies = FavoriteMovies.query \
                                .filter(FavoriteMovies.review.isnot(None)) \
                                .order_by(FavoriteMovies.pk.desc()) \
                                .all()    

    random_reviews = random.sample(movies, 5)

    return render_template('public/all_reviews.html', random_reviews= random_reviews)



##############################################################################
# Cast detail route
##############################################################################
@app.route('/cast_detail/<id>')
def show_cast_detail(id):
    """ Show cast detail. """
    
    cast = get_cast_detail(id)
       
    return render_template('public/cast_detail.html', cast=cast,
                           IMAGE_BASE_URL=IMAGE_BASE_URL)


##############################################################################
# Favorite casts route
##############################################################################
@app.route('/favorite_casts')
def favorite_casts():
    """ Show favorite casts. """ 

    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")

    else:
        casts = FavoriteCasts.query.filter_by(user_id = g.user.id).all()
        
        casts_info = []
        if casts:
            for cast in casts:
                casts_info.append(get_cast_detail(cast.id))

        return render_template('favorites/favorite_casts.html', casts_info=casts_info)
 


##############################################################################
# Add a new cast to favorites 
##############################################################################
@app.route('/favorite_cast_new/<id>')
def favorite_cast_new(id):
    """ Save a cast into FavoriteCasts db. """
    
    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")
    
    else:
        try: 
            cast = get_cast_detail(id)
            name = cast[id]['name']
            new_cast = FavoriteCasts(id=id, name=name, user_id=g.user.id)
            
            db.session.add(new_cast)
            db.session.commit()

            flash("Cast added", 'success')
            return redirect(url_for('show_cast_detail', id=id))
            
        except IntegrityError as e:
                flash("Cast already added", 'danger')
                return redirect(url_for('show_cast_detail', id=id))



##############################################################################
# Delete a cast from favorites
##############################################################################
@app.route('/favorite_casts/<id>/delete')
def favorite_cast_delete(id):
    """ Delete a favorite cast. """ 

    if not g.user:
        flash("Please sign up or login", "danger")
        return redirect("/signup")
    
    else:
        cast = FavoriteCasts.query.filter_by(id=id, user_id=g.user.id).first_or_404()
        db.session.delete(cast)
        db.session.commit()
        
        flash("Cast deleted", 'success')
        return redirect('/favorite_casts')

        




