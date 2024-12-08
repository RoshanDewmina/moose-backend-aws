from typing import List, Optional, Dict
from pydantic import BaseModel, validator, Field
from datetime import datetime
from bson import ObjectId

class Setpoint(BaseModel):
    _id: str
    name: str
    coolingSetpoint: float
    heatingSetpoint: float
    fanSpeed: int
    changedByServer: bool
    dates: dict

    @validator('_id', check_fields=False)
    def check_objectid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

class Schedule(BaseModel):
    scheduleStartHour: int
    scheduleStartMin: int
    switchStatus: int
    setpointIndex: int
    changedByServer: bool
    dateUpdated: Optional[datetime]

class Device(BaseModel):
    _id: str
    name: str
    loadTypeID: int
    priority: int
    macAddress: str
    modeID: int
    changedByServer: bool
    setpoints: List[Setpoint]
    schedules: Dict[str, List[Schedule]]
    thermostatMode: int
    fanModeID: int
    range: int
    coolingSetpoint: int
    heatingSetpoint: int
    holdType: int
    holdTime: int
    switchStatus: int
    batteryChargeStartTime: int
    batteryChargeFinishTime: int
    batteryDischarge1StartTime: int
    batteryDischarge1FinishTime: int
    batteryDischarge2StartTime: int
    batteryDischarge2FinishTime: int
    discharge1Level: int
    discharge2Level: int
    dateUpdated: Optional[datetime]
    dateCreated: Optional[datetime]
    status: Optional[int] = None

    @validator('_id', check_fields=False)
    def check_objectid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "5a9e3449b572e101fe470d7f",
                "name": "Pump",
                "loadTypeID": 1,
                "priority": 2,
                "macAddress": "dc:a6:40:60:83:2f",
                "modeID": 1,
                "changedByServer": False,
                "setpoints": [],                
                "status":0,
                "schedules": {
                    "monday": [
                        {
                            "scheduleStartHour": 10,
                            "scheduleStartMin": 15,
                            "switchStatus": 1,
                            "setpointIndex": 0,
                            "changedByServer": False,
                            "dateUpdated": "2024-06-12T10:14:19.968Z"
                        }
                    ],
                    "tuesday": [],
                    "wednesday": [],
                    "thursday": [],
                    "friday": [],
                    "saturday": [],
                    "sunday": []
                },
                "thermostatMode": 0,
                "fanModeID": 0,
                "range": 0,
                "coolingSetpoint": 0,
                "heatingSetpoint": 0,
                "holdType": 0,
                "holdTime": 0,
                "switchStatus": 0,
                "batteryChargeStartTime": 0,
                "batteryChargeFinishTime": 0,
                "batteryDischarge1StartTime": 0,
                "batteryDischarge1FinishTime": 0,
                "batteryDischarge2StartTime": 0,
                "batteryDischarge2FinishTime": 0,
                "discharge1Level": 0,
                "discharge2Level": 0,
                "dateCreated": "2024-06-12T10:14:19.968Z",
                "dateUpdated": "2024-06-12T10:14:19.968Z"

            }
        }

class Preference(BaseModel):
    comfort: int
    dateUpdated: datetime

class Hemsc(BaseModel):
    _id: str
    hemscID: str
    address: str
    apiKey: str
    community: Optional[str] = None
    preference: Preference
    users: List[str]
    devices: List[Device]
    dates: dict

    @validator('_id', check_fields=False)
    def check_objectid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "5a9e3449b572e101fe470d7f",
                "hemscID": "6543211",
                "address": "25 Tempeleton St",
                "apiKey": "123456789",
                "preference": {
                    "comfort": 2,
                    "dateUpdated": "2023-12-01T05:13:40.955Z"
                },
                "users": [
                    "5a9e3469b572e102562e6a08", "5a9e3469b572e102562e6a09"
                ],
                "devices": [ ],                   
                
                "dates": {
                    "dateCreated": "2023-12-01T02:40:37.321Z",
                    "dateUpdated": "2023-12-01T02:40:37.321Z"
                }
            }
        }

class PreferenceUpdate(BaseModel):
    comfort: int
    dateUpdated: Optional[datetime] = None

class HemscUpdate(BaseModel):
    _id: Optional[str] = None
    hemscID: Optional[str] = None
    address: str
    apiKey: Optional[str] = None
    community: Optional[str] = None
    preference: PreferenceUpdate
    users: Optional[List[str]] = None
    devices: Optional[List[Device]] = None
    dates: Optional[dict] = None

    @validator('_id', check_fields=False)
    def check_objectid_shape(cls, value):
        if value is not None:
            try:
                ObjectId(value)
            except Exception as e:
                raise ValueError(f'Invalid ObjectId format: {e}')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "address": "25 Tempeleton St",
                "apiKey": "123456789",
                "preference": {
                    "comfort": 2
                }
            }
        }

class SetpointUpdated(BaseModel):
    _id: str
    name: Optional[str] = None
    coolingSetpoint: Optional[float] = None
    heatingSetpoint: Optional[float] = None
    fanSpeed: Optional[int] = None
    changedByServer: Optional[bool] = None
    dates: Optional[dict] = None

    @validator('_id', check_fields=False)
    def check_objectid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

class ScheduleUpdated(BaseModel):
    scheduleStartHour: Optional[int] = None
    scheduleStartMin: Optional[int] = None
    switchStatus: Optional[int] = None
    setpointIndex: Optional[int] = None
    changedByServer: Optional[bool] = None
    dateUpdated: Optional[datetime] = None

class DeviceUpdated(BaseModel):
    _id: str
    name: Optional[str] = None
    loadTypeID: Optional[int] = None
    priority: Optional[int] = None
    macAddress: Optional[str] = None
    modeID: Optional[int] = None
    changedByServer: Optional[bool] = None
    setpoints: Optional[List[SetpointUpdated]] = None
    schedules: Optional[Dict[str, List[ScheduleUpdated]]] = None
    thermostatMode: Optional[int] = None
    fanModeID: Optional[int] = None
    range: Optional[int] = None
    coolingSetpoint: Optional[int] = None
    heatingSetpoint: Optional[int] = None
    holdType: Optional[int] = None
    holdTime: Optional[int] = None
    switchStatus: Optional[int] = None
    batteryChargeStartTime: Optional[int] = None
    batteryChargeFinishTime: Optional[int] = None
    batteryDischarge1StartTime: Optional[int] = None
    batteryDischarge1FinishTime: Optional[int] = None
    batteryDischarge2StartTime: Optional[int] = None
    batteryDischarge2FinishTime: Optional[int] = None
    discharge1Level: Optional[int] = None
    discharge2Level: Optional[int] = None
    dateUpdated: Optional[datetime] = None
    dateCreated: Optional[datetime] = None
    status: int

    @validator('_id', check_fields=False)
    def check_objectid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "5a9e3449b572e101fe470d7f",
                "name": "Pump",
                "status": 5,
                "loadTypeID": 1,
                "priority": 2,
                "macAddress": "dc:a6:40:60:83:2f",
                "modeID": 1,
                "changedByServer": False,
                "setpoints": [],
                "status": 0,
                "schedules": {
                    "monday": [
                        {
                            "scheduleStartHour": 10,
                            "scheduleStartMin": 15,
                            "switchStatus": 1,
                            "setpointIndex": 0,
                            "changedByServer": False,
                            "dateUpdated": "2024-06-12T10:14:19.968Z"
                        }
                    ],
                    "tuesday": [],
                    "wednesday": [],
                    "thursday": [],
                    "friday": [],
                    "saturday": [],
                    "sunday": []
                },
                "thermostatMode": 0,
                "fanModeID": 0,
                "range": 0,
                "coolingSetpoint": 0,
                "heatingSetpoint": 0,
                "holdType": 0,
                "holdTime": 0,
                "switchStatus": 0,  # This is required
                "batteryChargeStartTime": 0,
                "batteryChargeFinishTime": 0,
                "batteryDischarge1StartTime": 0,
                "batteryDischarge1FinishTime": 0,
                "batteryDischarge2StartTime": 0,
                "batteryDischarge2FinishTime": 0,
                "discharge1Level": 0,
                "discharge2Level": 0,
                "dateCreated": "2024-06-12T10:14:19.968Z",
                "dateUpdated": "2024-06-12T10:14:19.968Z"
            }
        }

def ResponseModel(data, code ,message):
    return {
        "data": [
            data
        ],
        "code": code,
        "message": message,
    }

def ErrorResponseModel(error, code, message):
    return {
        "error": error,
        "code": code,
        "message": message
    }
