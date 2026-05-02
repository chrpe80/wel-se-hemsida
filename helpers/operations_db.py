from db import db


def insert_one(collection, document):
    col = db.get_collection(collection)
    response = col.insert_one(document=document)
    return response


def find_one(collection, field, value):
    col = db.get_collection(collection)
    response = col.find_one({field: value})
    return response


def find_all_in_collection(collection):
    col = db.get_collection(collection)
    response = col.find({})
    return response


def update_one(collection, field_to_match, value_to_match, field_name, new_content):
    col = db.get_collection(collection)
    query_filter = {field_to_match: value_to_match}
    update_operation = {"$set": {field_name: new_content}}
    response = col.update_one(query_filter, update_operation)
    if response.modified_count == 0:
        return False
    return True


def delete_one(collection, field, value):
    col = db.get_collection(collection)
    query_filter = {field: value}
    response = col.delete_one(query_filter)
    if response.deleted_count == 0:
        return False
    return True
