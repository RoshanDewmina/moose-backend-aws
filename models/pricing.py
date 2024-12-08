from pydantic import BaseModel, validator, Field
from typing import Dict, Optional, List, Literal


class PricingSchema(BaseModel):
    _id: Optional[str] = None
    hemscID: str
    schema_name: Literal["flat_rate", "time_of_use", "tiered"]
    description: str

    class Config:
        pass

class FlatRatePricing(PricingSchema):
    flat_rate: float = Field(..., gt=0, description="Flat rate per kWh")

    @validator('flat_rate')
    def check_positive_rate(cls, value):
        if value <= 0:
            raise ValueError('Flat rate must be greater than zero')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "5a9e3449b572e101fe470d7f",
                "hemscID": "5a9e3449b572e101fe470d7f",
                "schema_name": "flat_rate",
                "description": "Flat rate pricing for all usage",
                "flat_rate": 0.15
            }
        }

class TimeOfUsePricing(PricingSchema):
    peak_rate: float = Field(..., gt=0, description="Rate during peak hours per kWh")
    off_peak_rate: float = Field(..., gt=0, description="Rate during off-peak hours per kWh")
    peak_hours: List[int] = Field(..., description="List of peak hours (0-23)")

    @validator('peak_hours')
    def check_peak_hours(cls, value):
        if not all(0 <= hour <= 23 for hour in value):
            raise ValueError('Peak hours must be within the range 0-23')
        return value

    @validator('peak_rate', 'off_peak_rate')
    def check_positive_rate(cls, value):
        if value <= 0:
            raise ValueError('Rate must be greater than zero')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "5a9e3449b572e101fe470d7f",
                "hemscID": "5a9e3449b572e101fe470d7f",
                "schema_name": "time_of_use",
                "description": "Pricing based on time of day",
                "peak_rate": 0.20,
                "off_peak_rate": 0.10,
                "peak_hours": [8, 9, 17, 18]
            }
        }

class TieredPricing(PricingSchema):
    tiers: List[dict] = Field(..., description="List of pricing tiers with 'limit' and 'rate'")

    @validator('tiers')
    def check_tiers(cls, value):
        if not value:
            raise ValueError('Tiers cannot be empty')
        for tier in value:
            if 'limit' not in tier or 'rate' not in tier:
                raise ValueError("Each tier must include 'limit' and 'rate'")
            if tier['limit'] <= 0 or tier['rate'] <= 0:
                raise ValueError('Tier limits and rates must be greater than zero')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "5a9e3449b572e101fe470d7f",
                "hemscID": "5a9e3449b572e101fe470d7f",
                "schema_name": "tiered",
                "description": "Pricing based on usage tiers",
                "tiers": [
                    {"limit": 100, "rate": 0.10},
                    {"limit": 200, "rate": 0.15},
                    {"limit": 300, "rate": 0.20},
                ]
            }
        }

class CalculatePricingRequest(BaseModel):
    home_Id: str
    usage: float
    usage_data: Optional[Dict[int, float]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "Flat Rate": {
                    "summary": "Example for flat rate pricing",
                    "value": {
                        "home_Id": "5a9e3449b572e101fe470d7f",
                        "usage": 150.0
                    }
                },
                "Time of Use": {
                    "summary": "Example for time of use pricing",
                    "value": {
                        "home_Id": "5a9e3449b572e101fe470d7f",
                        "usage": 150.0,
                        "usage_data": {
                            "0": 5.0,
                            "1": 3.5,
                            "8": 20.0,
                            "17": 15.0,
                            "18": 10.0
                        }
                    }
                },
                "Tiered Pricing": {
                    "summary": "Example for tiered pricing",
                    "value": {
                        "home_Id": "5a9e3449b572e101fe470d7f",
                        "usage": 150.0
                    }
                }
            }
        }

def ResponseModel(data,code, message):
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
