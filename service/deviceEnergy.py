from models.deviceEnergy import *
from typing import Optional, List, Dict
from database.database import *
from datetime import datetime
from dateutil import parser
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from service.homes import *
import random
import asyncio

async def get_all_device_energy(homeId: str, deviceID: str, startDate: Optional[str] = None, endDate: Optional[str] = None):
    last_record = await deviceEnergyHour_collection.find_one(
        {"deviceID": deviceID},
        sort=[("dateCreated", pymongo.DESCENDING)]
    )
    if not last_record:
        return {"data": [], "code": 400, "message": "No records found for this device"}

    if endDate is None:
        ed = datetime.now(timezone.utc)
    else:
        ed = (parser.parse(endDate))

    if startDate is None:
        sd = ed.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        sd = (parser.parse(startDate))

    device = await get_device_from_home(homeId, deviceID)
    if not device:
        return {"data": [], "code": 400, "message": "Device not found"}

    cursor = deviceEnergyHour_collection.find({
        "deviceID": deviceID,
        "dateCreated": {
            "$gte": sd,
            "$lte": ed
        }
    })

    documents = await cursor.to_list(length=None)
    return {"data": documents, "code": 200, "message": "Data retrieved successfully"}

async def process_device_energy(cursor):
    device_energy = []
    # h = await cursor.to_list(length=None)
    try:
        for energy_hour in cursor:
            for i, energy in enumerate(energy_hour.get('energy', [])):
                if isinstance(energy, dict) and 'valid' in energy and energy['valid']:

                    timestamp = energy_hour['dateCreated'] + timedelta(minutes=i)
                    device_energy.append(DeviceEnergy(
                        Timestamp =timestamp,
                        Energy =energy['energy'],
                    ))
        return device_energy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_time_and_index():
    now = datetime.now(timezone.utc)
    hour = now.replace(minute=0, second=0, microsecond=0)
    min = now.replace(second=0, microsecond=0)
    index = int((min - hour).total_seconds() // 60)
    return hour, index

async def create_or_update_energy_hour(hour, device_Id, energy_item, index):
    try:
        # Check if energy exists for the device at the current hour
        count = await deviceEnergyHour_collection.count_documents({
            "dateCreated": hour,
            "deviceID": device_Id
        })
        energy_model = energy_item.dict()

        if count == 0:
            energy_hour = DeviceEnergyHour(
                dateCreated=hour,
                deviceID=device_Id,
                energy=[None] * 60
            )
            # energy_hour[index] = energy_model
            energy_hour.energy[index] = energy_model
            await deviceEnergyHour_collection.insert_one(energy_hour.dict())
        else:
            # If documents found, update the existing energy hour document
            energy_hour = await deviceEnergyHour_collection.find_one({
                "dateCreated": hour,
                "deviceID": device_Id
            })
            energy_hour['energy'][index] = energy_model
            result = await deviceEnergyHour_collection.update_one(
                {
                    "dateCreated": hour,
                    "deviceID": device_Id
                },
                {
                    "$set": {f"energy.{index}": energy_model}
                }
            )
            if result.matched_count == 0:
                raise ValueError(f"home/hemscId {device_Id} not found")
            return energy_model
            # return {"message": "PhaseAVoltage hour updated", "matched_count": result.matched_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_device_energy_data(home_id:str, device_id: str, interval: int):
    try:
        device = await get_device_from_home(home_id, device_id)
        if not device:
            return {"data": [], "code": 400, "message": "Device not found"}
        from_date, index = calculate_time_and_index()
        from_date = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        result = await deviceEnergyHour_collection.find_one(
            {
                "deviceID": device_id,
                "dateCreated": {"$gte": from_date}
            },
            sort=[("dateCreated", pymongo.DESCENDING)]
        )
        if result and "energy" in result:
            energy_data = result["energy"]
            # Calculate the average of valid energy readings for the last 5 minutes
            valid_energy_values = [ entry["energy"] if isinstance(entry, dict) and entry.get("valid") else None
                                   for entry in energy_data[index-interval:index]]
            filtered_values = [float(val) for val in valid_energy_values if val is not None]
            average_energy = sum(filtered_values) / len(filtered_values) if filtered_values else 0
            return average_energy
        return 0
    except Exception as e:
        logging.error(f"Error while fetching device energy data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve device energy data.")