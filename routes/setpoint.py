from fastapi import APIRouter, HTTPException
from models.homes import *
from database.database import *
from service.homes import *
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/")
async def get_all_setpoint(home_Id: str, device_Id: str):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")
        document = await get_device_from_home(home_Id,device_Id)
        if "code" in document and "message" in document:
            return ResponseModel(document["data"], document["code"], document["message"])
        if document['setpoints']:
            return ResponseModel(document['setpoints'],200, "All requested setpoints data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for setpoints is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        # raise HTTPException(status_code=500, detail= message)

@router.post("/", response_model=Setpoint)
async def create_setpoint(home_Id:str, device_Id: str, setpoint: Setpoint):

        setpoint, device_query, now = await create_setpoint_schemas(home_Id,device_Id,setpoint)

        setpoint_id = ObjectId()
        setpoint._id = str(setpoint_id)
        setpoint_dict = setpoint.dict()
        setpoint_dict["_id"] = str(setpoint_id)

        update_result = await hemsc_collection.update_one(
            {"$and": [{"_id": ObjectId(home_Id)}, device_query]},
            {"$push": {"devices.$.setpoints": setpoint_dict},
            "$set": {"devices.$.dates.dateUpdated": now}}
        )
        logger.info(f"Update result: {update_result.raw_result}")
        if update_result.matched_count == 0:
           raise HTTPException(status_code=500, detail="Failed to create setpoint")

        return setpoint

@router.delete("/{setpoint_index}")
async def delete_setpoint(home_Id: str, device_Id: str, setpoint_index: int):
    home = await get_hemsc_hemscId(home_Id)
    if home == {}:
        return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")
    update_result = await delete_setpoint_schemas(home_Id, device_Id, setpoint_index)
    # if update_result["code"] != 200:
    #     raise HTTPException(status_code=update_result["code"], detail=update_result["message"])

    # if update_result.modified_count == 0:
    #     raise HTTPException(status_code=500, detail="Failed to delete setpoint")
    return JSONResponse(status_code=update_result["code"], content=update_result)
    # return {"message": "Setpoint deleted successfully"}

@router.put("/{setpoint_index}")
async def update_setpoint(home_Id: str, device_Id: str, setpoint_index: int, setpoint: Setpoint):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")

        result = await update_setpoint_schemass(home_Id, device_Id, setpoint_index, setpoint)
        if "code" in result and "message" in result:
            return ResponseModel(result["data"], result["code"], result["message"])

        document = await get_device_from_home(home_Id,device_Id)
        if document['setpoints']:
            return ResponseModel(document['setpoints'],200, "a requested setpoint data was updated successfully")
        else:
            return ResponseModel({},400, f"Data for setpoints is not found")
    except Exception as e:
        logger.error(f"Error updating device: {e}")
        raise HTTPException(status_code=500, detail=str(e))

