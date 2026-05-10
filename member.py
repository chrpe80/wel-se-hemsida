from flask import Blueprint, render_template, redirect, request, url_for, flash
from db import s3_client
from helpers.operations_s3 import get_contents
from helpers.helper_functions import get_metadata

member = Blueprint('member', __name__)


@member.route('/show-pdf', methods=['GET'])
def show_pdf():
    url = request.args.get("url", "")
    return render_template("member/show-pdf.html", url=url)


@member.route('/find-pdf', methods=['GET', "POST"])
def find_pdf():
    match request.method:
        case "POST":
            year = request.form.get("year")
            month = request.form.get("month")

            bucket = "pdfs-406868032142-eu-north-1-an"

            contents = get_contents(bucket)

            match all([not year, not month]):
                case True:
                    flash("Du måste fylla i något av fälten.")
                    return render_template("member/find-pdf.html")

            match all([year, month]):
                case True:
                    for content in contents:
                        metadata = get_metadata(s3_client, content, bucket)
                        match metadata["year"] == year and metadata["month"] == month:
                            case True:
                                url = s3_client.generate_presigned_url(
                                    ClientMethod="get_object",
                                    Params={
                                        "Bucket": bucket,
                                        "Key": content["Key"]
                                    },
                                )
                                return redirect(url_for(endpoint="member.show_pdf", url=url))

                case False:
                    match year and not month:
                        case True:
                            search_result = []
                            for content in contents:
                                metadata = get_metadata(s3_client, content, bucket)

                                match year == metadata["year"]:
                                    case True:
                                        url = s3_client.generate_presigned_url(
                                            ClientMethod="get_object",
                                            Params={
                                                "Bucket": bucket,
                                                "Key": content["Key"],
                                                "ResponseContentDisposition": "attachment"
                                            },
                                        )

                                        result = {"url": url, "year": metadata["year"], "month": metadata["month"]}

                                        search_result.append(result)

                            return render_template("member/show-search-result.html", search_result=search_result)

                    match month and not year:
                        case True:
                            search_result = []
                            for content in contents:
                                metadata = get_metadata(s3_client, content, bucket)

                                match month == metadata["month"]:
                                    case True:
                                        url = s3_client.generate_presigned_url(
                                            ClientMethod="get_object",
                                            Params={
                                                "Bucket": bucket,
                                                "Key": content["Key"],
                                                "ResponseContentDisposition": "attachment"
                                            },
                                        )

                                        result = {"url": url, "year": metadata["year"], "month": metadata["month"]}

                                        search_result.append(result)

                            return render_template("member/show-search-result.html", search_result=search_result)

    return render_template("member/find-pdf.html")
