"""User View tests."""

# createdb MoviesBox_test
# FLASK_ENV=production python3 -m unittest test_views.py
# to run all tests at once -> python -m unittest discover

import os
from unittest import TestCase
from models import db, User, FavoriteCasts, FavoriteMovies

# Set an environmental variable to use a different database for tests before importing app
os.environ['DATABASE_URL'] = "postgresql:///MoviesBox_test"

from app import app, CURR_USER_KEY

app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False



class ViewTestCase(TestCase):
    """ Test view functions """

    def setUp(self):
        """Create client and add sample data. setUp method is an instance method """

        User.query.delete()

        self.client = app.test_client()
        

        self.testuser = User.signup(username="testuser",                                
                                    email="test@test.com",
                                    password="hashed_psw",
                                    image_profile=None)

        self.testuser_id = 1111
        self.testuser.id = self.testuser_id

        db.session.commit()

        self.movietest = FavoriteMovies(
                                    id = 272,
                                    title = 'Batman Begins',
                                    review = "Batman Begins is a great movie",
                                    user_id = 1111,
                                )
        
        self.movietest.pk = 1000

        self.movietest2 = FavoriteMovies(
                                    id = 55846,
                                    title = 'Blitz',
                                    review = "",
                                    user_id = 1111,
                                )
        
        self.movietest2.pk = 1001

        db.session.add(self.movietest)
        db.session.add(self.movietest2)
        db.session.commit()

        self.casttest = FavoriteCasts(
                                id = 6384,
                                name = 'Keanu Reeves',
                                user_id = 1111,
                            )
        
        self.casttest.pk = 2000

        db.session.add(self.casttest)
        db.session.commit()

       
    def tearDown(self):
        """ Clean up any failed transaction. tearDown method is an instance method """

        db.session.rollback()


    def test_homepage(self):
        """ Test the homepage """

        with self.client as c:               

            resp = c.get("/", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn('<h1 class="join-message text-center">What to Watch</h1>', html)


    def test_users_show_profile(self):
        """ Test the users show profile view. """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id          

            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"<p>email: {self.testuser.email}</p>", html)


    def test_show_suggestions(self):
        """ Test movie suggestions view """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            movie = {"movie_title": "Avatar", "content": "overview"}
            resp = c.post("/homepage", data=movie, follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="card-header"><b>The Matrix</b></div>', html)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            movie = {"movie_title": "Avatar", "content": "soup"}
            resp = c.post("/homepage", data=movie, follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="card-header"><b>Avatar: The Way of Water</b></div>', html)


    def test_show_movie_detail(self):
        """ Test the show movie detail view. """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/movie_detail/298618")
        
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<a href="/cast_detail/1113116">Andy Muschietti</a>', html)


    def test_favorite_movie_new(self):
        """ Can a user add a new movie? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/favorite_movie_new/603", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-success">Movie added</div>', html)

            movies = FavoriteMovies.query.filter(FavoriteMovies.user_id == self.testuser.id).all()
            self.assertEqual(len(movies), 3)

            new_movie = FavoriteMovies.query.filter_by(user_id = self.testuser.id, id=603).first_or_404()
            self.assertEqual(new_movie.title, "The Matrix")


    def test_favorite_movie_new_logged_out(self):
        """ Can a user add a new movie when logged out?. """

        with self.client as c:
            resp = c.get("/favorite_movie_new/603", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-danger">Please sign up or login</div>', html)


    def test_favorite_movie_delete(self):
        """ Can a user delete a movie """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/favorite_movies/{self.movietest.id}/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-success">Movie deleted</div>', html)

            movies = FavoriteMovies.query.filter(FavoriteMovies.user_id == self.testuser.id).all()
            self.assertEqual(len(movies), 1)
            

    def test_delete_movie_logged_out(self):
        """Can a user delete a movie when logged out? """
        
        with self.client as c:
            
            resp = c.get(f'/favorite_movies/{self.movietest.id}/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-danger">Please sign up or login</div>', html)

    
    def test_create_review_movie(self):
        """Can a user write a review for a movie? """
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            movie_review = {"review": "This is a greate movie!!!"}
            resp = c.post(f'/review_movie/{self.movietest2.id}',data=movie_review,
                          follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-success">Review added</div>', html)

            resp = c.get(f'/users/{self.testuser.id}/reviews')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('This is a greate movie!!!', html)
    

    def test_create_review_movie_logged_out(self):
        """Can a user write a review for a movie when logged out? """
        
        with self.client as c:

            resp = c.get(f'/review_movie/{self.movietest2.id}', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-danger">Please sign up or login</div>', html)

    
    def test_edit_review_movie(self):
        """ Can a user edit a review for a movie? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            movie_review = {"review": "This is an edited testing review"}
            resp = c.post(f'/reviews/{self.movietest.id}/edit', data=movie_review,
                          follow_redirects=True)
           
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-success">Review edited</div>', html)

            resp = c.get(f'/users/{self.testuser.id}/reviews')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<p class="text-justify"> This is an edited testing review</p>', html)


    def test_edit_review_movie_logged_out(self):
        """ Can a user edit a review for a movie when logged out? """

        with self.client as c:

            resp = c.get(f'/review_movie/{self.movietest2.id}', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-danger">Please sign up or login</div>', html)

    def test_delete_review_movie(self):
        """ Can a user delete a review for a movie? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/reviews/{self.movietest.id}/delete', follow_redirects=True) 
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-success">Review deleted</div>', html)


    def test_delete_review_movie_logged_out(self):
        """ Can a user delete a review for a movie when logged out? """

        with self.client as c:
            
            resp = c.get(f'/reviews/{self.movietest.id}/delete', follow_redirects=True) 
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-danger">Please sign up or login</div>', html)


    def test_show_cast_detail(self):
        
        with self.client as c:

            resp = c.get(f'/cast_detail/{self.casttest.id}')
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn('<h1> Keanu Reeves </h1>', html)
            self.assertIn('Keanu Charles Reeves is a Canadian actor', html)


    def test_favorite_cast_new(self):
        """ Can a user add a new cast? """
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/favorite_cast_new/2975", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-success">Cast added</div>', html)

            movies = FavoriteCasts.query.filter(FavoriteCasts.user_id == self.testuser.id).all()
            self.assertEqual(len(movies), 2)

            new_cast = FavoriteCasts.query.filter_by(user_id = self.testuser.id, id=2975).first_or_404()
            self.assertEqual(new_cast.name, "Laurence Fishburne")


    def test_favorite_cast_new(self):
        """ Can a user add a new cast when logged out? """ 

        with self.client as c:                          

            resp = c.get("/favorite_cast_new/2975", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-danger">Please sign up or login</div>', html)


    def test_favorite_cast_delete(self):
        """ Can a user delete a cast """ 

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/favorite_casts/{self.casttest.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True) 
            self.assertIn('<div class="alert alert-success">Cast deleted</div>', html)
            
            casts = FavoriteCasts.query.filter(FavoriteCasts.user_id == self.testuser.id).all()
            self.assertEqual(len(casts), 0)
    

    def test_favorite_cast_delete_logged_out(self):
        """ Can a user delete a cast when logged out """ 

        with self.client as c:

            resp = c.get(f"/favorite_casts/{self.casttest.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<div class="alert alert-danger">Please sign up or login</div>', html)