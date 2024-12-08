from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Body, HTTPException
from auth.jwt_bearer import RoleChecker, JWTBearer
from fastapi.encoders import jsonable_encoder
import logging
from models.homes import *
from database.database import *
from service.deviceEnergy import *
from models.derTelemetry import *
from models.deviceEnergy import *
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

async def verify_websocket_jwt(websocket: WebSocket, allowed_roles: list):
    token = websocket.headers.get("Authorization")
    if token is None or not token.startswith("Bearer "):
        await websocket.close(code=1008)  # Policy Violation
        raise HTTPException(status_code=403, detail="Authorization required")

    # Remove the "Bearer " prefix to get the actual token
    jwt_token = token[7:]
    jwt_bearer = JWTBearer()
    
    try:
        # Verify the JWT token manually
        user = await jwt_bearer.verify_jwt(jwt_token)
        role_checker = RoleChecker(allowed_roles)

        # Use the role checker to validate permissions
        if not await role_checker(user):
            await websocket.close(code=1008)
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient role permissions")

        # Return the validated user
        return user

    except Exception as e:
        await websocket.close(code=1008)
        raise HTTPException(status_code=403, detail=str(e))

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, home_Id: str, device_Id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data.lower() == "ping":
                await websocket.send_text("pong")
            else:
                await websocket.send_text("Send 'ping' to get 'pong'")
    except WebSocketDisconnect:
        print(f"WebSocket connection closed for device {device_Id} in home {home_Id}")

@router.websocket("/energy")
async def websocket_device_energy(websocket: WebSocket, home_Id: str, device_Id: str, interval: int = 5):
    await websocket.accept()
    logging.info(f"WebSocket connection accepted for home: {home_Id}, device: {device_Id}")
    try:
        user = await verify_websocket_jwt(websocket, allowed_roles=["USER", "SUPEROPERATOR"])
        logging.info(f"Authenticated WebSocket connection for user {user.username} in home: {home_Id}, device: {device_Id}")
        while True:
            energy_data = await get_device_energy_data(home_Id, device_Id, interval)
            await websocket.send_json({"device_id": device_Id, "energy": energy_data})
            await asyncio.sleep(interval * 60)  # Convert minutes to seconds
    except WebSocketDisconnect:
        logging.info(f"WebSocket disconnected for home: {home_Id}, device: {device_Id}")
    except Exception as e:
        logging.error(f"Error in WebSocket connection: {str(e)}")
        await websocket.close(code=1011)