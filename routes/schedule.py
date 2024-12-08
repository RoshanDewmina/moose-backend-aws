from fastapi import APIRouter, HTTPException
from models.homes import *
from database.database import *
from service.homes import *

router = APIRouter()

@router.get("/")
async def get_all_schedules(home_Id: str, device_Id: str):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")

        document = await get_device_from_home(home_Id,device_Id)
        if "code" in document and "message" in document:
            return ResponseModel(document["data"], document["code"], document["message"])
        if document:
            return ResponseModel(document['schedules'],200, "All requested schedules data retrieved successfully")
        else:
            ResponseModel({},400, f"Data for schedules is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{schedule_day}", response_model=Dict[str, List[Schedule]])
async def create_day_schedules(home_Id: str, device_Id: str, schedule_day: str, schedules: List[Schedule]):

    result = await create_day_schedules_service(home_Id, device_Id, schedule_day, schedules)

    # return {"message": "Schedule day updated successfully"}
    return {"schedules": schedules}

@router.put("/{schedule_day}")
async def update_day_schedules(home_Id: str, device_Id: str, schedule_day: str, schedules: List[Schedule]):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"homeId: {home_Id} is not found")

        result =await update_schedules_service(home_Id, device_Id, schedule_day, schedules)
        if "code" in result and "message" in result:
            return ResponseModel(result["data"], result["code"], result["message"])
        document = await get_device_from_home(home_Id,device_Id)
        if document:
            return ResponseModel(document['schedules'], 200,"All requested schedules data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for schedules is not found")
    except Exception as e:
        logger.error(f"Error updating device: {e}")
        raise HTTPException(status_code=500, detail="Failed to update device")

    