"""Seed database."""

from app import db
from models import User, FavoriteMovies

# createdb MoviesBox_db

db.drop_all()
db.create_all()

print('Database created')

# If table isn't empty, empty it
User.query.delete()

demo_user = User.signup(
                username='demo',
                password='123456',
                email='demo@MoviesBox.com',
                image_profile= "/static/images/default-pic.png",
            )
Bob = User.signup(
                username='Bob',
                password='p@ssw0rd123',
                email='Bob@MoviesBox.com',
                image_profile= "/static/images/Bob.png",
            )
Jake = User.signup(
                username='Jake',
                password='Th!s1s@P@ssw0rd',
                email='Jake@MoviesBox.com',
                image_profile= "/static/images/Jake.jpeg",
            )

Sara = User.signup(
                username='Sara',
                password='Th3R4nd0mP@ssw0rd',
                email='Sara@MoviesBox.com',
                image_profile= "/static/images/Sara.png",
            )

Eli = User.signup(
                username='Eli',
                password='1234ABCDE!@#',
                email='Eli@MoviesBox.com',
                image_profile= "/static/images/Eli.jpeg",
            )

FavoriteMovies.query.delete()

Bob_review = FavoriteMovies(
                id = 603,
                title = 'The Matrix',
                review = "The Matrix is a mind-bending, action-packed masterpiece that will leave you questioning everything you thought you knew about reality. Keanu Reeves gives a tour-de-force performance as Neo, a computer hacker who is drawn into a world where the machines have taken over and the human race is enslaved. The special effects are groundbreaking, the action is relentless, and the philosophical themes are thought-provoking. If you haven't seen The Matrix, do yourself a favor and watch it today",
                user_id = 2,
            )

Jake_review = FavoriteMovies(
                id = 603,
                title = 'The Matrix',
                review = "The movie can be slow at times and ending is a bit confusing",
                user_id = 3,
            )

Jake_review2 = FavoriteMovies(
                id = 280,
                title = 'Terminator 2: Judgment Day',
                review = "I just watched Terminator 2: Judgment Day for the first time and I was blown away. The action is incredible, the special effects are groundbreaking, and the story is both suspenseful and thought-provoking. Arnold Schwarzenegger is great as the Terminator, but it's Edward Furlong who steals the show as John Connor. I highly recommend this movie to anyone who loves action movies, science fiction, or just great cinema.",
                user_id = 3,
            )

Sara_review = FavoriteMovies(
                id = 272,
                title = 'Batman Begins',
                review = "Batman Begins is a great origin story for the Dark Knight. It's dark, gritty, and realistic, with a great cast and action-packed sequences. Highly recommended!",
                user_id = 4,
            )

Eli_review = FavoriteMovies(
                id = 55846,
                title = 'Blitz',
                review = "Blitz is a gritty, violent thriller that stars Jason Statham as a detective on the trail of a serial killer. The film is well-acted and suspenseful, but it's not for the faint of heart. Overall, I enjoyed Blitz, but I wouldn't recommend it to everyone.",
                user_id = 5,
            )


db.session.add_all([Bob_review, Jake_review, Jake_review2, Sara_review, Eli_review])
db.session.commit()

print('Demo users and reviews created')

