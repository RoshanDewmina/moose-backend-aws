from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.responses import JSONResponse
from database.database import *
from models.events import *
from service.temperature import *
from auth.jwt_bearer import RoleChecker

router = APIRouter()

@router.get("/", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
async def get_temperatures(start_date: Optional[str] = None, end_date: Optional[str] = None):
    try:
        document = await get_all_temperatures_service(start_date, end_date)
        if document:
            return ResponseModel(document,200, "All requested temperatures data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for temperatures is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=TemperatureDay, dependencies=[Depends(RoleChecker(allowed_roles=["SUPEROPERATOR"]))])
async def create_temperature(temp_item: TempItem):
    try:
        result = await create_temperatures_service(temp_item)
        return {"message": "temperature save successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
