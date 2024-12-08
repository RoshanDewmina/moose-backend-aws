from fastapi import APIRouter,HTTPException
from fastapi.encoders import jsonable_encoder
import logging
from models.homes import *
from database.database import *
from models.homeEnergy import *
from typing import Optional, List, Dict
from datetime import datetime
from dateutil import parser
from pymongo import DESCENDING

router = APIRouter()

async def get_all_home_energy_service(homeId:str, startDate: Optional[str] = None, endDate: Optional[str] = None):
    try:
        home_object_id = ObjectId(homeId)
    except Exception as e:
        return ErrorResponseModel(f"Invalid homeId: {e}", 400, "Invalid homeId")

    last_record = await homeEnergyHour_collection.find_one(
            {"homeID": home_object_id}
            ,
            sort=[("dateCreated", DESCENDING)]
    )
    if last_record is None:
        return ResponseModel([],200, f"No records found for the specified homeID:{homeId} ")

    if endDate is None:
        ed = last_record['dateCreated']
    else:
        ed = (parser.parse(endDate))

    if startDate is None:
        sd = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        sd = (parser.parse(startDate))

    cursor = homeEnergyHour_collection.find({
              "homeID": home_object_id,
              "dateCreated": {
              "$gte": sd,
              "$lte": ed
            }
        })

    home_energy = []
    home_energy_hours = await cursor.to_list(length=None)

    try:
        for energy_hour in home_energy_hours:
            for i, energy in enumerate(energy_hour['energy']):
                if isinstance(energy, dict) and 'valid' in energy and energy['valid']:

                    timestamp = energy_hour['dateCreated'] + timedelta(minutes=i)
                    home_energy.append(HomeEnergy(
                        Timestamp = timestamp,
                        Energy = energy['energy'],
                    ).dict())

        print(f"Retrieved home energy data: {home_energy}")
        # return home_energy
        return ResponseModel(home_energy, 200, "Data retrieved successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def create_home_energy_service(homeId:str, energy_item: Energy):
    now = datetime.now(timezone.utc)
    hour = now.replace(minute=0, second=0, microsecond=0)
    minute = now.replace(second=0, microsecond=0)
    index = (minute - hour).seconds // 60

    count = await homeEnergyHour_collection.count_documents({
        "dateCreated": hour,
        "homeID": homeId
    })
    if count == 0:
        energy_hour = {
            "dateCreated": hour,
            "homeID": homeId,
            "energy": [None] * 60
        }
        energy_hour["energy"][index] = energy_item.dict()
        try:
            await homeEnergyHour_collection.insert_one(energy_hour)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        try:
            await homeEnergyHour_collection.update_one(
                {"dateCreated": hour, "homeID": homeId},
                {"$set": {f"energy.{index}": energy_item.dict()}}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))