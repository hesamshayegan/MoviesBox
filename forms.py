from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class AddUserForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_profile = StringField('(Optional) Image URL')

class EditUserForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_profile = StringField('(Optional) Image URL')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class MovieReccomend(FlaskForm):
    """Movie Reccomender form."""
    
    movie_title = StringField('Find Movies by Title or Cast', validators=[DataRequired()])
    content = RadioField('Similar content', choices=[('overview', 'Check out movies with similar title'), 
                                                     ('soup', 'Explore movies with shared cast')])
    
class ReviewForm(FlaskForm):
    """ Review form for casts and movies """
    review = TextAreaField('What did you think of the movie or the person overall? Would you recommend it to others?',
                           validators=[DataRequired(),
                            Length(min=10, max=250)])

class Confirmation(FlaskForm):
    """ Confirmation form for account deletion """
    confirmation = RadioField('Delete account confirmation',
                              choices=[('yes', 'Yes'), ('no', 'No')],
                              validate_choice=False)
