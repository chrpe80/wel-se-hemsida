from flask import Blueprint, render_template
from bson.objectid import ObjectId
import mistune
from helpers.operations_db import find_all_in_collection, find_one
from helpers.operations_s3 import get_image_url_from_keys

public = Blueprint('public', __name__)


@public.route("/show-books/", methods=["GET"])
def show_books():
    books = find_all_in_collection("books").to_list()
    if books:
        return render_template("public/books.html", books=books)
    return render_template("public/books.html")


@public.route("/show-cards/", methods=["GET"])
def show_cards():
    cards = find_all_in_collection("cards").to_list()
    if cards:
        return render_template("public/cards.html", cards=cards)
    return render_template("public/cards.html")


@public.route("/product-book/<product_id>", methods=["GET"])
def product_book(product_id):
    book = find_one("books", "_id", ObjectId(product_id))

    if book:
        return render_template("public/product-book.html", book=book)

    return render_template("public/product-book.html")


@public.route("/product-card/<product_id>", methods=["GET"])
def product_card(product_id):
    book = find_one("cards", "_id", ObjectId(product_id))

    if book:
        return render_template("public/product-card.html", card=book)

    return render_template("public/product-card.html")


@public.route("/minestagarden/", methods=["GET"])
def minestagarden():
    article = find_one("articles", "identifier", "minestagården")
    img = get_image_url_from_keys(["minestagården.png", "minestagården.jpeg", "minestagården.jpg"])

    if article and img:
        article_html = mistune.html(article["content"])
        return render_template("public/minestagarden.html", article=article_html, img=img)

    return render_template("public/minestagarden.html")


@public.route("/program/", methods=["GET"])
def program():
    article = find_one("articles", "identifier", "program")
    img = get_image_url_from_keys(["program.png", "program.jpeg", "program.jpg"])

    if article and img:
        article_html = mistune.html(article["content"])
        return render_template("public/program.html", article=article_html, img=img)

    return render_template("public/program.html")


@public.route("/pillars/", methods=["GET"])
def pillars():
    article = find_one("articles", "identifier", "grundsatser")
    img = get_image_url_from_keys(["grundsatser.png", "grundsatser.jpeg", "grundsatser.jpg"])

    if article and img:
        article_html = mistune.html(article["content"])
        return render_template("public/pillars.html", article=article_html, img=img)

    return render_template("public/pillars.html")


@public.route("/history/", methods=["GET"])
def history():
    article = find_one("articles", "identifier", "historia")
    img = get_image_url_from_keys(["historia.png", "historia.jpeg", "historia.jpg"])

    if article and img:
        article_html = mistune.html(article["content"])
        return render_template("public/history.html", article=article_html, img=img)

    return render_template("public/history.html")


@public.route("/meditation/", methods=["GET"])
def meditation():
    article = find_one("articles", "identifier", "meditation")
    img = get_image_url_from_keys(["meditation.png", "meditation.jpeg", "meditation.jpg"])

    if article and img:
        article_html = mistune.html(article["content"])
        return render_template("public/meditation.html", article=article_html, img=img)

    return render_template("public/meditation.html")


@public.route("/healing/", methods=["GET"])
def healing():
    article = find_one("articles", "identifier", "helande")
    img = get_image_url_from_keys(["helande.png", "helande.jpeg", "helande.jpg"])

    if article and img:
        article_html = mistune.html(article["content"])
        return render_template("public/healing.html", article=article_html, img=img)

    return render_template("public/healing.html")


@public.route("/teaching/", methods=["GET"])
def teaching():
    article = find_one("articles", "identifier", "undervisning")
    img = get_image_url_from_keys(["undervisning.png", "undervisning.jpeg", "undervisning.jpg"])

    if article and img:
        article_html = mistune.html(article["content"])
        return render_template("public/teaching.html", article=article_html, img=img)

    return render_template("public/teaching.html")


@public.route("/membership/", methods=["GET"])
def membership():
    article = find_one("articles", "identifier", "medlemskap")
    img = get_image_url_from_keys(["medlemskap.png", "medlemskap.jpeg", "medlemskap.jpg"])

    if article and img:
        article_html = mistune.html(article["content"])
        return render_template("public/membership.html", article=article_html, img=img)

    return render_template("public/membership.html")


@public.route("/astrology/", methods=["GET"])
def astrology():
    article = find_one("articles", "identifier", "astrologi")
    img = get_image_url_from_keys(["astrologi.png", "astrologi.jpeg", "astrologi.jpg"])

    if article and img:
        article_html = mistune.html(article["content"])
        return render_template("public/astrology.html", article=article_html, img=img)

    return render_template("public/astrology.html")


@public.route("/show-notifications/", methods=["GET"])
def show_notifications():
    notifications = find_all_in_collection("notifications").to_list()

    if notifications:
        notifications_with_content_as_html = []
        for notification in notifications:
            notification["content"] = mistune.html(notification["content"])
            notifications_with_content_as_html.append(notification)

        return render_template("public/notifications.html", notifications=notifications_with_content_as_html)

    return render_template("public/notifications.html")


@public.route("/show-center/", methods=["GET"])
def show_center():
    centers = find_all_in_collection("centers").to_list()

    if centers:
        return render_template("public/centers.html", centers=centers)

    return render_template("public/centers.html")


@public.route("/contact/", methods=["GET"])
def contact():
    return render_template("public/contact.html")
