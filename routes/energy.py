from fastapi import APIRouter, Body

from database.database import *
from models.events import *
from models.temperatures import *

router = APIRouter()

# @router.get("/import_energy")
# async def get_import_energy():
#     data = await retrieve_import_events()
#     return ResponseModel(data, "Import energy is retrieved successfully") \
#         if len(data) > 0 \
#         else ResponseModel(
#         data, "Empty list returned")

# @router.get("/export_energy")
# async def get_export_energy():
#     data = await retrieve_export_events()
#     return ResponseModel(data, "Export energy is retrieved successfully") \
#         if len(data) > 0 \
#         else ResponseModel(
#         data, "Empty list returned")

# @router.post("/temperatures")
# async def create_export_energy(req: TemperatureModel = Body(...)):
#     data = await add_temperatures(req.dict())
#     return ResponseModel(data, "Temperatures inserted successfully") \
#         if len(data) > 0 \
#         else ResponseModel(
#         data, "Empty list returned")

# @router.get("/temperatures")
# async def get_temperatures():
#     data = await retrieve_temperatures()
#     return ResponseModel(data, "Temperatures is retrieved successfully") \
#         if len(data) > 0 \
#         else ResponseModel(
#         data, "Empty list returned")