from models.derTelemetry import *
from models.deviceEnergy import *
from typing import Optional, List, Dict
from database.database import *
from datetime import datetime
import dateutil.parser
import httpx
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from decouple import config
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi.encoders import jsonable_encoder
from service.homes import *
from service.deviceEnergy import create_or_update_energy_hour

SPONGE_TOKEN = config('SPONGE_TOKEN')
# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler = AsyncIOScheduler()

async def get_all_derTelemetry(homeId:str, deviceID: str, startDate: Optional[str] = None, endDate: Optional[str] = None):

        last_record = await deviceTelemetryHour_collection.find_one(
            {"deviceID": deviceID},
            sort=[("dateCreated", pymongo.DESCENDING)]
        )
        if not last_record:
            return {}
            # raise ValueError("No records found for this device")
            # raise HTTPException(detail="No records found for this device")

        if endDate is None:
           ed = datetime.now(timezone.utc) + timedelta(days=1)
        else:
           ed = datetime.strptime(endDate, "%Y-%m-%d")

        if startDate is None:
           sd = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
           sd = datetime.strptime(startDate, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)
        cursor = deviceTelemetryHour_collection.find({
              "deviceID": deviceID,
              "dateCreated": {
              "$gte": sd,
              "$lte": ed
            }
        })
        derTelemetry = []
        derTelemetry_hours = await cursor.to_list(length=None)
        for telemetry in derTelemetry_hours:
            derTelemetry.append({"dateCreated": telemetry['dateCreated'],
                                "Telemetry": telemetry['telemetry']})
        return derTelemetry

async def get_aggregated_ave_derTelemetry(homeId: str, deviceID: str, aggregationType: str):
    try:
        telemetry_field = "telemetry.unitACWhr"
        now = datetime.now(timezone.utc)

        # Determine start date and grouping logic based on aggregation type
        if aggregationType == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            group_by = {
                "year": {"$year": "$dateCreated"},
                "month": {"$month": "$dateCreated"},
                "day": {"$dayOfMonth": "$dateCreated"},
                "hour": {"$hour": "$dateCreated"}
            }
            total_periods = 24  # Total hours in a day
            period_format = "%H"  # Hourly format
        elif aggregationType == "weekly":
            start_date = now - timedelta(days=now.weekday())  # Start from last Monday
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            group_by = {
                "year": {"$year": "$dateCreated"},
                "month": {"$month": "$dateCreated"},
                "day": {"$dayOfMonth": "$dateCreated"}
            }
            total_periods = 7  # Days in a week
            period_format = "%Y-%m-%d"  # Date format
        elif aggregationType == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            group_by = {
                "year": {"$year": "$dateCreated"},
                "month": {"$month": "$dateCreated"},
                "day": {"$dayOfMonth": "$dateCreated"}
            }
            total_periods = (now - start_date).days + 1  # Days in the current month
            period_format = "%Y-%m-%d"  # Date format
        elif aggregationType == "yearly":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            group_by = {
                "year": {"$year": "$dateCreated"},
                "month": {"$month": "$dateCreated"},
                "day": {"$dayOfMonth": "$dateCreated"}
            }
            total_periods = (now - start_date).days + 1  # Days in the current year until now
            period_format = "%Y-%m-%d"  # Date format
        else:
            return {"code": 400, "message": "Invalid aggregation type"}

        pipeline = [
            {
                "$match": {
                    "deviceID": deviceID,
                    "dateCreated": {"$gte": start_date, "$lt": now}
                }
            },
            {
                "$unwind": "$telemetry"
            },
            {
                "$match": {
                    "telemetry.unitACWhr": {"$ne": None}
                }
            },
            {
                "$group": {
                    "_id": group_by,
                    "averageUnitACWhr": {"$avg": "$telemetry.unitACWhr"}
                }
            }
        ]

        # Execute the aggregation
        cursor = deviceTelemetryHour_collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        # Prepare the expected data slots
        period_data = {}
        current = start_date

        for _ in range(total_periods):
            period_key = current.strftime(period_format)
            period_data[period_key] = 0  # Default to zero
            if aggregationType == "daily":
                current += timedelta(hours=1)
            else:
                current += timedelta(days=1)

        # Fill in the actual results
        for result in results:
            if aggregationType == "daily":
                period_key = f"{result['_id']['hour']:02d}"
            else:
                period_key = f"{result['_id']['year']}-{result['_id']['month']:02d}-{result['_id']['day']:02d}"

            if period_key in period_data:
                period_data[period_key] = result["averageUnitACWhr"]

        # Return the response
        return {
            "from": start_date.isoformat(),
            "to": now.isoformat(),
            "averageUnitACWhr": list(period_data.values())
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"code": 500, "message": "Internal Server Error"}

async def get_aggregated_sum_derTelemetry(homeId: str, deviceID: str, aggregationType: str): 
    try:
        telemetry_field = "telemetry.unitACWhr"  # Ensure the correct field path
        now = datetime.now(timezone.utc)

        # Determine start date and grouping logic based on aggregation type
        if aggregationType == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            group_by = {
                "year": {"$year": "$dateCreated"},
                "month": {"$month": "$dateCreated"},
                "day": {"$dayOfMonth": "$dateCreated"},
                "hour": {"$hour": "$dateCreated"}
            }
            total_periods = 24  # Total hours in a day
            period_format = "%H"  # Hourly format
        elif aggregationType == "weekly":
            start_date = now - timedelta(days=now.weekday())  # Start from last Monday
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            group_by = {
                "year": {"$year": "$dateCreated"},
                "month": {"$month": "$dateCreated"},
                "day": {"$dayOfMonth": "$dateCreated"}
            }
            total_periods = 7  # Days in a week
            period_format = "%Y-%m-%d"  # Date format
        elif aggregationType == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            group_by = {
                "year": {"$year": "$dateCreated"},
                "month": {"$month": "$dateCreated"},
                "day": {"$dayOfMonth": "$dateCreated"}
            }
            total_periods = (now - start_date).days + 1  # Days in the current month
            period_format = "%Y-%m-%d"  # Date format
        elif aggregationType == "yearly":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            group_by = {
                "year": {"$year": "$dateCreated"},
                "month": {"$month": "$dateCreated"},
                "day": {"$dayOfMonth": "$dateCreated"}
            }
            total_periods = (now - start_date).days + 1  # Days in the current year until now
            period_format = "%Y-%m-%d"  # Date format
        else:
            return {"code": 400, "message": "Invalid aggregation type"}

        # Build the aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "deviceID": deviceID,  
                    "dateCreated": {"$gte": start_date, "$lt": now}
                }
            },
            {
                "$unwind": "$telemetry"
            },
            {
                "$match": {
                    "telemetry.unitACWhr": {"$ne": None}
                }
            },
            {
                "$group": {
                    "_id": group_by,
                    "sumUnitACWhr": {"$sum": "$telemetry.unitACWhr"}  # Change from avg to sum
                }
            }
        ]

        # Execute the aggregation
        cursor = deviceTelemetryHour_collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        # Prepare the expected data slots
        period_data = {}
        current = start_date

        for _ in range(total_periods):
            period_key = current.strftime(period_format)
            period_data[period_key] = 0  # Default to zero
            if aggregationType == "daily":
                current += timedelta(hours=1)
            else:
                current += timedelta(days=1)

        # Fill in the actual results
        for result in results:
            if aggregationType == "daily":
                period_key = f"{result['_id']['hour']:02d}"
            else:
                period_key = f"{result['_id']['year']}-{result['_id']['month']:02d}-{result['_id']['day']:02d}"

            if period_key in period_data:
                period_data[period_key] = result["sumUnitACWhr"]  # Change from average to sum

        # Return the response
        return {
            "from": start_date.isoformat(),
            "to": now.isoformat(),
            "sumUnitACWhr": list(period_data.values())  # Change key for the response
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"code": 500, "message": "Internal Server Error"}

async def create_derTelemetry_service(deviceID: str, telemetry: DERTelemetry):

    now = datetime.now(timezone.utc)
    hour = now.replace(minute=0, second=0, microsecond=0)
    min = now.replace(second=0, microsecond=0)
    index = int((min - hour).total_seconds() // 60)
    query = {"dateCreated": hour, "deviceID": deviceID}
    count = await deviceTelemetryHour_collection.count_documents(query)
    telemetry_model = telemetry.dict()

    if count == 0:
        telemetry_hour = DeviceTelemetryHour(
            dateCreated=hour,
            deviceID=deviceID,
            telemetry=[None] * 60
        )
        telemetry_hour.telemetry[index] = telemetry_model
        await deviceTelemetryHour_collection.insert_one(telemetry_hour.dict(by_alias=True))
    else:
        telemetry_hour = await deviceTelemetryHour_collection.find_one({
                "dateCreated": hour,
                "deviceID": deviceID
            })
        telemetry_hour['telemetry'][index] = telemetry_model
        result = await deviceTelemetryHour_collection.update_one(
            {
                "dateCreated": hour,
                "deviceID": deviceID
            },
            {
                "$set": {f"telemetry.{index}": telemetry_model}
            }
            )

def map_device_telemetry(device_data):
    """
    Converts the device telemetry data to the desired schema.
    """
    telemetry = {
        "phaseAVoltage": 0,
        "phaseBVoltage": 0,
        "phaseCVoltage": 0,
        "unitACWatts": 0,
        "unitACWhr": 0,
        "frequency": 0,
        "dcVoltage": 0,
        "dcWatts": 0,
        "soc": 0,
        "availableStorage": 0,
        "batteryVoltage": 0,
        "pvVoltage": 0,
        "status": {"0": "Normal operation"}
    }

    line_telemetry = device_data.get("line_telemetry", {})
    
    # Mapping phase voltages from grid_0, grid_1, grid_2
    for i in range(3):
        grid_key = f"grid_{i}"
        if grid_key in line_telemetry:
            telemetry[f"phase{chr(65+i)}Voltage"] = line_telemetry[grid_key].get("voltage", 0)

    # Calculating net power and energy
    total_grid_power = sum(line_telemetry[key].get("power", 0)
                            for key in line_telemetry
                            if line_telemetry[key].get("current_type") == "AC" and "grid" in key)
    total_load_power = sum(line_telemetry[key].get("power", 0)
                           for key in line_telemetry
                           if line_telemetry[key].get("current_type") == "AC" and "loads" in key)
    telemetry["unitACWatts"] = total_grid_power - total_load_power

    total_grid_energy = sum(line_telemetry[key].get("energy", 0)
                            for key in line_telemetry
                            if line_telemetry[key].get("current_type") == "AC" and "grid" in key)
    total_load_energy = sum(line_telemetry[key].get("energy", 0)
                            for key in line_telemetry
                            if line_telemetry[key].get("current_type") == "AC" and "loads" in key)
    telemetry["unitACWhr"] = total_grid_energy - total_load_energy

    dc_lines = [key for key in line_telemetry if line_telemetry[key].get("current_type") == "DC"]
    if dc_lines:
        total_dc_power = sum(line_telemetry[line].get("power", 0) for line in dc_lines)
        telemetry["dcWatts"] = total_dc_power
        telemetry["dcVoltage"] = line_telemetry[dc_lines[0]].get("voltage", 0)
        
        if "solar_0" in line_telemetry:
            telemetry["pvVoltage"] = line_telemetry["solar_0"].get("voltage", 0)
        if "battery_0" in line_telemetry:
            telemetry["batteryVoltage"] = line_telemetry["battery_0"].get("voltage", 0)
    telemetry["status"] = device_data.get("status", {})
    status_mapping = {
        "Normal operation": 1,
    }
    status_text = list(device_data.get("status", {}).values())[0]
    internal_status = status_mapping.get(status_text, 0) #TODO

    return telemetry

async def fetch_and_store_devices(site_id: str, asset_id: str, device_id: str):
    """
    Fetches device data from the API and stores it in MongoDB.
    """
    API_URL = f'https://proxy.sponge.to/{site_id}/api/v1/status?token={SPONGE_TOKEN}&device_id={asset_id}'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, timeout=10.0)
            response.raise_for_status()
            devices = response.json()

        if asset_id not in devices:
            logging.info(f"Device {device_id} not found in API response.")
            return

        device_data = devices[asset_id]
        now = dateutil.parser.parse(device_data.get("timestamp")) if device_data.get("timestamp") else datetime.now(timezone.utc)
        hour = now.replace(minute=0, second=0, microsecond=0)
        min_time = now.replace(second=0, microsecond=0)
        index = int((min_time - hour).total_seconds() // 60)

        telemetry = map_device_telemetry(device_data)

        query = {"dateCreated": hour, "deviceID": device_id}
        count = await deviceTelemetryHour_collection.count_documents(query)

        if count == 0:
            telemetry_hour = {
                "dateCreated": hour,
                "deviceID": device_id,
                "assetID": asset_id,
                "telemetry": [None] * 60
            }
            telemetry_hour["telemetry"][index] = telemetry
            await deviceTelemetryHour_collection.insert_one(telemetry_hour)
            logging.info(f"Inserted new telemetry for device {device_id} at hour {hour}")
        else:
            await deviceTelemetryHour_collection.update_one(
                query,
                {"$set": {f"telemetry.{index}": telemetry}}
            )
            logging.info(f"Updated telemetry for device {device_id} at minute {index} of hour {hour}")

        energy_item = Energy(**{"energy": telemetry["unitACWhr"], "valid": True})
        await create_or_update_energy_hour(hour, device_id, energy_item, index)

    except httpx.RequestError as e:
        logging.info(f"Error fetching device data for device {device_id}: {e}")
        pass

async def start_scheduler(home_Id: str, device_id: str, site_id: str, asset_id: str, interval: int = 5):
    job_id = f"{site_id}_{asset_id}_{device_id}"

    # Check if the job already exists
    if scheduler.get_job(job_id):
        raise HTTPException(status_code=400, detail="Job already scheduled")
    else:
        scheduler.add_job(fetch_and_store_devices, 'interval', minutes=interval, id=job_id, args=[site_id, asset_id, device_id])
        scheduler.start()
        return {"message": f"Job {job_id} started"}

async def stop_scheduler(home_Id: str, device_id: str, site_id: str, asset_id: str):
    job_id = f"{site_id}_{asset_id}_{device_id}"

    # Stop the job if it exists
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.remove()
    return {"message": f"Job {job_id} stopped"}

# Shutdown scheduler gracefully on application shutdown
def shutdown_scheduler():
    scheduler.shutdown()