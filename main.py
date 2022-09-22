import os
import flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import find_dotenv, load_dotenv
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    current_user
)

app = flask.Flask(__name__)

load_dotenv(find_dotenv())
app.secret_key = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)



db_url = os.getenv("DATABASE_URL")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def index():

    return flask.redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if flask.request.method == "POST":
        data = flask.request.form
        users = User.query.all()
        registered = False
        if len(users) == 0:
            first_user = User(username=data['username'])
            db.session.add(first_user)
            db.session.commit()
        for user in users:
            if user.username == data["username"]:
                registered = True
                return flask.redirect("/")
            
            if not registered:
                new_user = User(username=data['username'])
                db.session.add(new_user)
                db.session.commit()
                return flask.redirect("/")
                

    return flask.render_template("login.html")

app.run(
    host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", "8080")), debug=True
)