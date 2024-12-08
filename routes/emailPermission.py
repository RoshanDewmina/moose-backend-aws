from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse
from database.database import *
from models.emailPermission import *
from service.emailPermission import *

router = APIRouter()

@router.get("/")
async def get_email_permission_list():
    try:
        document = await get_all_emailpermissions_service()
        if document:
            return ResponseModel(document, 200, "All requested email data retrieved successfully")
        else:
            return ResponseModel({}, 400, "Data for email is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{email}")
async def get_email_permission_by_email(email: str):
    try:
        document = await get_emailpermission_service(email)
        if document:
            document = convert_objectid(document)
            return ResponseModel(document, 200, "All requested email data retrieved successfully")
        else:
            return ResponseModel({}, 400, "Data for email is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
 

@router.post("/",response_model= dict, response_model_exclude_unset=True)
async def create_email_have_permission(email_permission: EmailPermission):
    try:
        await create_email_permission_service(email_permission)
        return {"message": "email save successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{permissionId}")
async def delete_email_permission(permissionId: str):
    try:
        result = await delete_email_permission_service(permissionId)
        if result == 0:
            raise HTTPException(status_code=404, detail="Email not found")
        return {"message": "Email deleted successfully", "deleted_count": result}    
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{permissionId}")
async def update_setpoint(permissionId: str, email_permission: EmailPermission):
    try:
        result = await update_email_permission_service(permissionId,email_permission)
        if result["code"] != 200:
            return ResponseModel(data=result["data"], code=result["code"], message=result["message"])
        document =await get_email_permission_ById_service(permissionId)
        if document:
            document = convert_objectid(document)
            return ResponseModel(document, 200,"HEMSC was successfully updated.")
        else:
            return ResponseModel({},400, f"Data for this HEMS is not found")            
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
