from flask import flash
from botocore.exceptions import ClientError
from db import s3_client
import os


def upload_file_object(fileobject, bucket, filename, content_type):
    s3_client.upload_fileobj(
        Fileobj=fileobject,
        Bucket=bucket,
        Key=filename,
        ExtraArgs={'ContentType': content_type}
    )


def delete_file_object(bucket, key):
    s3_client.delete_object(Bucket=bucket, Key=key)


def get_contents(bucket):
    response = s3_client.list_objects(Bucket=bucket)
    return response.get("Contents", [])


def get_image_url_from_keys(keys: list):
    bucket = os.getenv("AWS_IMAGE_BUCKET_NAME")

    contents = s3_client.list_objects(Bucket=bucket).get("Contents", [])

    if contents:
        keys_in_bucket = [item["Key"] for item in contents]

        for key in keys:
            if key in keys_in_bucket:
                try:
                    url = s3_client.generate_presigned_url(
                        ClientMethod="get_object",
                        Params={"Bucket": bucket, "Key": key},
                        ExpiresIn=3600
                    )
                    return url

                except ClientError as e:
                    flash(f"Något gick fel: {e}")
                    continue
    return None