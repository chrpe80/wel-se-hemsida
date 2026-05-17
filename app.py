import sentry_sdk
import flask
from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
from bson.objectid import ObjectId
import os
from db import db
from helpers.operations_s3 import get_image_url_from_keys

from auth import auth
from admin import admin
from models import User
from public import public
from member import member

import errors

load_dotenv()

app = Flask(__name__)

sentry_sdk.init(
    os.getenv("SENTRY_DSN"),
    send_default_pii=True,
    max_request_body_size="always",
    traces_sample_rate=0,
    send_client_reports=False,
    auto_session_tracking=False,
)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(public)
app.register_blueprint(member)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth.login"
login_manager.login_message = "Du behöver logga in för att komma åt den här sidan."


@app.context_processor
def inject_logo():
    logga = {"logga": get_image_url_from_keys(["logga.png", "logga.jpg", "logga.jpeg"])}
    return logga


@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({"_id": ObjectId(user_id)})

    if not user_data:
        return None

    user = User()
    user.set_id(user_data.get("_id"))
    user.username = user_data.get("username")
    user.password = user_data.get("password")
    user.is_admin = user_data.get("is_admin")
    user.is_authenticated = True
    user.is_active = True
    user.is_anonymous = False

    return user


@app.route('/')
def index():
    image_url = get_image_url_from_keys(["hero_index.png", "hero_index.jpeg"])
    if image_url:
        return render_template("public/index.html", image_url=image_url)
    return render_template("public/index.html")


if __name__ == '__main__':
    app.run()
