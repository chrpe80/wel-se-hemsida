from PIL import Image, UnidentifiedImageError
import base64
from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps
from io import BytesIO


def get_thumbnail(file: bytes, size: tuple[float, float]):

    size = size

    try:
        with Image.open(BytesIO(file)) as img:
            img.thumbnail(size)

            buffer = BytesIO()
            img.save(buffer, format="JPEG")

            return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except UnidentifiedImageError:
        return None


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if not current_user.is_admin:
            flash("Du har inte behörighet att komma åt den här sidan.")
            return redirect(url_for("index"))

        return func(*args, **kwargs)

    return wrapper
