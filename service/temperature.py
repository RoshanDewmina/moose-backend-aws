from models.events import *
from typing import Optional, List, Dict
from database.database import *
from datetime import datetime
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
import logging
from models.temperatures import *

async def get_all_temperatures_service(startDate: Optional[str] = None, endDate: Optional[str] = None):
    if endDate is None:
        ed = datetime.now(timezone.utc)
    else:
        ed = datetime.strptime(endDate, "%Y-%m-%d")

    if startDate is None:
        sd = (datetime.now(timezone.utc)-timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        sd = datetime.strptime(startDate, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)

    cursor = temperatureDay_collection.find({
        "dateCreated": {
            "$gte": sd,
            "$lte": ed
        }
    })
    temps = []
    if cursor != []:
       async for temp_day in cursor:
            try:
                temp_day_obj = TemperatureDay(**temp_day)
                for i, temp in enumerate(temp_day_obj.temperatures):
                    if temp and temp.valid:

                        timestamp = temp_day_obj.dateCreated + timedelta(minutes=i * 10)
                        temps.append(Temperature(timestamp=timestamp, temperature=temp.temperature))
            except Exception as inner_e:
                logger.error(f"Error processing document {temp_day}: {str(inner_e)}")
                continue
       logger.info(f"Found {len(temps)} temperatures")
       return temps
    else:
        return []

async def create_temperatures_service(temp_item: TempItem):
    now = datetime.now(timezone.utc)
    day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    min_time = now.replace(second=0, microsecond=0)
    index = int((min_time - day).total_seconds() // 600)
    existing_day = await temperatureDay_collection.find_one({"dateCreated": day})
    if not existing_day:
        temp_day = TemperatureDay(dateCreated=day , temperatures=[None] * 144)
        temp_day.temperatures[index] = temp_item
        result = await temperatureDay_collection.insert_one(temp_day.dict(exclude_unset=True))
        # result = await temperatureDay_collection.insert_one(temp_day.dict())
        temp_day.id = str(result.inserted_id)
    else:
        update_query = {
            "$set": {
                f"temperatures.{index}": temp_item.dict()
            }
        }
        await temperatureDay_collection.update_one({"dateCreated": day}, update_query)
        existing_day["temperatures"][index] = temp_item.dict()
        temp_day = TemperatureDay(**existing_day)
        temp_day._id = str(existing_day["_id"])

    return temp_day