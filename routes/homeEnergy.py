from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
import logging
from database.database import *
from service.homeEnergy import *
from service.homes import *
from models.homeEnergy import *

router = APIRouter()

@router.get("/")
async def get_home_energy(home_Id:str, startDate: Optional[str] = None, endDate: Optional[str] = None):
    try:
        document = await get_all_home_energy_service(home_Id, startDate, endDate)

        if document['data']:
            return ResponseModel(document['data'],200, "All requested home energy data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for home energy is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_energy_item(energy_item: Energy, home_Id: str):
    try:
       await create_home_energy_service(home_Id, energy_item)
       return {"message": "Energy item created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

