from pydantic import BaseModel, EmailStr, validator
from bson import ObjectId

from pydantic import BaseModel, EmailStr, validator
from bson import ObjectId

class AccountConfirmation(BaseModel):
    accountConfirmationID: str
    email: EmailStr

    @validator('accountConfirmationID')
    def check_objectid_shape(cls, value):
        try:
            ObjectId(value)
        except Exception as e:
            raise ValueError(f'Invalid ObjectId format: {e}')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "accountConfirmationID": "659837818c69940043999d70",
                "email": "info@jazzsolar.com"
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
