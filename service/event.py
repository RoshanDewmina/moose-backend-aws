from models.events import *
from typing import Optional, List, Dict
from database.database import *
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
import logging
from fastapi.encoders import jsonable_encoder
from service.homes import *

async def get_event_service(home_Id: str):
    result = []
    events_cursor = event_collection.find({"homeID": home_Id}).sort("startTime", -1).limit(20)
    print(datetime.now(timezone.utc))
    event_docs = await events_cursor.to_list(length=None)
    if event_docs != []:
        for event_docs in event_docs:
           event_docs['_id'] = str(event_docs['_id'])
           result.append(event_docs)
        return result
    else:
        return []

async def get_event_byId(event_id: str):
    event = await event_collection.find_one({"_id": ObjectId(event_id)})
    if event is None:
        raise HTTPException(status_code=400, detail="Home not found")
    return Event(**event)

async def create_event_service(home_Id: str, event: Event):   
    event_dict = event.dict(by_alias=True)
    event_dict["homeID"] = home_Id
    event_dict["_id"] = ObjectId()
    now = datetime.now(timezone.utc)
    event_dict['dates']['dateCreated'] = now
    event_dict['dates']['dateUpdated'] = now
    try:
        result = await event_collection.insert_one(event_dict)
        return str(result.inserted_id)
    except DuplicateKeyError:
        raise ValueError("DuplicateKeyError: eventId already exists")

async def get_last_event_service(home_Id: str):
    now = datetime.now(timezone.utc)
    query = {
            "$and": [
                {"homeID": home_Id},
                {"cancelled": False},
                {"endTime": {"$gt": now}},
            ]
        }
    events_cursor = event_collection.find(query).sort("startTime")
    events = await events_cursor.to_list(length=None)
    if not events:
        print("No document found for the given homeId")
        return ResponseModel(data={}, code=400, message=f"event not found")
    return [Event(**event) for event in events]

async def cancel_event_service(home_Id: str, event_id:str):
    try:
        event_object_id = ObjectId(event_id)
    except InvalidId:
        return ResponseModel(data={}, code=400, message="Invalid event_id")

    now = datetime.now(timezone.utc)
    event = await event_collection.find_one({"_id": event_object_id, "homeID": home_Id})

    if not event:
        return ResponseModel(data={}, code=400, message=f"Eventid: {event_id} not found")

    update_result = await event_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": {"cancelled": True, "dateUpdated": now}}
    )
    if update_result.modified_count == 0:
        return ResponseModel(data={}, code=400, message=f"Failed to cancel the event")
    return ResponseModel(data={"modified_count": update_result.modified_count}, code=200, message="Event cancelled successfully")

async def opt_out_event_service(home_Id: str, event_id:str):
    try:
        event_object_id = ObjectId(event_id)
    except InvalidId:
        return ResponseModel(data={}, code=400, message="Invalid event_id")

    now = datetime.now(timezone.utc)
    event = await event_collection.find_one({"_id": event_object_id , "homeID": home_Id})
    if not event:
        return ResponseModel(data={}, code=400, message=f"Event not found")

    update_result = await event_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": {"active": False, "dateUpdated": now}}
    )
    if update_result.modified_count == 0:
        return ResponseModel(data={}, code=400, message=f"Failed to cancel the event")
    return ResponseModel(data={"modified_count": update_result.modified_count}, code=200, message="Event deactivated successfully")

