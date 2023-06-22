"""User model tests."""

# createdb MoviesBox_test
# FLASK_ENV=production python3 -m unittest test_user_model.py
# to run all tests at once -> python -m unittest discover

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, FavoriteCasts, FavoriteMovies


# Set an environmental variable to use a different database for tests before importing app
os.environ['DATABASE_URL'] = "postgresql:///MoviesBox_test"

from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///MoviesBox_test"
app.config['SQLALCHEMY_ECHO'] = False

db.create_all()


class UsersModelTestCase(TestCase):
    """ Test the user model. """

    def setUp(self):
        """Create client and add sample data."""

        User.query.delete()        
        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",                                
                                    email="test@test.com",
                                    password="hashed_psw",
                                    image_profile=None)

        self.testuser_id = 1111
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        """ Clean up any failed transaction. """

        db.session.rollback()



    #################################################
    # User.signup Tests
    #################################################
    def test_user_model(self):
        """ Tests the basic functionality of the `User` model. """

        u = User.signup(
            username="testuser0",
            password="HASHED_PASSWORD",
            email="test0@test.com",
            image_profile=None
        )
        
        db.session.commit()

        
        self.assertEqual(u.username, "testuser0")
        self.assertEqual(FavoriteMovies.query.all(), [])
        self.assertEqual(FavoriteCasts.query.all(), [])
    
    def test_valid_username_signup(self):
        """ Tests that a new `User` instance can be created with valid username credentials. """
        
        # correct credentials, no error
        user1 = User.signup(username="testuser1", password="HASHED_PASSWORD",
                             email="test1@test.com", image_profile=None)
        user1.id = 1
        db.session.commit()

        user_test = User.query.get(user1.id)
        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.username, "testuser1")
        self.assertEqual(user_test.email, "test1@test.com")
        self.assertNotEqual(user_test.password, "HASHED_PASSWORD")
        self.assertTrue(user_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        """ Tests that a new `User` instance cannot be created with invalid username credentials. """

        user2 = User.signup(username=None, password="HASHED_PASSWORD",
                            email="test2@test.com", image_profile=None)
        uid = 1000
        user2.id = uid

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        """ Tests that a new `User` instance cannot be created with invalid email credentials. """

        user3 = User.signup(username="test3", password="HASHED_PASSWORD",
                            email=None, image_profile=None)
        uid = 1001
        user3.id = uid
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        """ Tests that a new `User` instance cannot be created with invalid password credentials. """

        with self.assertRaises(ValueError) as context:
            User.signup("test", "email@gmail.com", None, None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("test", "email@gmail.com", "", None)
    


    #################################################
    # Authentication Tests
    #################################################
    def test_valid_authentication(self):
        """ Tests that the `authenticate()` class method returns the user object when valid credentials are used. """

        user4 = User.authenticate(username=self.testuser.username,
                                 password="hashed_psw")
        
        self.assertIsNotNone(user4)
        self.assertEqual(user4.id, self.testuser.id)
    
    def test_invalid_username_authentication(self):
        """ Tests that the `authenticate()` class method returns `False` when invalid username credentials are used. """

        self.assertFalse(User.authenticate(username="invalidusername",
                                           password="hashed_psw"))
    
    def test_invalid_password_authentication(self):
        """ Tests that the `authenticate()` class method returns `False` when invalid password credentials are used. """

        self.assertFalse(User.authenticate(username="testuser",
                                            password="invalidpassword"))



    #################################################
    #  Uniqueness constraint Tests
    #################################################    
    def test_duplicate_username(self):
        """ Tests that a user cannot be created with an existing username. """

        user5 = User.signup(username="test5", password="HASHED_PASSWORD",
                            email="test5@test.com", image_profile=None)
        uid = 1002
        user5.id = uid
        db.session.commit()

        # Same username as user5
        user6 = User.signup(username="test5", password="HASHED_PASSWORD",
                            email="test6@test.com", image_profile=None)
        uid = 1003
        user6.id = uid
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_duplicate_email(self):
        """ Tests that a user cannot be created with an existing email address. """ 

        user5 = User.signup(username="test5", password="HASHED_PASSWORD",
                            email="test5@test.com", image_profile=None)
        uid = 1002
        user5.id = uid
        db.session.commit()

        # Same email as user5
        user8 = User.signup(username="test8", password="HASHED_PASSWORD",
                            email="test5@test.com", image_profile=None)
        uid = 1004
        user8.id = uid
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()