"""SQLAlchemy models for MoviesBox."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

bcrypt = Bcrypt()
db = SQLAlchemy()


##########################################################################
class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_profile = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )


    @classmethod
    def signup(cls, username, email, password, image_profile):
        """Sign up user.
        
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_profile=image_profile,
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """ The class method finds a user by their password hash 
        and returns the user object if found, or False if not found. """
        

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False



##########################################################################
class FavoriteCasts(db.Model):
    """User's favorite casts."""

    __tablename__ = 'favorite_casts'

    pk = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    
    id = db.Column(
        db.Integer,
    )

    name = db.Column(
        db.Text,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    # Prevent the model from adding casts without id
    @validates("id")
    def validate_id(self, key, value):
        if value is None:
            raise ValueError("cast id cannot be empty.")
        return value

    # With this unique constraint in place, the same user is not be able to add the same cast multiple times. 
    # However, different users can still add the same person to their favorite casts. 
    __table_args__ = (
        db.UniqueConstraint('user_id', 'id', name='uq_favorite_casts_user_id_id'),
    )



##########################################################################
class  FavoriteMovies(db.Model):
    """ User's favorite Movies. """
    
    __tablename__ = 'favorite_movies'
    
    pk = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    
    id = db.Column(
        db.Integer,
    )

    title = db.Column(
        db.Text,
        nullable=False,
    )

    review = db.Column(
        db.Text,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    # Prevent the model from adding movies without id
    @validates("id")
    def validate_id(self, key, value):
        if value is None:
            raise ValueError("movie id cannot be empty.")
        return value

    # With this unique constraint in place, the same user is not be able to add the same movie multiple times. 
    # However, different users can still add the same film to their favorite movies. 
    __table_args__ = (
        db.UniqueConstraint('user_id', 'id', name='uq_favorite_movies_user_id_id'),
    )

    user = db.relationship('User')

##########################################################################
def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)

