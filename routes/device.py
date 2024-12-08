from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import logging
from models.homes import *
from database.database import *
from service.homes import *
from models.derTelemetry import *
from models.deviceEnergy import *
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

router = APIRouter()

#get all records of home's devices
@router.get("/",response_description="All device information")
async def get_all_devices(home_Id:str):
    try:
        document = await get_devices(home_Id)
        if "code" in document and "message" in document:
            return ResponseModel(document["data"], document["code"], document["message"])

        if 'devices' in document and document['devices']:
            return ResponseModel(document['devices'],200, "All requested Device data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for Device is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_Id}",response_description="a device information")
async def get_device(home_Id:str, device_Id:str):
    try:
        device = await get_device_from_home_deviceEndpoint(home_Id, device_Id)
        if "code" in device and "message" in device:
            return ResponseModel(device["data"], device["code"], device["message"])
        if device:
            return ResponseModel(device,200, "Device data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for Device is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def post_device(home_Id: str, device: Device):
    try:

        new_device_id = await create_devices(home_Id,device)
        return ResponseModel(data=new_device_id, code=200, message="Device data created successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{device_Id}")
async def update_device(home_Id: str, device_Id: str, device_data: DeviceUpdated):
    try:
        result = await update_device_data(home_Id,device_data, device_Id)
        if "code" in result and "message" in result:
            return ResponseModel(result["data"], result["code"], result["message"])
        device = await get_device_from_home(home_Id, device_Id)
        if device:
            return ResponseModel(device,200, "Device data update successfully")
        else:
            return ResponseModel({},400, f"Data for Device is not found")
    except Exception as e:
        logger.error(f"Error updating device: {e}")
        raise HTTPException(status_code=500, detail="Failed to update device")

@router.delete("/{device_Id}")
async def delete_device(home_Id:str, device_Id: str):
    logging.info("Retrieving all Hemsc data")
    result = await delete_device_data(home_Id, device_Id)
    if "code" in result and "message" in result:
            return ResponseModel(result["data"], result["code"], result["message"])
    return {"message": "Device deleted successfully", "deviceId": device_Id}