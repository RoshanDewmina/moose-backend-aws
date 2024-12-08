from models.events import *
from typing import Optional, List, Dict
from database.database import *
from datetime import datetime
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
import logging
from fastapi.encoders import jsonable_encoder
from models.users import *
from models.homes import *
from pymongo import MongoClient, TEXT
from pymongo.collation import Collation
from passlib.context import CryptContext
from auth.jwt_handler import signJWT
from routes.admin import refresh_tokens

list_of_emails = ["javad.fattahi@uottawa.ca", "jon@jazzsolar.com","raghav@jazzsolar.com",
                  "goutam@jazzsolar.com", "ketan@jazzsolar.com", "navitha@jazzsolar.com",
                  "sanjaysundram@gmail.com", "fatemi.narges55@gmail.com"]

hash_helper = CryptContext(schemes=["bcrypt"])
# refresh_tokens = {}
async def token_from_apiKey(apiKey:str):
    user = await admin_collection.find_one({"apiKey": apiKey})
    if (user):
            tokens = signJWT(data={"user_id": user["email"], "type": user["type"]})
            return tokens['access_token']
    else:
        return None

