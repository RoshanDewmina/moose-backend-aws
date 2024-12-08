from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.responses import JSONResponse
from pymongo.collection import Collection
import logging
from database.database import *
from models.homes import *
from service.homes import *
from bson import ObjectId
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

router = APIRouter()

@router.get("/", response_description="All HEMS information will be retrieved")
async def get_all_hemsc_route():
    try:
        logging.info("Retrieving all Hemsc data")
        hemsc_list = await get_all_hemsc()
        if hemsc_list:
            return ResponseModel(hemsc_list,200, "All requested HEMS data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for HEMS is not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{api_Key}", response_description="HEMS information will be retrieved by api-key")
async def get_hemsc_by_api(api_Key: str):    
    try:        
        hemsc = await get_hemsc_byId(api_Key)
        if hemsc:
            return ResponseModel(hemsc,200, "HEMS data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for HEMS with  apiKey: {api_Key} is not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{hemsc_Id}/", response_description="HEMS information will be retrieved by hemscID")
async def get_hemsc_by_hemscId(hemsc_Id: str):    
    try:        
        hemsc = await get_hemsc_hemscId(hemsc_Id)
        if hemsc:
            return ResponseModel(hemsc,200, "HEMS data retrieved successfully")
        else:
            return ResponseModel({},400, f"Data for HEMS with ID: {hemsc_Id} is not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_Id}")
async def get_user_by_Id(user_Id:str):    
    try:
        document = await get_hemsc_from_user_id(user_Id)
        if document:
            return ResponseModel(document, 200, "user data retrieved successfully")
        else:
            return ResponseModel({}, 400, f"Data for userId: {user_Id} is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

#region create
@router.post("/",response_model= dict, response_model_exclude_unset=True)
async def post_hemsc(hemsc: Hemsc ):
    try:
        new_hemsc_id = await create_hemsc(hemsc)
        hemsc = await get_hemsc_hemscId(new_hemsc_id)
        if hemsc:
            return ResponseModel(hemsc,200, "HEMSC was successfully created")
        else:
            return ResponseModel({},400, f"Data for home/hemscId: {hemscID} is not found")
        # return JSONResponse(content={"id": new_hemsc_id, "message": "Hemsc data created successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#endregion

#region update
@router.put("/{home_Id}")
async def update_hemsc(home_Id: str, hemsc: HemscUpdate):
    try:
        result = await update_hemsc_data(home_Id, hemsc)
        if result["code"] != 200:
            return ResponseModel(data=result["data"], code=result["code"], message=result["message"])        
        document = await get_hemsc_hemscId(home_Id)
        if document:
            return ResponseModel(document, 200,"HEMSC was successfully updated.")
        else:
            return ResponseModel({},400, f"Data for this HEMS is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

#endregion

#region Delete
@router.delete("/")
async def delete_hemsc(home_Id: str):
    try:
        hemsc_count = await delete_hemsc_data(home_Id)
        if hemsc_count == 0:
            raise HTTPException(status_code=200, detail="Hemsc not found")
        return {"message": "Hemsc deleted successfully", "deleted_count": hemsc_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#endregion

