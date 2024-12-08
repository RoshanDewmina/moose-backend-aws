import motor.motor_asyncio, urllib.parse, pymongo
from bson import ObjectId
from datetime import timedelta, timezone, datetime
import os
from .database_parser import admin_parser, event_parser
from decouple import config
import logging
from pymongo.collection import Collection
import asyncio

from pymongo.errors import ServerSelectionTimeoutError

#region database
MONGO_DETAILS = config('MONGO_DETAILS')
db_user = config('MONGO_USER')
db_pass = urllib.parse.quote(config('MONGO_PASS'))
db_host = config('MONGO_HOST')

MONGO_DETAILS = MONGO_DETAILS.format(db_user, db_pass, db_host)
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.asset
#endregion

#region collections
# admin_collection = database.get_collection('admins')
admin_collection = database['admins']
hemsc_collection = database['hemsc']
deviceEnergyHour_collection = database['deviceEnergyHour']
homeEnergyHour_collection = database['homeEnergyHour']
deviceTelemetryHour_collection = database['DeviceTelemetryHour']
temperatureDay_collection = database['TemperatureDay']
energy_collection = database['energy']
EmailPermission_collection = database['EmailPermission']
userLog_collection = database['userLog']
event_collection = database['events']
pricing_collection = database['billing']
#endregion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    client.admin.command('ping')
    logger.info("Connected to MongoDB successfully")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

async def retrieve_events(skip:int, limit:int):
    events = event_collection.find({}).skip(skip).limit(limit)
    counts = await event_collection.count_documents({})
    events = await events.to_list(length=limit)
    return event_parser(events, counts)

# Dependency functions
def get_admin_collection() -> Collection:
    return admin_collection

async def check_connection():
    try:
        # Attempt to get a list of databases to confirm connection
        dbs = await client.list_database_names()
        logger.info(f"Connected to MongoDB. Databases: {dbs}")
    except ServerSelectionTimeoutError as e:
        logger.error(f"Server selection error: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

async def main():
    await check_connection()

if __name__ == "__main__":
    asyncio.run(main())

