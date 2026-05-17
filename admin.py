from flask import Blueprint, request, render_template, redirect, flash, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from botocore.exceptions import ClientError
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import datetime
import os

from helpers.variables import identifiers, identifiers_img
from helpers.helper_functions import get_thumbnail, admin_required
from helpers.helper_classes import Responses
from helpers.operations_db import insert_one, find_one, find_all_in_collection, delete_one, update_one
from helpers.operations_s3 import upload_file_object, get_contents, delete_file_object

load_dotenv()

r = Responses()

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
            flash(r.all_fields_are_required())
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
            flash(r.operation_successful())
            return render_template(template)

        except DuplicateKeyError:
            flash(r.duplicate_key("Användaren", username))
            return render_template(template)

    return render_template(template)


@admin.route("/update-user", methods=["GET", "POST"])
@login_required
@admin_required
def update_user():
    all_users = find_all_in_collection("users")
    template = "admin/users/update_user.html"

    if request.method == "POST":
        user_id = request.form.get("select_user")
        if user_id is None:
            flash(r.field_missing("Användare"))
            return render_template(template, all_users=all_users)

        user = find_one("users", "_id", ObjectId(user_id))

        is_admin = request.form.get("is_admin") == "1"
        match is_admin:
            case None:
                is_admin = user["is_admin"]
            case "_":
                is_admin = request.form.get("is_admin") == "1"

        username = request.form["username"]
        match bool(username):
            case False:
                username = user["username"]

        password = request.form["password"]
        match bool(password):
            case False:
                password = user["password"]
            case True:
                password = generate_password_hash(password=password)

        fname = request.form["fname"]
        match bool(fname):
            case False:
                fname = user["fname"]

        lname = request.form["lname"]
        match bool(lname):
            case False:
                lname = user["lname"]

        email = request.form["email"]
        match bool(email):
            case False:
                email = user["email"]

        phone = request.form["phone"]
        match bool(phone):
            case False:
                phone = user["phone"]

        response = update_one(
            "users",
            "_id",
            ObjectId(user_id),
            is_admin=is_admin,
            username=username,
            password=password,
            fname=fname,
            lname=lname,
            email=email,
            phone=phone
        )

        if response:
            flash(r.operation_successful())
            return render_template(template, all_users=all_users)

        flash(r.operation_failed())
        return render_template(template, all_users=all_users)

    return render_template(template, all_users=all_users)


@admin.route("/delete-user", methods=["GET", "POST"])
def delete_user():
    response = find_all_in_collection("users")
    all_users = [item for item in response if not item["is_admin"]]

    if request.method == "POST":
        user_id = request.form.get("select_user")
        if user_id is None:
            flash(r.field_missing("Användare"))
            return render_template("admin/users/delete_user.html", all_users=all_users)

        response = delete_one("users", "_id", ObjectId(user_id))
        if response:
            flash(r.operation_successful())
            return redirect(url_for("admin.delete_user"))

        flash(r.operation_failed())
        return render_template("admin/users/delete_user.html", all_users=all_users)

    return render_template("admin/users/delete_user.html", all_users=all_users)


@admin.route("/add-article", methods=["GET", "POST"])
@login_required
@admin_required
def add_article():
    template = "admin/articles/add_article.html"
    collection = "articles"

    if request.method == "POST":
        identifier = request.form.get("identifier")
        content = request.form.get("content")
        image = request.files.get("image")

        if not all([identifier, content, image]):
            flash(r.all_fields_are_required())
            return render_template(template, identifiers=identifiers)

        if image is None:
            flash(r.operation_failed())
            return render_template(template, identifiers=identifiers)

        if not image.mimetype == "image/jpeg":
            flash(r.filetype("jpeg"))
            return render_template(template, identifiers=identifiers)

        image_data = image.read()

        thumbnail = get_thumbnail(image_data, (960, 540))

        if thumbnail is None:
            flash(r.operation_failed())
            return render_template(template)

        document = {"identifier": identifier, "content": content, "thumbnail": thumbnail}

        try:
            insert_one(collection, document)
            flash(r.operation_successful())
            return render_template(template, identifiers=identifiers)

        except DuplicateKeyError:
            flash(r.duplicate_key('Artikeln', identifier))
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
        image = request.files.get("image")

        if not all([identifier, new_content]):
            flash(r.fields_missing("Identifierare", "Innehåll"))
            return render_template(template, identifiers=identifiers)

        if not image:
            response = update_one(collection, "identifier", identifier, content=new_content)

            if not response:
                flash(r.operation_failed())
                return render_template(template, identifiers=identifiers)

            flash(r.operation_successful())
            return render_template(template, identifiers=identifiers)

        image_data = image.read()

        thumbnail = get_thumbnail(image_data, (960, 540))
        if thumbnail is None:
            flash(r.operation_failed())
            return render_template(template)

        response = update_one(collection, "identifier", identifier, content=new_content, thumbnail=thumbnail)
        if not response:
            flash(r.operation_failed())
            return render_template(template, identifiers=identifiers)

        flash(r.operation_successful())
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
            flash(r.field_missing("Identifierare"))
            return render_template(template, identifiers=identifiers)

        response = delete_one("articles", "identifier", identifier)
        if not response:
            flash(r.operation_failed())
            return render_template(template, identifiers=identifiers)

        flash(r.operation_successful())
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
            flash(r.field_missing("ID"))
            return render_template(template, identifiers_img=identifiers_img)

        if not image:
            flash(r.field_missing("Bild"))
            return render_template(template, identifiers_img=identifiers_img)

        if not image.mimetype == "image/jpeg":
            flash(r.filetype("jpeg"))
            return render_template(template, identifiers_img=identifiers_img)

        image_bytes = image.read()

        try:
            with Image.open(BytesIO(image_bytes)) as im:
                if not im.format:
                    flash("Okänt bildformat.")
                    return render_template(template, identifiers_img=identifiers_img)

                bucket = os.getenv("AWS_IMAGE_BUCKET_NAME")
                filename = f"{identifier}.{im.format.lower()}"
                content_type = im.get_format_mimetype()

                image.seek(0)
                upload_file_object(image, bucket, filename, ContentType=content_type)
                flash(r.operation_successful())
                return render_template(template, identifiers_img=identifiers_img)

        except ClientError:
            flash(r.operation_failed())
            return render_template(template, identifiers_img=identifiers_img)

        except UnidentifiedImageError:
            flash(r.operation_failed())
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
            flash(r.field_missing("Filnamn"))
            return render_template(template, keys=keys)

        bucket = os.getenv("AWS_IMAGE_BUCKET_NAME")
        delete_file_object(bucket, key)
        flash(r.operation_successful())
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
            flash(r.all_fields_are_required())
            return render_template(template)

        try:
            insert_one(collection, {"now": now, "title": title, "content": content})
            flash(r.operation_successful())
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
            flash(r.choose_option())
            return render_template(template, data=data)

        response = delete_one(collection, "now", identifier)

        if response:
            flash(r.operation_successful())
            return render_template(template, data=data)

        flash(r.operation_failed())
        return render_template(template, data=data)

    return render_template(template, data=data)


@admin.route("/add-book/", methods=["GET", "POST"])
@login_required
@admin_required
def add_book():
    template = "admin/publications/add_book.html"
    collection = "books"

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        price = request.form.get("price")
        description = request.form.get("description")
        image = request.files.get("image")

        if not all([title, author, price, description, image]):
            flash(r.all_fields_are_required())
            return render_template(template)

        if image is None:
            flash(r.operation_failed())
            return render_template(template)

        if not image.mimetype == "image/jpeg":
            flash(r.filetype("jpeg"))
            return render_template(template)

        image_data = image.read()

        thumbnail = get_thumbnail(image_data, (500, 500))

        if thumbnail is None:
            flash(r.operation_failed())
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
            flash(r.operation_successful())
            return render_template(template)

        except DuplicateKeyError:
            flash(r.duplicate_key("Dokumentet", title))
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
            flash(r.choose_option())
            return render_template(template, data=data)

        response = delete_one(collection="books", field="title", value=book_title)
        if response:
            flash(r.operation_successful())
            return render_template(template, data=data)

        flash(r.operation_failed())
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
            flash(r.all_fields_are_required())
            return render_template(template)

        if image is None:
            flash(r.operation_failed())
            return render_template(template)

        if not image.mimetype == "image/jpeg":
            flash(r.filetype("jpeg"))
            return render_template(template)

        image_data = image.read()

        thumbnail = get_thumbnail(image_data, (960, 540))

        if thumbnail is None:
            flash(r.operation_failed())
            return render_template(template)

        document = {
            "title": title,
            "artist": artist,
            "price": price,
            "thumbnail": thumbnail
        }

        try:
            insert_one(collection, document)
            flash(r.operation_successful())
            return render_template(template)

        except DuplicateKeyError:
            flash(r.duplicate_key("Dokumentet", title))
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
            flash(r.choose_option())
            return render_template(template, data=data)

        response = delete_one(collection="cards", field="title", value=card_title)
        if response:
            flash(r.operation_successful())
            return render_template(template, data=data)

        flash(r.operation_failed())
        return render_template(template, data=data)

    return render_template(template, data=data)


@admin.route("/add-center/", methods=["GET", "POST"])
@login_required
@admin_required
def add_center():
    template = "admin/center/add_center.html"
    if request.method == "POST":
        title = request.form.get("title", "")
        contacts = request.form.get("contacts", "")
        address = request.form.get("address", "")
        email = request.form.get("email", "")
        cc = request.form.get("cc", "")
        phone = request.form.get("phone", "")
        homepage = request.form.get("homepage", "")

        if not title:
            flash(r.field_missing("Titel"))
            return render_template(template)

        data = {
            "title": title,
            "contacts": contacts,
            "address": address,
            "email": email,
            "cc": cc,
            "phone": phone,
            "homepage": homepage
        }

        try:
            insert_one("centers", document=data)
            flash(r.operation_successful())
            return render_template(template)

        except DuplicateKeyError:
            flash(r.operation_failed())
            return render_template(template)

    return render_template(template)


@admin.route("/delete-center", methods=["GET", "POST"])
def delete_center():
    centers = find_all_in_collection("centers")
    if request.method == "POST":
        center_id = request.form.get("center")
        if center_id is None:
            flash(r.choose_option())
            return render_template("admin/center/delete_center.html", centers=centers)

        response = delete_one("centers", "_id", ObjectId(center_id))
        if response:
            flash(r.operation_successful())
            return render_template("admin/center/delete_center.html", centers=centers)

        flash(r.operation_failed())
        return render_template("admin/center/delete_center.html", centers=centers)

    return render_template("admin/center/delete_center.html", centers=centers)


@admin.route("/add-pdf", methods=["GET", "POST"])
def add_pdf():
    bucket = "pdfs-406868032142-eu-north-1-an"
    maximum = datetime.datetime.now().year
    if request.method == "POST":
        year = request.form.get("year")
        month = request.form.get("month")
        file = request.files.get("pdf")

        if file is None:
            flash(r.operation_failed())
            return render_template("admin/members/add_pdf.html", maximum=maximum)

        if not all([year, month, file]):
            flash(r.all_fields_are_required())
            return render_template("admin/members/add_pdf.html", maximum=maximum)

        if not file.mimetype == "application/pdf":
            flash(r.filetype("PDF"))
            return render_template("admin/members/add_pdf.html", maximum=maximum)

        filename = f"{year}_{month}.pdf"
        objects = get_contents(bucket)
        keys = [item["Key"] for item in objects]
        if filename in keys:
            flash(r.duplicate_key("Filnamn", filename))
            return render_template("admin/members/add_pdf.html", maximum=maximum)

        try:
            upload_file_object(
                fileobject=file,
                bucket=bucket,
                filename=filename,
                ContentType=file.content_type,
                Metadata={"year": year, "month": month}
            )

            flash(r.operation_successful())
            return render_template("admin/members/add_pdf.html", maximum=maximum)

        except ClientError as e:
            flash(e.response)
            return render_template("admin/members/add_pdf.html", maximum=maximum)

    return render_template("admin/members/add_pdf.html", maximum=maximum)


@admin.route("/delete-pdf", methods=["GET", "POST"])
@login_required
@admin_required
def delete_pdf():
    bucket = os.getenv("AWS_PDF_BUCKET_NAME")
    template = "admin/members/delete_pdf.html"
    contents = get_contents(bucket)
    keys = [item["Key"] for item in contents]

    if request.method == "POST":
        key = request.form.get("key")
        if not key:
            flash(r.field_missing("Filnamn"))
            return render_template(template, keys=keys)

        try:
            response = delete_file_object(bucket, key)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 204:
                flash(r.operation_successful())
                return redirect(url_for("admin.delete_pdf"))

            flash(r.operation_failed())
            return render_template(template, keys=keys)

        except ClientError:
            flash(r.operation_failed())
            return render_template(template, keys=keys)

    return render_template(template, keys=keys)
