# app.py
import os
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.templating import Jinja2Templates
from fastapi.params import Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader

from service.derTelemetry import shutdown_scheduler

import logging
import random
import asyncio
from auth.jwt_bearer import RoleChecker
from routes.admin import router as AdminRouter
from routes.device import router as DeviceRouter
from routes.event import router as EventRouter
from routes.deviceEnergy import router as DeviceEnergyRouter
from routes.energy import router as EnergyRouter
from routes.homes import router as HomeRouter
from routes.schedule import router as ScheduleRouter
from routes.setpoint import router as SetpointRouter
from routes.preference import router as PreferenceRouter
from routes.temperature import router as TemperatureRouter
from routes.homeEnergy import router as HomeEnergyRouter
from routes.derTelemetry import router as DerTelemetryRouter
from routes.emailPermission import router as EmailPermissionRouter
from routes.userLog import router as UserLogRouter
from routes.manageUsers import router as ManageUserRouter
from routes.pricing import router as PricingRouter
from routes.webSockets import router as WebsocketRouter

description = """
CoVue API is a enables you
to check and set µ-Tie configurations
"""

app = FastAPI(title="GridVue Swagger API",
              description=description,
              version="0.0.2",
              contact={
                  "name": "GridVue Energy",
                  "url": "https://GridVue.ca/",
                  "email": "info@GridVue.ca"
                  },
              docs_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["*"]
api_key_header = APIKeyHeader(name="api-key", auto_error=False)
async def authorize_request(api_key_header: str = Security(api_key_header)):
    if "API_KEY" in os.environ:
        if api_key_header == os.environ["API_KEY"]:
            return api_key_header
        elif api_key_header == None:
            raise HTTPException(
                status_code=401, detail="authorization header missing")
        else:
            raise HTTPException(
                status_code=401, detail="incorrect authorization credentials")
    else:
        raise HTTPException(
            status_code=403, detail="please create an admin secret key")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="GridVue API",
        swagger_favicon_url="/static/img/favicon.ico"
    )

templates = Jinja2Templates(directory="templates")
@app.get("/instruction", include_in_schema=False)
async def instruction_ui_html(request: Request):
    return templates.TemplateResponse("instructions.html", {"request": request})

@app.get("/", tags=["Root"], include_in_schema=False)
async def read_root():
    return {"message": "Welcome to GridVue CoVue API."}

@app.on_event("shutdown")
async def shutdown_event():
    shutdown_scheduler()

app.include_router(AdminRouter, tags=["Administrator"], prefix="/api", )
app.include_router(ManageUserRouter, tags=["Manage User"], prefix="/manageUser", dependencies=[Depends(RoleChecker(allowed_roles=["SUPEROPERATOR"]))])
app.include_router(EmailPermissionRouter, tags=["User Provisioning"], prefix="/provisioning", dependencies=[Depends(RoleChecker(allowed_roles=["SUPEROPERATOR"]))])
app.include_router(UserLogRouter, tags=["User Log"], prefix="/userlog", dependencies=[Depends(RoleChecker(allowed_roles=["SUPEROPERATOR"]))])
app.include_router(HomeRouter, tags=["Home"], prefix="/homes", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
app.include_router(PreferenceRouter, tags=["Preference"], prefix="/homes/{home_Id}/preference", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
app.include_router(DeviceRouter, tags=["Devices"], prefix="/homes/{home_Id}/devices", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
app.include_router(DeviceEnergyRouter, tags=["Devices Energy"], prefix="/homes/{home_Id}/devices/{device_Id}/devicesEnergy", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
app.include_router(DerTelemetryRouter, tags=["Telemetry"], prefix="/homes/{home_Id}", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
app.include_router(ScheduleRouter, tags=["Schedule"], prefix="/homes/{home_Id}/devices/{device_Id}/schedule", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
app.include_router(SetpointRouter, tags=["Setpoint"], prefix="/homes/{home_Id}/devices/{device_Id}/setpoint", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
app.include_router(PricingRouter, tags=["Billing and Pricing"], prefix="/homes/{home_Id}/pricing", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
app.include_router(EventRouter, tags=["Event"], prefix="/homes/{home_Id}/events", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
app.include_router(TemperatureRouter, tags=["Temperature"], prefix="/temperature", dependencies=[Depends(RoleChecker(allowed_roles=["USER", "SUPEROPERATOR"]))])
app.include_router(WebsocketRouter, tags=["Websockets"], prefix="/homes/{home_Id}/devices/{device_Id}/ws", )