from fastapi import APIRouter, HTTPException, Body, Depends
from utils.encoders import bson_encoder
from database.database import *
from models.users import *
from service.admin import *
from auth.jwt_bearer import RoleChecker

router = APIRouter()

# region information from userModel
@router.get("/")
async def get_all_user_list():
    try:
        document = await get_all_user_service()
        if document:
            return ResponseModel(document, 200, "All requested user log data retrieved successfully")
        else:
            return ResponseModel({}, 400, "Data for user log is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{user_id}")
async def get_user_by_Id(user_id:str):
    try:
        document = await get_user_by_id_service(user_id)
        if document:
            return ResponseModel(document, 200, "user data retrieved successfully")
        else:
            return ResponseModel({}, 400, f"Data for userId: {user_id} is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", dependencies=[Depends(RoleChecker(allowed_roles=["SUPEROPERATOR"]))])
async def user_update(user_id:str, user: UserModelUpdate = Body(...)):
    user_exists = await admin_collection.find_one({"userID":  user_id})
    if user_exists:
        user_dict = user.dict(by_alias=True)
        result = await update_user(user_id, user_dict)
        if result.get("code") == 200:
            updated_user = await admin_collection.find_one({"userID":  user_id})
            updated_user = bson_encoder(updated_user)
            return {"data": [updated_user], "code": 200, "message": "Update successful"}
        else:
            return result
    else:
        raise HTTPException(status_code=404, detail=f"User id {user_id} not found")

