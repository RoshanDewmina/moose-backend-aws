from models.pricing import *
from fastapi import HTTPException
from typing import Dict, Any, List
from dateutil import parser
from datetime import datetime
from database.database import *
from pymongo.errors import DuplicateKeyError

async def register_pricing_schema(home_Id: str, pricing_schema: Any) -> None:
    pricing_schemas_db = await pricing_collection.find_one({"hemscID": home_Id})
    if pricing_schemas_db:
        raise ValueError("Pricing model for this HEMSC already exists")
    else:
        pricing_dict = pricing_schema.dict(by_alias=True)
        print(pricing_dict)
        pricing_dict["_id"] = ObjectId()
        pricing_dict["hemscID"] = home_Id
        try:
            result = await pricing_collection.insert_one(pricing_dict)
            return str(result.inserted_id)
        except DuplicateKeyError:
            raise ValueError("DuplicateKeyError: Pricing model already exists")


async def get_pricing_schema(home_Id: str, model_name: str) -> Any:
    pricing_schemas_db = await pricing_collection.find_one({"hemscID": home_Id})
    if model_name not in pricing_schemas_db:
        raise ValueError(f"Pricing model '{model_name}' not found.")
    return pricing_schemas_db[model_name]


async def update_pricing_schema(home_Id: str, model_name: str, pricing_schema: Any) -> None:
    pricing_schemas_db = await pricing_collection.find_one({"hemscID": home_Id})
    if model_name not in pricing_schemas_db:
        raise ValueError(f"Pricing model '{model_name}' not found.")
    pricing_data = pricing_schema.dict(exclude_unset=True)
    result = await pricing_collection.update_one(
            {"hemscID": home_Id},
            {"$set": pricing_data}
    )
    if result.matched_count == 0 or result.modified_count == 0:
        return {}
    return pricing_data

async def calculate_pricing(home_Id: str, device_Id: str, model_name: str, start_date: str = None, end_date: str = None) -> float:
    # Convert date strings to datetime objects
    sd = (datetime.now(timezone.utc) - timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0) if start_date is None else (parser.parse(start_date))
    ed = datetime.now(timezone.utc) if end_date is None else (parser.parse(end_date))

    # Fetch documents within the specified date range
    cursor = deviceEnergyHour_collection.find({
        "deviceID": device_Id,
        "dateCreated": {
            "$gte": sd,
            "$lte": ed
        }
    })
    documents = await cursor.to_list(length=None)
    if not documents:
        raise HTTPException(status_code=404, detail="No data found for the given date range.")

    pricing_schemas_db = await pricing_collection.find_one({"hemscID": home_Id})
    if not pricing_schemas_db:
        raise ValueError(f"Pricing model '{model_name}' not found for home ID {home_Id}.")

    pricing_schema = pricing_schemas_db.get('schema_name')
    if pricing_schema != model_name:
        raise ValueError(f"Pricing model '{model_name}' is not defined for this home.")

    # Initialize total energy and total cost
    total_energy = 0.0
    total_cost = 0.0

    if model_name == "flat_rate":
        # Sum up all valid energy usage and apply the flat rate
        for doc in documents:
            if "energy" in doc and isinstance(doc["energy"], list):
                for energy_entry in doc["energy"]:
                    
                    if isinstance(energy_entry, dict) and energy_entry.get("valid", True):
                        total_energy += energy_entry.get("energy", 0)
        total_cost = (total_energy/1000.0) * pricing_schemas_db['flat_rate']
        return {'total_cost':total_cost, 'total_energy':total_energy}

    elif model_name == "time_of_use":
        # Calculate cost based on time of use rates
        for doc in documents:
            timestamp = doc["dateCreated"]
            if "energy" in doc and isinstance(doc["energy"], list):
                for energy_entry in doc["energy"]:
                    if isinstance(energy_entry, dict) and energy_entry.get("valid", False):
                        hour = timestamp.hour
                        energy = energy_entry["energy"]
                        total_energy += energy_entry.get("energy", 0)
                        if hour in pricing_schemas_db['peak_hours']:
                            total_cost += (energy/1000.0) * pricing_schemas_db['peak_rate']
                        else:
                            total_cost += (energy/1000.0) * pricing_schemas_db['off_peak_rate']
        return {'total_cost':total_cost, 'total_energy':total_energy}

    elif model_name == "tiered":
        # Sum up all valid energy usage
        for doc in documents:
            if "energy" in doc and isinstance(doc["energy"], list):
                for energy_entry in doc["energy"]:
                    if isinstance(energy_entry, dict) and energy_entry.get("valid", False):
                        total_energy += energy_entry.get("energy", 0)

        # Calculate cost based on tiered pricing
        remaining_usage = total_energy
        for tier in pricing_schemas_db['tiers']:
            if remaining_usage <= tier['limit']:
                total_cost += (remaining_usage/1000.0) * tier['rate']
                break
            else:
                total_cost += tier['limit'] * tier['rate']
                remaining_usage -= tier['limit']
        return {'total_cost':total_cost, 'total_energy':total_energy}

    else:
        raise ValueError(f"Pricing model '{model_name}' is not supported.")

async def delete_pricing_data(home_Id:str, schema_name:str):
    pricing = await pricing_collection.find_one({"hemscID": home_Id})
    if not pricing:
        raise HTTPException(status_code=404, detail="Pricing model is not found")
    if pricing["schema_name"] == schema_name:
        result = await pricing_collection.delete_one({"hemscID": home_Id})
        if result.deleted_count == 0:
            logging.info("No home ID is found to delete the pricing schema")
            raise HTTPException(status_code=404, detail="No home ID is found to delete the pricing schema")
        return result.deleted_count
    else:
        raise HTTPException(status_code=404, detail="schema name is not found")