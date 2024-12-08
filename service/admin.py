from typing import List, Dict
from database.database import *
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from models.users import *
from models.homes import *
from pymongo import MongoClient, TEXT
from service.emailPermission import *


async def add_user(data: dict) -> dict:
    if data.get('email'):
        try:
            dateCreated = datetime.now(timezone.utc) if not data.get('dates', {}).get('dateCreated') else data.get('dates', {}).get('dateCreated')
        except:
            dateCreated = datetime.now(timezone.utc)
            pass
        current_email = data.get('email').lower()
        
        check_email = await check_user_email_with_permission(current_email)
        if check_email is None:
            raise HTTPException(status_code=400, detail="Email is not allowed") 
        
        # if current_email not in [email.lower() for email in list_of_emails]:
        #     raise HTTPException(status_code=400, detail="Email is not allowed")
        _id = ObjectId()
        data.update({
            "_id": _id,
            "userID": str(_id),
            "email": current_email,
            "verified": True,
            "type": "USER" if not data.get('type') else data.get('type'),
            "language": "EN" if not data.get('language') else data.get('language'),
            "dates": {"dateCreated": dateCreated,
                     "dateUpdated": datetime.now(timezone.utc)}
        })
        admin = await admin_collection.insert_one(data)
        new_admin = await admin_collection.find_one({"_id": admin.inserted_id})
        return remove_sensitive_fields(admin_parser(new_admin))
    else:
        return {}

def remove_sensitive_fields(data: dict) -> dict:
    data.pop('password', None)
    return data

async def get_hemsc_id_by_apikey(api_key: str):

    hemsc_entry = await hemsc_collection.find_one({"apiKey": api_key})

    if hemsc_entry:
        return hemsc_entry.get("hemscID")
    return None

async def add_supper_user_in_hemsc(admin_collection: Collection) -> list:
    try:
        count = await admin_collection.count_documents({})
        print(f"Document count in 'admins' collection: {count}")
    except Exception as e:
        print(f"Error accessing 'admins' collection: {e}")
    valid_user_ids = []
    list_of_supperUser= ['javad.fattahi@uottawa.ca','fatemi.narges55@gmail.com']
    for user_email in list_of_supperUser:
        user_email_lower = user_email.lower()
        user = await admin_collection.find_one({'email': user_email_lower })
        # print(f"print user in for: {user}")
        if user:
            if user.get('_id'):
               valid_user_ids.append(str(user["_id"]))

    # print(f"Valid user IDs: {valid_user_ids}")
    return valid_user_ids

async def connect_user_to_homes(email: str):
    user = await admin_collection.find_one({"email": email.lower()})
    if user and user.get("apiKey")!= "":
        apiKey = user["apiKey"]
        try:
            hemsc_collection.update_one(
                {"$or": [{"apiKey": apiKey}]},
                {"$push": {"users": str(user["_id"])}}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update homes collection: {str(e)}")

async def update_user(user_id, user_dict):
    user_dict = {k: v for k, v in user_dict.items() if v is not None}
    if user_dict.get('email'):
        user_dict['email'] = user_dict.get('email').lower()
    
    result = await admin_collection.update_one(
        {"userID": user_id},
        {"$set": user_dict}
    )
    if result.matched_count == 0:
        return {"data": [], "code": 400, "message": "user id not found"}
    if result.modified_count == 0:
        return {"data": [], "code": 500, "message": "Update failed or no new data entry"}
    return {"data": [], "code": 200, "message": "Update successful"}

def convert_object_id(document):
    if isinstance(document, list):
        for doc in document:
            doc['_id'] = str(doc['_id'])
    else:
        document['_id'] = str(document['_id'])
    return document
        
async def get_all_user_service():
    document = await admin_collection.find().to_list(1000)
    if document:
        return convert_object_id(document)
    else:
        return {}
    
    
async def get_user_by_id_service(userid : str):    
    document = await admin_collection.find_one({"_id": ObjectId(userid)})    
    if document:
        return convert_object_id(document)
    else:
        return {}



