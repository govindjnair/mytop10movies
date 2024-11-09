from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6doneWlSihBXox7C0sKR6b'
Bootstrap5(app)


# Create DB
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db.init_app(app)


# Create Table

class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    image_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()

all_movies = []


def add_movie(title, year, description, rating, ranking, review, image_url):
    movie = Movie(title=title, year=year, description=description, rating=rating, ranking=ranking, review=review,
                  image_url=image_url)
    with app.app_context():
        db.session.add(movie)
        db.session.commit()


def read_data():
    all_movies.clear()
    with app.app_context():
        result = db.session.execute(db.select(Movie).order_by(Movie.title))
        all_data = result.scalars().all()
        for data in all_data:
            print(data)
            all_movies.append(data)


def delete_movie(title):
    with app.app_context():
        movie_to_delete = db.session.execute(db.select(Movie).where(Movie.title == title)).scalar()
        db.session.delete(movie_to_delete)
        db.session.commit()


def update_rating(title, value):
    with app.app_context():
        book_to_update = db.session.execute(db.select(Movie).where(Movie.title == title)).scalar()
        book_to_update.rating = value
        db.session.commit()


# add_movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     image_url="https://upload.wikimedia.org/wikipedia/en/c/c4/Phone_Booth_movie.jpg"
# )


read_data()
print(all_movies)


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add movie")


@app.route('/')
def home():
    read_data()
    return render_template("index.html", data=all_movies)


@app.route('/edit', methods=["POST", "GET"])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", movie=movie, form=form)


@app.route('/<movie>')
def modify(movie):
    delete_movie(movie)
    return redirect(url_for('home'))


@app.route('/add')
def add_from_web():
    form = AddMovieForm()
    return render_template("add.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
