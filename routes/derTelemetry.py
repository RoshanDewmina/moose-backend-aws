from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from database.database import *
from models.derTelemetry import *
from service.derTelemetry import *
from service.homes import *

router = APIRouter()

@router.get("/device/{device_Id}/telemetry")
async def get_telemetry(home_Id:str, device_Id: str, startDate: Optional[str] = None, endDate: Optional[str] = None):
    try:
        derTelemetry = await get_all_derTelemetry(home_Id, device_Id, startDate, endDate)
        if derTelemetry:
            return ResponseModel(derTelemetry, 200, "All requested telemetry retrieved successfully")
        else:
            return ResponseModel({}, 400, f"Data for Device Energy is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/device/{device_Id}/telemetry")
async def create_telemetry_by_device(home_Id: str, device_Id: str, telemetry: DERTelemetry):
    try:
        await create_derTelemetry_service(device_Id, telemetry)
        return {"message": "derTelemetry save successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/device/{device_Id}/scheduler/start")
async def manage_scheduler(home_Id:str, device_Id: str, payload: telemetryScheduler):
    result = await start_scheduler(home_Id, device_Id, payload.site_id, payload.asset_id)
    return result
    
@router.post("/device/{device_Id}/scheduler/stop")
async def manage_scheduler(home_Id:str, device_Id: str, payload: telemetryScheduler):
    result = await stop_scheduler(home_Id, device_Id, payload.site_id, payload.asset_id)
    return result

@router.get("/device/{device_Id}/telemetry/average")
async def aggregated_average_der_Telemetry(home_Id: str, device_Id: str, type: Optional[str] = None):
    try:
        if not type:
            return {"code": 400, "message": "aggregationType query parameter is required"}
        derTelemetry = await get_aggregated_ave_derTelemetry(home_Id, device_Id, type)
        if derTelemetry:
            return {
                "data": derTelemetry,
                "code": 200,
                "message": "All requested telemetry retrieved successfully"
            }
        else:
            return {
                "data": {},
                "code": 400,
                "message": "Data for Device Energy is not found"
            }
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/device/{device_Id}/telemetry/aggregate")
async def aggregated_der_Telemetry(home_Id: str, device_Id: str, type: Optional[str] = None):
    try:
        if not type:
            return {"code": 400, "message": "aggregationType query parameter is required"}
        derTelemetry = await get_aggregated_sum_derTelemetry(home_Id, device_Id, type)
        if derTelemetry:
            return {
                "data": derTelemetry,
                "code": 200,
                "message": "All requested telemetry retrieved successfully"
            }
        else:
            return {
                "data": {},
                "code": 400,
                "message": "Data for Device Energy is not found"
            }
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))