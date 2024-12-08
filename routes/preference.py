from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models.homes import *
from database.database import *
from service.homes import *

router = APIRouter()

@router.get("/")
async def get_all_preference(home_Id:str):
    try:
        document = await get_home(home_Id)
        if "code" in document and "message" in document:
            return ResponseModel(document["data"], document["code"], document["message"])
        if document.preference:
            return ResponseModel(document.preference,200, "All requested preference data retrieved successfully")
        else:
            return ResponseModel({}, 400, f"Data for preference is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/")
async def update_preference(home_Id: str, preference_data: PreferenceUpdate):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
            return ResponseModel(data={}, code=400, message=f"homeId: {home_Id} is not found")

        result = await update_preference_data(home_Id, preference_data,)
        document = await get_devices(home_Id)
        if 'preference' in document and document['preference']:
            return ResponseModel(document['preference'],200, "All requested preference data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for preference is not found")

    except Exception as e:
        logger.error(f"Error updating preference: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preference")  