from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse
from database.database import *
from models.userLog import *
from service.userLog import *
from service.admin import *

router = APIRouter()

@router.get("/")
async def get_user_log_list():
    try:
        document = await get_all_user_log()
        if document:
            return ResponseModel(document, 200, "All requested user log data retrieved successfully")
        else:
            return ResponseModel({}, 400, "Data for user log is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/{user_email}")
# async def get_user_log_list_by_email(user_email: str):
#     try:
#         document = await get_userLog_by_email_service(user_email)
#         if document:
#             # document = convert_objectid(document)
#             return ResponseModel(document, 200, "All requested email data retrieved successfully")
#         else:
#             return ResponseModel({}, 400, "Data for email is not found")
#     except Exception as e:
#         logging.error(f"Error occurred: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


