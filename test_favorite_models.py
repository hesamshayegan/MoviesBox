"""Favorite models tests."""

# createdb MoviesBox_test
# FLASK_ENV=production python3 -m unittest test_favorite_models.py
# to run all tests at once -> python -m unittest discover

import os
from unittest import TestCase
from models import db, User, FavoriteCasts, FavoriteMovies
from sqlalchemy.exc import IntegrityError


# Set an environmental variable to use a different database for tests before importing app
os.environ['DATABASE_URL'] = "postgresql:///MoviesBox_test"

from app import app

app.config['SQLALCHEMY_ECHO'] = False

db.create_all()


class FavoriteModelTestCase(TestCase):
    """ Test the favorite models. """

    def setUp(self):
        """ Create client and add sample data. setUp method is an instance method. """

        User.query.delete()
        FavoriteCasts.query.delete()
        FavoriteMovies.query.delete()

        self.user = User.signup(
            username="testuser0",
            password="HASHED_PASSWORD",
            email="test0@test.com",
            image_profile=None
        )
        
        self.user.id = 1111
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """ Clean up any failed transaction. tearDown method is an instance method. """

        db.session.rollback()


    def test_favorite_models(self):
        """ Tests the basic functionality of the Favorite models. """

        movietest = FavoriteMovies(
                                    id = 272,
                                    title = 'Batman Begins',
                                    review = "Batman Begins is a great movie",
                                    user_id = self.user.id,
                                )
        movietest.pk = 1000

        db.session.add(movietest)
        db.session.commit()

        casttest = FavoriteCasts(
                                id = 6384,
                                name = 'Keanu Reeves',
                                user_id = self.user.id,
                            )
        
        casttest.pk = 2000

        db.session.add(casttest)
        db.session.commit()


        self.assertEqual(movietest.title, "Batman Begins")
        self.assertEqual(casttest.id, 6384)
        self.assertEqual(movietest.user_id, self.user.id)
        self.assertEqual(casttest.user_id, self.user.id)

    def test_favorite_movies_unique_constraint(self):
        """ Can a user add the same movie twice? """

        movietest = FavoriteMovies(
                                    id = 272,
                                    title = 'Batman Begins',
                                    review = None,
                                    user_id = self.user.id,
                                )
        movietest.pk = 1000

        db.session.add(movietest)
        db.session.commit()

        movietest2 = FavoriteMovies(
                                    id = 272,
                                    title = 'Batman Begins',
                                    review = None,
                                    user_id = self.user.id,
                                )
        movietest2.pk = 1001

        with self.assertRaises(IntegrityError) as context:
            db.session.add(movietest2)
            db.session.commit()

    def test_favorite_models_must_have(self):
        """ Can a user add a movie or cast without id? """

        with self.assertRaises(ValueError) as context:
            movietest = FavoriteMovies(
                        id=None,
                        title='Batman Begins',
                        review=None,
                        user_id=self.user.id,
                        )
            movietest.pk = 1000
            db.session.add(movietest)
            db.session.commit()

        self.assertEqual(str(context.exception), "movie id cannot be empty.")

        with self.assertRaises(ValueError) as context:
            casttest = FavoriteCasts(
                        id = None,
                        name = 'Keanu Reeves',
                        user_id = self.user.id,
                        )
        
            casttest.pk = 2000
            db.session.add(casttest)
            db.session.commit()
        
        self.assertEqual(str(context.exception), "cast id cannot be empty.")


    def test_favorite_casts_unique_constraint(self):
        """ Can a user add the same cast twice? """

        casttest = FavoriteCasts(
                                id = 6384,
                                name = 'Keanu Reeves',
                                user_id = self.user.id,
                            )
        
        casttest.pk = 2000

        db.session.add(casttest)
        db.session.commit()

        casttest2 = FavoriteCasts(
                                id = 6384,
                                name = 'Keanu Reeves',
                                user_id = self.user.id,
                            )
        
        casttest2.pk = 2001

        with self.assertRaises(IntegrityError) as context:
            db.session.add(casttest2)
            db.session.commit()
        
    
    def test_cascade_on_delete(self):
        """ Test that the cascade delete works for FavoriteMovies
            and FavoriteCasts when a user is deleted """

        self.assertEqual(len(FavoriteMovies.query.all()), 0)
        movietest = FavoriteMovies(
                                    id = 272,
                                    title = 'Batman Begins',
                                    review = None,
                                    user_id = self.user.id,
                                )
        movietest.pk = 1000

        db.session.add(movietest)
        db.session.commit()

        self.assertEqual(len(FavoriteMovies.query.all()), 1)

        self.assertEqual(len(FavoriteCasts.query.all()), 0)
        casttest = FavoriteCasts(
                                id = 6384,
                                name = 'Keanu Reeves',
                                user_id = self.user.id,
                            )
        
        casttest.pk = 2000

        db.session.add(casttest)
        db.session.commit()
        self.assertEqual(len(FavoriteCasts.query.all()), 1)

        db.session.delete(self.user)
        db.session.commit()

        self.assertEqual(len(FavoriteMovies.query.all()), 0)
        self.assertEqual(len(FavoriteCasts.query.all()), 0)