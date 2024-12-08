from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse
from database.database import *
from models.events import *
from service.event import *
from service.homes import *

router = APIRouter()

@router.get("/", response_description="All Event information will be retrieved")
async def get_event(home_Id: str):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")

        document = await get_event_service(home_Id)
        if document:
            return ResponseModel(document, 200, "All requested Event data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for Event is not found")
    except Exception as e:
        # logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current")
async def get_current_enet(home_Id: str):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")

        document = await get_last_event_service(home_Id)
        if "code" in document and "message" in document:
            return ResponseModel(document["data"], document["code"], document["message"])
        if document:
            return ResponseModel(document,200, "All requested Event data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for Event is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/", response_model= dict, response_model_exclude_unset=True)
async def create_events(home_Id: str,event: Event):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")

        await create_event_service(home_Id,event)
        document = await get_event_service(home_Id)
        if document:
            return ResponseModel(document, 200, "Event data created successfully")
        else:
            return ResponseModel({},400, f"Data can not saved")
        # return JSONResponse(content={"id": new_event_id, "message": "Event data created successfully"})
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.put("/{event_id}/cancel")
async def get_cancel_event(home_Id:str, event_Id: str):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")
        result = await cancel_event_service(home_Id, event_Id)
        if result["code"] != 200:
            return ResponseModel(data=result["data"], code=result["code"], message=result["message"])
        document = await get_event_byId(event_Id)
        if document:
            return ResponseModel(document, 200, "All requested Event data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for Event is not found")
    except HTTPException as e:
        logger.error(f"HTTP error: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error cancelling event: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/{event_id}/opt-out")
async def get_opt_out_event(home_Id:str, event_Id: str):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")
        result = await opt_out_event_service(home_Id, event_Id)
        if result["code"] != 200:
            return ResponseModel(data=result["data"], code=result["code"], message=result["message"])
        document = await get_event_byId(event_Id)
        if document:
            return ResponseModel(document,200, "All requested Event data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for Event is not found")
    except Exception as e:
        logger.error(f"Error cancelling event: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

