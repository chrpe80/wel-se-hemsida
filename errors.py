from flask import render_template
from public import public
from admin import admin


@public.app_errorhandler(500)
def handle_500(e):
    return render_template('error_pages/500.html'), 500


@admin.app_errorhandler(404)
def handle_duplicate_key_error(e):
    return render_template('error_pages/404.html'), 404
