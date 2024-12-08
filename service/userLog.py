from typing import Optional, List, Dict
from database.database import *
from datetime import datetime
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from models.userLog import *

def serialize_document(doc):
    if isinstance(doc, dict):
        return {k: serialize_document(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, list):
        return [serialize_document(i) for i in doc]
    else:
        return doc

async def get_all_user_log() -> List[Dict]:
    try:
        documents = await userLog_collection.find().to_list(1000)        
        serialized_documents = [serialize_document(doc) for doc in documents]
        return serialized_documents
    except Exception as e:
        logging.error(f"Error occurred while fetching user logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching user logs")

async def get_userLog_by_email_service(email: str):
    emailPermission = await EmailPermission_collection.find_one({"email": email})
    if  emailPermission:
         return emailPermission
    else:
        return {}
    
async def save_user_login_in_log(user: dict):    
    now = datetime.now(timezone.utc) 

    user_log = UserLog(
        userID=user.get("_id", ""),
        firstName=user.get("firstName", ""),
        lastName=user.get("lastName", ""),
        email=user.get("email", ""),
        type=user.get("type", ""),
        loginDates=now
    )    
    result = await userLog_collection.insert_one(user_log.dict())
    


