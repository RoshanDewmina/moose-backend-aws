from pydantic import BaseModel, Field, EmailStr

class AdminModel(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "Javad Fattahi",
                "email": "javad.fattahi@uottawa.ca",
                "password": "uOttawa!456"
            }
        }