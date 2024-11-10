from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from dotenv import load_dotenv
import os

load_dotenv()

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


def add_movie(title, year, description, image_url):
    movie = Movie(title=title, year=year, description=description, image_url=image_url)

    with app.app_context():
        db.session.add(movie)
        db.session.commit()


def read_data():
    all_movies.clear()
    with app.app_context():
        result = db.session.execute(db.select(Movie).order_by(desc(Movie.rating)))
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
    for movie in all_movies:
        movie.ranking = all_movies.index(movie) + 1
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


@app.route('/add', methods=["GET", "POST"])
def add_from_web():
    form = AddMovieForm()
    movie_title = form.title.data
    if form.validate_on_submit():
        response = requests.get("http://www.omdbapi.com/",
                                params={"apikey": os.getenv("OMDB_API_KEY"), "t": movie_title})
        data = response.json()
        if data["Response"] == "False":
            return render_template("oops.html", error=data.get('Error'))

        add_movie(title=data["Title"], year=data["Year"], description=data["Plot"], image_url=data["Poster"])

        with app.app_context():
            movie = db.session.execute(db.select(Movie).where(Movie.title == data["Title"])).scalar()
        if movie:
            movie_id = movie.id
            return redirect(url_for('edit', id=movie_id))
        else:
            return "Movie not found after adding. Please check the database."

    return render_template("add.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
