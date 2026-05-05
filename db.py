from pymongo import MongoClient
import boto3
from botocore.config import Config
import os

from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("URI")

mongo_client = MongoClient(uri)
db = mongo_client.get_database("db")

s3_client = boto3.client(
    service_name="s3",
    region_name="eu-north-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    config=Config(
        signature_version="s3v4",
        s3={'addressing_style': 'virtual'}
    )
)