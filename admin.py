from flask import Blueprint, request, render_template, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from pymongo.errors import DuplicateKeyError
from botocore.exceptions import ClientError
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import datetime
import os

from helpers.variables import identifiers, identifiers_img
from helpers.helper_functions import get_thumbnail, admin_required
from helpers.operations_db import insert_one, find_all_in_collection, delete_one, update_one
from helpers.operations_s3 import upload_file_object, get_contents, delete_file_object

load_dotenv()

admin = Blueprint('admin', __name__)


@admin.route("/admin-start", methods=["GET"])
@login_required
@admin_required
def admin_start():
    if current_user.is_admin:
        return render_template("admin/start/admin-start.html")
    return render_template("auth/login.html")


@admin.route("/add-user", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():
    template = "admin/users/add_user.html"

    if request.method == "POST":
        is_admin = request.form["is_admin"] == "1"
        username = request.form["username"]
        password = request.form["password"]
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        phone = request.form["phone"]

        if not all([username, password, fname, lname, email, phone]):
            flash("Alla fält måste fyllas i.")
            return render_template(template)

        psw_hash = generate_password_hash(password)

        new_user = {
            "is_admin": is_admin,
            "username": username,
            "password": psw_hash,
            "fname": fname,
            "lname": lname,
            "email": email,
            "phone": phone
        }

        collection = "users"

        try:
            insert_one(collection, new_user)
            flash("Användaren lades till.")
            return render_template(template)

        except DuplicateKeyError:
            flash("Användaren finns redan.")
            return render_template(template)

    return render_template(template)


@admin.route("/add-article", methods=["GET", "POST"])
@login_required
@admin_required
def add_article():
    template = "admin/articles/add_article.html"
    collection = "articles"

    if request.method == "POST":
        identifier = request.form.get("identifier")
        content = request.form.get("content")

        if not all([identifier, content]):
            flash("Alla fält måste fyllas i.")
            return render_template(template, identifiers=identifiers)

        document = {"identifier": identifier, "content": content}

        try:
            insert_one(collection, document)
            flash("Artikeln lades till.")
            return render_template(template, identifiers=identifiers)

        except DuplicateKeyError:
            flash("Artikeln finns redan.")
            return render_template(template, identifiers=identifiers)

    return render_template(template, identifiers=identifiers)


@admin.route("/update-article", methods=["GET", "POST"])
@login_required
@admin_required
def update_article():
    template = "admin/articles/update_article.html"
    collection = "articles"

    if request.method == "POST":
        identifier = request.form.get("identifier")
        new_content = request.form.get("content")

        if not identifier or not new_content:
            flash("Alla fält måste fyllas i.")
            return render_template(template, identifiers=identifiers)

        response = update_one(collection, "identifier", identifier, "content", new_content)

        if not response:
            flash("Artikeln hittades inte.")
            return render_template(template, identifiers=identifiers)

        flash("Artikeln har uppdaterats.")
        return render_template(template, identifiers=identifiers)

    return render_template(template, identifiers=identifiers)


@admin.route("/delete-article", methods=["GET", "POST"])
@login_required
@admin_required
def delete_article():
    template = "admin/articles/delete_article.html"

    if request.method == "POST":
        identifier = request.form.get("identifier")

        if not identifier:
            flash("Identifierare saknas.")
            return render_template(template, identifiers=identifiers)

        response = delete_one("articles", "identifier", identifier)

        if not response:
            flash("Artikeln hittades inte.")
            return render_template(template, identifiers=identifiers)

        flash("Artikeln har raderats.")
        return render_template(template, identifiers=identifiers)

    return render_template(template, identifiers=identifiers)


@admin.route("/add-image", methods=["GET", "POST"])
@login_required
@admin_required
def add_image():
    template = "admin/images/add_image.html"

    if request.method == "POST":
        identifier = request.form.get("identifier")
        image = request.files.get("image")

        if not identifier:
            flash("Identifierare saknas.")
            return render_template(template)

        if not image:
            flash("Ingen bild vald.")
            return render_template(template)

        try:
            image_bytes = image.read()

            with Image.open(BytesIO(image_bytes)) as im:
                if not im.format:
                    flash("Okänt bildformat.")
                    return render_template(template, identifiers_img=identifiers_img)

                bucket = os.getenv("AWS_IMAGE_BUCKET_NAME")
                filename = f"{identifier}.{im.format.lower()}"
                content_type = im.get_format_mimetype()

            image.seek(0)
            upload_file_object(image, bucket, filename, content_type)

            flash("Bilden har laddats upp.")
            return render_template(template, identifiers_img=identifiers_img)

        except UnidentifiedImageError:
            flash("Filen är inte en giltig bild.")
            return render_template(template, identifiers_img=identifiers_img)

        except ClientError:
            flash("Kunde inte ladda upp bilden.")
            return render_template(template, identifiers_img=identifiers_img)

    return render_template(template, identifiers_img=identifiers_img)


@admin.route("/delete-image", methods=["GET", "POST"])
@login_required
@admin_required
def delete_image():
    template = "admin/images/delete_image.html"
    contents = get_contents(os.getenv("AWS_IMAGE_BUCKET_NAME"))
    keys = [item["Key"] for item in contents]

    if request.method == "POST":
        key = request.form.get("key")
        if not key:
            flash("Filnamn saknas.")
            return render_template(template, keys=keys)

        bucket = os.getenv("AWS_IMAGE_BUCKET_NAME")

        try:
            delete_file_object(bucket, key)
            flash("Bilden har raderats.")
            return render_template(template, keys=keys)

        except ClientError:
            flash("Kunde inte radera bilden.")
            return render_template(template, keys=keys)

    return render_template(template, keys=keys)


@admin.route("/add-notification/", methods=["GET", "POST"])
@login_required
@admin_required
def add_notification():
    template = "admin/notifications/add_notification.html"
    collection = "notifications"

    if request.method == "POST":
        now = datetime.datetime.now().strftime("%y-%m-%d %H:%M")
        title = request.form.get("title")
        content = request.form.get("content")

        if not all([title, content]):
            flash("Alla fält måste fyllas i.")
            return render_template(template)

        try:
            insert_one(collection, {"now": now, "title": title, "content": content})
            flash("Nyheten har lagts till.")
            return render_template(template)

        except DuplicateKeyError:
            flash(f"Det går inte att lägga till två nyheter samma minut.")
            return render_template(template)

    return render_template(template)


@admin.route("/delete-notification/", methods=["GET", "POST"])
@login_required
@admin_required
def delete_notification():
    template = "admin/notifications/delete_notification.html"
    collection = "notifications"
    data = find_all_in_collection(collection)

    if request.method == "POST":
        identifier = request.form.get("identifier")
        if not identifier:
            flash("Välj ett alternativ.")
            return render_template(template, data=data)

        response = delete_one(collection, "now", identifier)

        if response:
            flash("Nyheten togs bort.")
            return render_template(template, data=data)

        flash("Nyheten togs inte bort.")
        return render_template(template, data=data)

    return render_template(template, data=data)


@admin.route("/add-book/", methods=["GET", "POST"])
@login_required
@admin_required
def add_book():
    template = "admin/publications/add_book.html"
    collection = "books"

    if request.method == "POST":
        title = request.form.get("title").capitalize()
        author = request.form.get("author")
        price = request.form.get("price")
        description = request.form.get("description")
        image = request.files.get("image")

        if not all([title, author, price, description, image]):
            flash("Alla fält måste fyllas i.")
            return render_template(template)

        image_data = image.read()

        thumbnail = get_thumbnail(image_data)

        if thumbnail is None:
            flash("Dokumentet sparades inte.")
            return render_template(template)

        document = {
            "title": title,
            "author": author,
            "price": price,
            "description": description,
            "thumbnail": thumbnail
        }

        try:
            insert_one(collection, document)
            flash("Dokumentet sparades.")
            return render_template(template)

        except DuplicateKeyError:
            flash("Det finns redan ett dokument med den titeln.")
            return render_template(template)

    return render_template(template)


@admin.route("/delete-book/", methods=["GET", "POST"])
@login_required
@admin_required
def delete_book():
    template = "admin/publications/delete_book.html"
    data = find_all_in_collection("books")

    if request.method == "POST":
        book_title = request.form.get("book_title")
        if not book_title:
            flash("Välj en bok.")
            return render_template(template, data=data)

        response = delete_one(collection="books", field="title", value=book_title)
        if response:
            flash("Boken togs bort.")
            return render_template(template, data=data)

        flash("Boken togs inte bort.")
        return render_template(template, data=data)

    return render_template(template, data=data)


@admin.route("/add-card/", methods=["GET", "POST"])
@login_required
@admin_required
def add_card():
    template = "admin/publications/add_card.html"
    collection = "cards"

    if request.method == "POST":
        title = request.form.get("title")
        artist = request.form.get("artist")
        price = request.form.get("price")
        image = request.files.get("image")

        if not all([title, artist, price, image]):
            flash("Alla fält måste fyllas i.")
            return render_template(template)

        image_data = image.read()

        thumbnail = get_thumbnail(image_data)

        if thumbnail is None:
            flash("Dokumentet sparades inte.")
            return render_template(template)

        document = {
            "title": title,
            "artist": artist,
            "price": price,
            "thumbnail": thumbnail
        }

        try:
            insert_one(collection, document)
            flash("Dokumentet sparades.")
            return render_template(template)

        except DuplicateKeyError:
            flash("Det finns redan ett dokument med den titeln.")
            return render_template(template)

    return render_template(template)


@admin.route("/delete-card/", methods=["GET", "POST"])
@login_required
@admin_required
def delete_card():
    template = "admin/publications/delete_card.html"
    data = find_all_in_collection("cards")

    if request.method == "POST":
        card_title = request.form.get("card_title")
        if not card_title:
            flash("Välj ett kort.")
            return render_template(template, data=data)

        response = delete_one(collection="cards", field="title", value=card_title)
        if response:
            flash("Kortet togs bort.")
            return render_template(template, data=data)

        flash("Kortet togs inte bort.")
        return render_template(template, data=data)

    return render_template(template, data=data)


@admin.route("/add-center/", methods=["GET", "POST"])
@login_required
@admin_required
def add_center():
    template = "admin/center/add_center.html"
    if request.method == "POST":
        title = request.form.get("title")
        address = request.form.get("address")
        email = request.form.get("email")
        cc = request.form.get("cc")
        phone = request.form.get("phone")
        homepage = request.form.get("homepage", "")

        if not all([title, address, email, cc, phone]):
            flash("Fyll i alla fält.")
            return render_template(template)

        if not cc.isnumeric() and phone.isnumeric():
            flash("Telefonnummer och landskod måste vara numeriska.")
            return render_template(template)

        data = {
            "title": title,
            "address": address,
            "email": email,
            "cc": cc,
            "phone": phone,
            "homepage": homepage
        }

        try:
            insert_one("centers", document=data)
            flash("Dokumentet laddades upp.")
            return render_template(template)

        except ClientError:
            flash("Dokumentet laddades inte upp.")
            return render_template(template)

        except DuplicateKeyError:
            flash("Dokumentet laddades inte upp.")
            return render_template(template)

    return render_template(template)
