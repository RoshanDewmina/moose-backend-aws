from models.homes import *
from typing import Optional, List, Dict
from database.database import *
# from database.database import admin_collection, hemsc_collection
from datetime import datetime
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
import logging
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from service.mockup_deviceEnergy import *
from utils.encoders import bson_encoder

async def get_all_hemsc() -> List[Hemsc]:
    documents = await hemsc_collection.find().to_list(1000) #ToDo query

    result = []
    for document in documents:
        if '_id' in document:
            document['_id'] = str(document['_id'])
        for device in document.get('devices', []):
            if '_id' in device:
                device['_id'] = str(device['_id'])
            if 'setpoints' in device and isinstance(device['setpoints'], list):
                for setpoint in device['setpoints']:
                    if '_id' in setpoint:
                        setpoint['_id'] = str(setpoint['_id'])
        result.append(document)

    return result

async def get_hemsc_byId(api_Key: str) -> List[Hemsc]:
    documents = await hemsc_collection.find({"apiKey": api_Key}).to_list(1000)
    result = []    
    if documents != []:        
        for document in documents:
            if '_id' in document:
                document['_id'] = str(document['_id'])
            for device in document.get('devices', []):
                if '_id' in device:
                   device['_id'] = str(device['_id'])
                if 'setpoints' in device and isinstance(device['setpoints'], list):
                    for setpoint in device['setpoints']:
                       if '_id' in setpoint:
                         setpoint['_id'] = str(setpoint['_id'])
            result.append(document)
        return result
    else:
        return []

async def get_hemsc_hemscId(hemscID: str) -> Optional[Hemsc]:
    document = await hemsc_collection.find_one({"hemscID": hemscID})
    if document:
        if '_id' in document:
            document['_id'] = str(document['_id'])
        if 'devices' in document:
            for device in document['devices']:
                if '_id' in device:
                    device['_id'] = str(device['_id'])
                if 'setpoints' in device and isinstance(device['setpoints'], list):
                    for setpoint in device['setpoints']:
                        if '_id' in setpoint:
                            setpoint['_id'] = str(setpoint['_id'])
        return document
    else:
        return {}
    
async def get_hemsc_from_user_id(user_id: str) -> Optional[Hemsc]:    
    
    documents = await hemsc_collection.find({"users": user_id}).to_list(1000)
    result = []
    if documents != []:
        for document in documents:
            document['_id'] = str(document['_id'])
            for device in document['devices']:
                device['_id'] = str(device['_id'])
                if 'setpoints' in device and isinstance(device['setpoints'], list):
                    for setpoint in device['setpoints']:
                       if '_id' in setpoint:
                          setpoint['_id'] = str(setpoint['_id'])
            result.append(document)
        return result
    else:
        return []
    
async def create_hemsc(hemsc: Hemsc ):
    if hemsc.hemscID:
        check_hemscId = await hemsc_collection.find_one({"hemscID": hemsc.hemscID})
        if check_hemscId:
          raise ValueError("hemscID already exists")

    hemsc_dict = hemsc.dict(by_alias=True)
    hemsc_dict["_id"] = ObjectId()
    hemsc_dict["hemscID"] = str(hemsc_dict["_id"])
    # Delete Dome device
    hemsc_dict['devices'] = []
    # Check community
    hemsc_dict['community'] = 'Residential' if hemsc_dict['community'] == None else hemsc_dict['community']
    # Remove invalid users
    valid_user_ids = []
    for user_id in hemsc_dict['users']:
        user = await admin_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            valid_user_ids.append(user_id)

    list_of_supperUser= ['javad.fattahi@uottawa.ca','fatemi.narges55@gmail.com']
    for user_email in list_of_supperUser:
        user_email_lower = user_email.lower()
        user = await admin_collection.find_one({'email': user_email_lower })
        if user:
            if user.get('_id'):
               valid_user_ids.append(str(user["_id"]))

    hemsc_dict['users'] = valid_user_ids
    try:
        result = await hemsc_collection.insert_one(hemsc_dict)
        return str(result.inserted_id)
    except DuplicateKeyError:
        raise ValueError("DuplicateKeyError: hemscID already exists")

async def update_hemsc_data(home_id: str, hemsc: dict) -> dict:
    existing_hemsc = await hemsc_collection.find_one({"_id": ObjectId(home_id)})
    if existing_hemsc is None or not existing_hemsc:
        return {"data": [[]], "code": 400, "message": f"home/hemscId {home_id} does not exist"}
    
    update_dict = {}
    posted_data = hemsc.dict(exclude_unset=True)
    for key, value in posted_data.items():
        # Skip 'dateCreated' and nested 'dateCreated' fields
        if key == "dateCreated":
            continue
        
        if key in existing_hemsc:
            # Handle nested updates (e.g., updating fields within 'devices' or 'preference')
            if isinstance(existing_hemsc[key], dict) and isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    # Skip nested 'dateCreated' in subdocuments
                    if sub_key == "dateCreated":
                        continue
                    update_dict[f"{key}.{sub_key}"] = sub_value
                    # Update the 'dateUpdated' field if a nested value is changed
                    update_dict[f"{key}.dateUpdated"] = datetime.now(timezone.utc)
            elif existing_hemsc[key] != value:
                update_dict[key] = value
                update_dict["dates.dateUpdated"] = datetime.now(timezone.utc)
        else:
            update_dict[key] = value
    if update_dict != {}:
        update_dict["dates.dateUpdated"] = datetime.now(timezone.utc)
    
    # Perform the update operation
    result = await hemsc_collection.update_one(
        {"_id": ObjectId(home_id)},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        return {"data": [[]], "code": 400, "message": "home/hemscId not found"}
    if result.modified_count == 0:
        return {"data": [[]], "code": 500, "message": "Update failed"}
    hemsc = await hemsc_collection.find_one({"_id": ObjectId(home_id)})
    hemsc = bson_encoder(hemsc)
    return {"data": [hemsc], "code": 200, "message": "Update successful"}

async def delete_hemsc_data(homeid: str) -> dict:
    home = await hemsc_collection.find_one({"_id": ObjectId(homeid)})

    if not home:
        raise HTTPException(status_code=404, detail="Home not found")

    result = await admin_collection.delete_many({"_id": {"$in": home["users"]}})
    if result.deleted_count == 0:
        logging.info("No users found to delete")
    result = await hemsc_collection.delete_one({"_id": ObjectId(homeid)})

    return result.deleted_count

async def get_home(home_id: str):
    home = await hemsc_collection.find_one({"_id": ObjectId(home_id)})
    if home is None:
        print("No document found for the given home_id")
        return ResponseModel(data={}, code=400, message=f"Data is not found")
    return Hemsc(**home)

async def get_devices(home_id: str):
    print("Fetching device data")
    document = await hemsc_collection.find_one({"_id": ObjectId(home_id)})
    print("Fetched document:")

    if document is None or not document:
        print("No document found for the given home_id")
        return ResponseModel(data={}, code=400, message=f"Data for home/hemscId {home_id} is not found")

    if '_id' in document:
        document['_id'] = str(document['_id'])

    if 'devices' in document:
        for device in document['devices']:
            if '_id' in device:
                device['_id'] = str(device['_id'])
            if 'setpoints' in device and isinstance(device['setpoints'], list):
                for setpoint in device['setpoints']:
                    if '_id' in setpoint:
                        setpoint['_id'] = str(setpoint['_id'])
    return document

async def get_device_from_home_deviceEndpoint(home_id:str, device_id: str) -> Device:

    home = await get_hemsc_hemscId(home_id)
    if home == {}:
        print("No document found for homeId")
        return ResponseModel(data={}, code=400, message=f"home/hemscId {home_id} is not found")

    if ObjectId.is_valid(device_id):
        which_find = {"devices._id": ObjectId(device_id)}
        which_select = {"_id": ObjectId(device_id)}
    else:
        which_find = {"devices.macAddress": device_id}
        which_select = {"macAddress": device_id}

    query = {
        "$and": [
            {"_id": ObjectId(home_id)},
            which_find
        ]
    }
    projection = {
        "devices": {
            "$elemMatch": which_select
        }
    }
    home = await hemsc_collection.find_one(query, projection)
    if home is None or not home:
        print("No document found")
        return ResponseModel(data={}, code=400, message=f"deviceId {device_id} is not found")
    # if not home or 'devices' not in home or not home['devices']:
    #     raise HTTPException(status_code=400, detail="Device not found")
    for device in home['devices']:
        device['_id'] = str(device['_id'])
        if 'setpoints' in device and isinstance(device['setpoints'], list):
            for setpoint in device['setpoints']:
                if '_id' in setpoint:
                   setpoint['_id'] = str(setpoint['_id'])
    device = home['devices'][0]
    return device

async def create_devices(home_id:str, device: Device):
    # Check device with the given MAC address already exists
    check_macAdress = await hemsc_collection.find_one(
        {"_id": home_id, "devices.macAddress": device.macAddress},
        {"devices.$": 1}
    )
    if  check_macAdress:
        raise HTTPException(status_code=400, detail="This MAC address is already in use")
    if not isinstance(home_id, ObjectId):
        home_id = ObjectId(home_id)

    new_device = device.dict()
    new_device["_id"] = ObjectId()
    new_device["dateCreated"] = datetime.now(timezone.utc)
    new_device["dateUpdated"] = datetime.now(timezone.utc)
    new_device["setpoints"] = []

    new_device['status'] = 0 if new_device['status'] == None else new_device['status']

    # Add new device to the home
    update_hemsc = await hemsc_collection.update_one(
        {"_id": ObjectId(home_id)},
        {"$push": {"devices": new_device}}
    )
    # logging.info(f"Update result: {update_hemsc.raw_result}")
    if update_hemsc.modified_count == 1:
        new_device["_id"] = str(new_device["_id"])
        return new_device
    else:
        raise HTTPException(status_code=500, detail="Failed to create device")

async def delete_device_data(home_id:str, device_id: str) -> int:

    home = await get_hemsc_hemscId(home_id)
    if home == {}:
        print("No document found for homeId")
        return ResponseModel(data={}, code=400, message=f"home/hemscId {home_id} is not found")
    # check
    if ObjectId.is_valid(device_id):
        which_find = {"devices._id": ObjectId(device_id)}
        which_delete = {"_id": ObjectId(device_id)}
    else:
        which_find = {"devices.macAddress": device_id}
        which_delete = {"macAddress": device_id}

    if not isinstance(home_id, ObjectId):
        home_id = ObjectId(home_id)

    result = await hemsc_collection.find_one({
        "$and": [
            {"_id": home_id},
            which_find,
        ],
    }, {
        "devices": {"$elemMatch": which_delete},
    })
    # logger.info(f"Query result: {result}")
    if not result or "devices" not in result or not result["devices"]:
        print("not found")
        return ResponseModel({},400, f"Data for Device is not found")

    result = await hemsc_collection.update_one(
        {
            "$and": [
                {"_id": ObjectId(home_id)},
                which_find,
            ]
        },
        {
            "$pull": {
                "devices": which_delete,
            }
        }
    )
    if result.modified_count == 0:
        return ResponseModel({},400, "Device not deleted")
        # raise HTTPException(status_code=400, detail="Device not deleted")

    return ResponseModel({},  200,  "Device deleted successfully")

async def get_device_from_home_for_update(home_id: str, device_id: str) -> Device:
    # device_obj_id = ObjectId(device_id)
    which_find = {"devices.macAddress": device_id}
    which_select = {"macAddress": device_id}
    if ObjectId.is_valid(device_id):
        which_find = {"devices._id": ObjectId(device_id)}
        which_select = {"_id": ObjectId(device_id)}

    if not isinstance(home_id, ObjectId):
        home_id = ObjectId(home_id)

    result = await hemsc_collection.find_one({
        "$and": [
            {"_id": home_id},
            which_find,
        ],
    }, {
        "devices": {"$elemMatch": which_select},
    })
    # logger.info(f"Query result: {result}")
    if not result or "devices" not in result or not result["devices"]:
        raise HTTPException(status_code=400, detail="Device not found")
    device_data = result["devices"][0]
    return device_data

async def update_device_data(home_id: str, device_data: DeviceUpdated, device_id: str):
    # Determine the query based on the device_id type
    which_find = {"devices.macAddress": device_id}
    which_select = {"macAddress": device_id}
    if ObjectId.is_valid(device_id):
        which_find = {"devices._id": ObjectId(device_id)}
        which_select = {"_id": ObjectId(device_id)}

    # Convert home_id to ObjectId if necessary
    if not isinstance(home_id, ObjectId):
        home_id = ObjectId(home_id)

    # Find the device in the database
    result = await hemsc_collection.find_one({
        "$and": [
            {"_id": home_id},
            which_find,
        ],
    }, {
        "devices": {"$elemMatch": which_select},
    })

    if not result or "devices" not in result or not result["devices"]:
        return ResponseModel({}, 400, f"Data for Device is not found")

    # Load existing device data from the database (dictionary format)
    device_data_from_db = result["devices"][0]

    # Update the dateUpdated field
    now = datetime.now(timezone.utc)
    device_data_dict = device_data.dict(exclude_unset=True)
    if 'dateUpdated' in device_data_dict:
        device_data_dict['dateUpdated'] = now

    # Update device_data_from_db with the fields provided in device_data_dict
    for key, value in device_data_dict.items():
        if key == "dateCreated":  # Exclude dateCreated from being updated
            continue
        device_data_from_db[key] = value
    # Perform the update operation, targeting the specific device in the array
    result = await hemsc_collection.update_one(
        {"_id": home_id, "devices._id": ObjectId(device_id)},
        {"$set": {"devices.$": device_data_from_db}}
    )

    if result.matched_count == 0:
        return ResponseModel({}, 400, f"Device not found")
    result = await hemsc_collection.find_one({
        "$and": [
            {"_id": home_id},
            which_find,
        ],
    }, {
        "devices": {"$elemMatch": which_select},
    })

    if not result or "devices" not in result or not result["devices"]:
        return ResponseModel({}, 400, f"Data for Device is not found")
    return result["devices"][0]

async def get_device_from_home(home_id:str, device_id: str) -> Device:
    if ObjectId.is_valid(device_id):
        which_find = {"devices._id": ObjectId(device_id)}
        which_select = {"_id": ObjectId(device_id)}
    else:
        which_find = {"devices.macAddress": device_id}
        which_select = {"macAddress": device_id}

    query = {
        "$and": [
            {"_id": ObjectId(home_id)},
            which_find
        ]
    }
    projection = {
        "devices": {
            "$elemMatch": which_select
        }
    }
    home = await hemsc_collection.find_one(query, projection)
    if home is None or not home:
        print("No document found")
        return ResponseModel(data={}, code=400, message=f"deviceId: {device_id} is not found")
    # if not home or 'devices' not in home or not home['devices']:
    #     raise HTTPException(status_code=400, detail="Device not found")
    for device in home['devices']:
        device['_id'] = str(device['_id'])
        if 'setpoints' in device and isinstance(device['setpoints'], list):
            for setpoint in device['setpoints']:
                if '_id' in setpoint:
                   setpoint['_id'] = str(setpoint['_id'])
    device = home['devices'][0]
    return device

async def get_device_from_home_setpoint(home_id: str, device_id: str) -> Device:
    device_query = {"devices._id": ObjectId(device_id)} if ObjectId.is_valid(device_id) else {"devices.macAddress": device_id}
    home = await hemsc_collection.find_one({"_id": ObjectId(home_id), **device_query}, {"devices.$": 1})

    if not home or 'devices' not in home or not home['devices']:
        raise HTTPException(status_code=404, detail="Device not found")

    device = home['devices'][0]
    device['_id'] = str(device['_id'])

    for setpoint in device['setpoints']:
        setpoint['_id'] = str(setpoint['_id'])

    return Device(**device)

def build_query_and_projection(home_id: str, device_id: str):
    # Construct the query based on whether device_id is a valid ObjectId
    if ObjectId.is_valid(device_id):
        which_find = {"devices._id": ObjectId(device_id)}
    else:
        which_find = {"devices.macAddress": device_id}

    query = {
        "$and": [
            {"_id": ObjectId(home_id)},
            which_find
        ]
    }
    return query

async def update_schedules_service(home_id: str, device_id: str, schedule_day: str, schedules: List[Schedule]):
    query = build_query_and_projection(home_id, device_id)
    # Update the dateUpdated for each schedule
    for schedule in schedules:
        schedule.dateUpdated = datetime.now(timezone.utc)
    if "dateCreated" in schedule:
        schedule.pop("dateCreated")
    update_data = {
        "$set": {
            f"devices.$.schedules.{schedule_day}": jsonable_encoder(schedules),
            "devices.$.dateUpdated": datetime.now(timezone.utc)
        }
    }

    result = await hemsc_collection.update_one(query, update_data)
    if result.matched_count == 0:
        return ResponseModel({},400, f"deviceId: {device_id}  not found")
    if result.modified_count == 0:
        return ResponseModel({},400, f"Schedules not updated")
    return result

async def create_day_schedules_service(home_id: str, device_id: str,schedule_day: str, schedules: List[Schedule]):
    if ObjectId.is_valid(device_id):
        which_find = {"devices._id": ObjectId(device_id)}
    else:
        which_find = {"devices.macAddress": device_id}
    query = {
        "$and": [
            {"_id": ObjectId(home_id)},
            which_find
        ]
    }
    current_time = datetime.now(timezone.utc)
    for schedule in schedules:
        schedule.dateUpdated = current_time
    update_data = {
        "$addToSet": {
            f"devices.$.schedules.{schedule_day}": {"$each": jsonable_encoder(schedules)}
        },
        "$set": {
            "devices.$.dateUpdated": current_time
        }
    }
    result = await hemsc_collection.update_one(query, update_data)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Schedules not updated")
    return result

async def create_setpoint_schemas(home_id: str, device_id: str,setpoint: Setpoint):
    if ObjectId.is_valid(device_id):
        device_query = {"devices._id": ObjectId(device_id)}
    else:
        device_query = {"devices.macAddress": device_id}
    device = await hemsc_collection.find_one({
                                              "$and": [{"_id": ObjectId(home_id)},
                                                        device_query]
                                            })
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device_setpoints = device.get('devices', [])[0].get('setpoints', [])
    if len(device_setpoints) >= 8:
        raise HTTPException(status_code=400, detail="Maximum of 8 setpoints")
    now = datetime.now(timezone.utc)
    setpoint.dates = {
        "dateCreated": now,
        "dateUpdated": now
    }
    return setpoint, device_query, now

async def delete_setpoint_schemas(home_id: str, device_id: str, setpoint_index: int):
    if ObjectId.is_valid(device_id):
        device_query = {"devices._id": ObjectId(device_id)}
    else:
        device_query = {"devices.macAddress": device_id}

    home = await hemsc_collection.find_one({"_id": ObjectId(home_id)})

    if home is None or not home:
        print("No document found")
        return ResponseModel({}, 400, "Home not found")
    # if not home:
    #     raise HTTPException(status_code=404, detail="Home not found")

    # Find the correct device and setpoint
    found_device = None
    found_setpoint = None
    for device in home['devices']:

        if str(device['_id']) == device_id or device.get('macAddress') == device_id:
            found_device = device
            if setpoint_index < len(found_device['setpoints']):
                found_setpoint = found_device['setpoints'][setpoint_index]
            break

    if not found_device:
        print("not found")
        return ResponseModel({}, 400, "deviceId: {device_id} not found")
    if not found_setpoint:
        return ResponseModel({}, 400, "Setpoint not found")
    # if not found_device or not found_setpoint:
    #     raise HTTPException(status_code=404, detail="Device or setpoint not found")

    update_result = await hemsc_collection.update_one(
        {"_id": ObjectId(home_id), **device_query},
        {"$pull": {f"devices.$[device].setpoints": {"_id": found_setpoint['_id']}}},
        array_filters=[{"device._id": ObjectId(device_id)}]
    )
    if update_result.modified_count == 0:
        return ResponseModel({}, 500, "Failed to delete setpoint")

    return ResponseModel({}, 200, "Setpoint deleted successfully")

async def get_device_from_home_for_setpoint(home_id:str, device_id: str) -> Device:

    if ObjectId.is_valid(device_id):
        which_find = {"devices._id": ObjectId(device_id)}
        which_select = {"devices._id": 1, "devices.setpoints": 1}
    else:
        which_find = {"devices.macAddress": device_id}
        which_select = {"devices.macAddress": 1, "devices.setpoints": 1}

    query = {
        "$and": [
            {"_id": ObjectId(home_id)},
            which_find
        ]
    }

    home = await hemsc_collection.find_one(query, projection={"devices.$": 1})

    if home is None or 'devices' not in home or not home['devices']:
        print("No document found")
        return ResponseModel(data=[{}], code=400, message=f"Device with id {device_id} not found")

    device = home['devices'][0]
    device['_id'] = str(device['_id'])

    if 'setpoints' in device and isinstance(device['setpoints'], list):
        for setpoint in device['setpoints']:
            if '_id' in setpoint:
                setpoint['_id'] = str(setpoint['_id'])

    return device

async def update_setpoint_schemass(home_id: str, device_id: str, setpoint_index: int, setpoint: Setpoint):

    if ObjectId.is_valid(device_id):
        device_query = {"devices._id": ObjectId(device_id)}
    else:
        device_query = {"devices.macAddress": device_id}

    # Retrieve the home
    home = await hemsc_collection.find_one({"_id": ObjectId(home_id)})
    if home is None or not home:
        print("No document found")
        return ResponseModel({}, 400, "Homeis: {home_id} not found")

    # Find the correct device and setpoint
    found_device = None
    found_setpoint = None

    for device in home['devices']:
        if str(device['_id']) == device_id or device.get('macAddress') == device_id:
            found_device = device
            if setpoint_index < len(found_device['setpoints']):
                found_setpoint = found_device['setpoints'][setpoint_index]
            break

    if not found_device:
        print("not found")
        return ResponseModel({}, 400, "Deviceid: {device_id} not found")
    if not found_setpoint:
        return ResponseModel({}, 400, "Setpoint not found")

    # Update setpoint data
    found_setpoint['name'] = setpoint.name
    found_setpoint['coolingSetpoint'] = setpoint.coolingSetpoint
    found_setpoint['heatingSetpoint'] = setpoint.heatingSetpoint
    found_setpoint['fanSpeed'] = setpoint.fanSpeed
    found_setpoint['changedByServer'] = setpoint.changedByServer
    found_setpoint['dates']['dateUpdated'] = datetime.now(timezone.utc)

    if "dateCreated" in found_setpoint:
        found_setpoint.pop("dateCreated")
    # Update dateUpdated in device
    found_device['dateUpdated'] = datetime.now(timezone.utc)

    # Update the setpoint in the database
    update_result = await hemsc_collection.update_one(
        {
            "_id": ObjectId(home_id),
            **device_query
        },
        {
            "$set": {
                f"devices.$.setpoints.{setpoint_index}": found_setpoint,
                "devices.$.dateUpdated": found_device['dateUpdated']
            }
        }
    )
    if update_result.modified_count == 0:
        return ResponseModel([],400, "Failed to update setpoint")

    # return {"data": [{}], "code": 200, "message": "Setpoint updated successfully"}

async def update_preference_data(home_id: str, preference_data: PreferenceUpdate):
    preference_data.dateUpdated = datetime.now(timezone.utc)
    result = await hemsc_collection.update_one(
        {"_id": ObjectId(home_id)},
        {"$set": {"preference": preference_data.dict()}}
    )
    if result.matched_count == 0:
        return ResponseModel([],400, "Failed to update setpoint")