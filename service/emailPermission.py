from typing import Optional, List, Dict
from database.database import *
from datetime import datetime
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from models.emailPermission import *

def document_to_dict(document):
    if isinstance(document, list):
        return [document_to_dict(item) for item in document]
    if isinstance(document, dict):
        return {key: document_to_dict(value) for key, value in document.items()}
    if isinstance(document, ObjectId):
        return str(document)
    if isinstance(document, datetime):
        return document.isoformat()
    return document

#region convert objectid to str
def convert_objectid(data):
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data
#endregion

async def get_all_emailpermissions_service():
    result = await EmailPermission_collection.find().to_list(1000)
    return document_to_dict(result)

async def get_emailpermission_service(email: str):
    emailPermission = await EmailPermission_collection.find_one({"email": email.lower()})
    if  emailPermission:
        return emailPermission
    else:
        return {}
 


async def create_email_permission_service(email_permission: EmailPermission):

    email_permission_dict = email_permission.dict(by_alias=True)
    email_permission_dict["_id"] = ObjectId()
    now = datetime.now(timezone.utc)
    email_permission_dict["dateCreated"] = now
    email_permission_dict["email"] = email_permission.email.lower()
    # check duplicateKey of email
    check_duplicate = await EmailPermission_collection.find_one({"email": email_permission.email.lower()})
    if check_duplicate:
       raise HTTPException(status_code=404, detail="The email already exists.") 
    try:
        result = await EmailPermission_collection.insert_one(email_permission_dict)
        return str(result.inserted_id)
    except DuplicateKeyError:
        raise ValueError("DuplicateKeyError: email permission ID already exists")

async def delete_email_permission_service(permissionId: str) -> int:
    emailPermission = await EmailPermission_collection.find_one({"_id": ObjectId(permissionId)})
    if not emailPermission:
        raise HTTPException(status_code=404, detail="emailPermission not found")
    result = await EmailPermission_collection.delete_one({"_id": ObjectId(permissionId)})
    return result.deleted_count

async def update_email_permission_service(permissionId: str, email_permission: dict):
    emailPermission = await EmailPermission_collection.find_one({"_id": ObjectId(permissionId)})
    if not emailPermission:
        raise HTTPException(status_code=404, detail="emailPermission not found")    
     
    email_permission_dict = email_permission.dict(exclude_unset=True)
    now = datetime.now(timezone.utc)
    # email_permission_dict.dateUpdated = datetime.now(timezone.utc)
    email_permission_dict["dateUpdated"] = now
    result = await EmailPermission_collection.update_one(
        {"_id": ObjectId(permissionId)},
        {"$set": email_permission_dict}
    )    
    if result.matched_count == 0:
            return ResponseModel([],400, "Failed to Email permission setpoint")    
    if result.modified_count == 0:
            return {"data": [[]], "code": 500, "message": "Update failed"}
    return {"data": [[]], "code": 200, "message": "Update successful"}

async def get_email_permission_ById_service(permissionId: str):
    emailPermission = await EmailPermission_collection.find_one({"_id": ObjectId(permissionId)})
    if  emailPermission:
         return emailPermission
    else:
        return {}
    
async def check_user_email_with_permission(email: str):
    emailPermission = await EmailPermission_collection.find_one({"email": email.lower()})
    return emailPermission

async def add_default_email_permissions():

    now = datetime.now(timezone.utc)
    default_data = [
        {
            "email": "fatemi.narges55@gmail.com",
            "permission": "SUPEROPERATOR",
            "dateCreated": now,
            "dateUpdated": now
        },
        {
            "email": "javad.fattahi@uottawa.ca",
            "permission": "SUPEROPERATOR",
            "dateCreated": now,
            "dateUpdated": now
        }
    ]
    count = await EmailPermission_collection.count_documents({})
    if count == 0:
        await EmailPermission_collection.insert_many(default_data)
        logging.info("Default data added as the collection was empty.")
    else:
        logging.info("Collection is not empty. Default data not added.")




    
    

