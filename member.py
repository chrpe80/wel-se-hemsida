from flask import Blueprint, render_template


member = Blueprint('member', __name__)


@member.route('/show-pdf', methods=['GET'])
def show_pdf():
    return render_template("member/show-pdf.html")

@member.route('/find-pdf', methods=['GET'])
def find_pdf():
    return render_template("member/find-pdf.html")