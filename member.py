from flask import Blueprint, render_template, request
from db import s3_client
from helpers.operations_s3 import get_contents

member = Blueprint('member', __name__)


@member.route('/show-pdf', methods=['GET'])
def show_pdf():
    return render_template("member/show-pdf.html")


@member.route('/find-pdf', methods=['GET', "POST"])
def find_pdf():
    match request.method:
        case "POST":
            year = request.form.get("year")
            month = request.form.get("month")

            bucket = "pdfs-406868032142-eu-north-1-an"

            contents = get_contents(bucket)

            match all([year, month]):
                case True:
                    for content in contents:
                        key = content["Key"]
                        head = s3_client.head_object(Bucket=bucket, Key=key)
                        metadata = head["Metadata"]
                        f = metadata["year"] == year and metadata["month"] == month
                        if f:
                            url = s3_client.generate_presigned_url(
                                ClientMethod="get_object",
                                Params={
                                    "Bucket": bucket,
                                    "Key": key
                                },
                            )

                            return render_template("member/show-pdf.html", url=url)

                case False:
                    if year and not month:
                        pass

                    elif month and not year:
                        pass

                    else:
                        pass


    return render_template("member/find-pdf.html")

