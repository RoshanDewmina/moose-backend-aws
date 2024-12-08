
from bson import ObjectId
from datetime import datetime

def bson_encoder(data):
    if isinstance(data, dict):
        return {k: bson_encoder(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [bson_encoder(v) for v in data]
    elif isinstance(data, ObjectId):
        return str(data)  # Convert ObjectId to string
    elif isinstance(data, datetime):
        return data.isoformat()  # Convert datetime to ISO format string
    else:
        return data