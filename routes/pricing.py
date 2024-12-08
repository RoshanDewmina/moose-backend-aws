from fastapi import APIRouter, HTTPException, Body
from models.pricing import *
from service.pricing import *
from typing import Dict, Union, Optional
import logging

router = APIRouter()

@router.post("/config")
async def register_pricing(home_Id: str, 
                           payload: Union[FlatRatePricing, TimeOfUsePricing, TieredPricing]):
    try:
        schema_name = payload.schema_name
        inserted_id = await register_pricing_schema(home_Id, payload)
        if inserted_id:
            pricing_schema = await get_pricing_schema(home_Id, schema_name)
            return ResponseModel(pricing_schema, 200, "Pricing schema was successfully created")
        else:
            return ResponseModel({}, 400, f"Data for home/hemscId: {inserted_id} is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{schema_name}")
async def get_pricing(home_Id: str, schema_name: str):
    try:
        pricing_schema = await get_pricing_schema(home_Id, schema_name)
        if pricing_schema:
            return ResponseModel(pricing_schema, 200, "Pricing schema is retrieve successfully created")
        else:
            return ResponseModel({}, 400, f"Data for the pricing model: {schema_name} is not found")
    except ValueError as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/update")
async def update_pricing(home_Id: str,
                         payload: Union[FlatRatePricing, TimeOfUsePricing, TieredPricing]):
    try:
        schema_name = payload.schema_name
        result = await update_pricing_schema(home_Id, schema_name, payload)
        if result != {}:
            return ResponseModel(result, 200, "Pricing schema is retrieve successfully created")
        else:
            return ResponseModel({}, 400, f"Data for the pricing model: {schema_name} is not found")
    except ValueError as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/devices/{device_Id}/earning/{schema_name}")
async def calculate_pricing_endpoint(
    home_Id: str, 
    device_Id: str,
    schema_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    try:
        # Calculate the cost based on the pricing model
        total_cost = await calculate_pricing(home_Id, device_Id, schema_name, start_date, end_date)

        return {
            "deviceID": device_Id,
            "schema_name": schema_name,
            "total_cost": total_cost,
        }

    except ValueError as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{schema_name}")
async def delete_pricing_schema(home_Id:str, schema_name: str):
    logging.info("Retrieving all Hemsc data")
    result = await delete_pricing_data(home_Id, schema_name)
    if "code" in result and "message" in result:
            return ResponseModel(result["data"], result["code"], result["message"])
    return {"message": f"Price schema fo {schema_name} deleted successfully"}