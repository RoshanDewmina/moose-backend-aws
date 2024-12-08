from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import logging
from models.homes import *
from database.database import *
from service.deviceEnergy import *
from service.homes import *
from models.derTelemetry import *
from models.deviceEnergy import *
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def get_device_energy(home_Id:str, device_Id: str, startDate: Optional[str] = None, endDate: Optional[str] = None):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")
        result = await get_all_device_energy(home_Id, device_Id, startDate, endDate)
        if result["code"] != 200:
            return ResponseModel(data=result["data"], code=result["code"], message=result["message"])
        document = await process_device_energy(result["data"])
        if document:
            return ResponseModel(document, 200, "All requested Device Energy data retrieved successfully")
        else:
             return ResponseModel(data=[], code=400, message="Data for Device Energy is not found")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=None)
async def create_device_energy(home_Id:str, device_Id: str, energy_item: Energy):
    try:
        home = await get_hemsc_hemscId(home_Id)
        if home == {}:
           return ResponseModel(data={}, code=400, message=f"home/hemscId: {home_Id} is not found")
        device = await get_device_from_home(home_Id,device_Id)
        if not device:
           return ResponseModel(status_code=400, detail="deviceId: {device_Id} not found")
        hour, index = calculate_time_and_index()
        result = await create_or_update_energy_hour(hour, device_Id, energy_item, index)
        if result:
            return ResponseModel(result,200, "device energy hour updated successfully")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/device_energy")
async def websocket_device_energy(websocket: WebSocket, home_id: str, device_id: str, interval: int = 5):
    await websocket.accept()
    logging.info(f"WebSocket connection accepted for home: {home_id}, device: {device_id}")
    try:
        while True:
            # Get the latest device energy data for the last `interval` minutes
            energy_data = await get_device_energy_data(home_id, device_id, interval)
            # Send the data back through the WebSocket connection
            await websocket.send_json({"device_id": device_id, "energy": energy_data})
            # Sleep for the specified interval before checking again
            await asyncio.sleep(interval * 60)  # Convert minutes to seconds
    except WebSocketDisconnect:
        logging.info(f"WebSocket disconnected for home: {home_id}, device: {device_id}")
    except Exception as e:
        logging.error(f"Error in WebSocket connection: {str(e)}")
        await websocket.close(code=1011)

@router.post("/mocupe")
async def mocup_device_energy(home_Id: str, device_Id:str):
    # home_id = "66923e98d8f087f776e8a085"
    # device_Id = "66923e98d8f087f776e8a086"
    asyncio.create_task(generate_data_periodically(home_Id, device_Id))

async def generate_data_periodically(home_Id: str, device_Id: str):

    while True:
        energy_item = Energy(energy=14, valid=True)
        try:
            await create_device_energy(home_Id, device_Id, energy_item)
        except HTTPException as e:
            print(f"Error: {e.detail}")
        await asyncio.sleep(60)