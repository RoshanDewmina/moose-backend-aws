from fastapi import Body, APIRouter, Request
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from database.database import *
from database.database import admin_collection
from auth.jwt_handler import signJWT, decodeJWT
from models.users import UserModel, UserCredentials,TokenRefreshRequest
from fastapi import HTTPException
import jwt
from service.admin import *
from service.userLog import *
from service.emailPermission import *

router = APIRouter()

hash_helper = CryptContext(schemes=["bcrypt"])
refresh_tokens = {}


@router.post("/login")
async def user_login(user_credentials: UserCredentials = Body(...)):
    await add_default_email_permissions()
    user = await admin_collection.find_one({"email": user_credentials.email.lower()})
    if (user):
        current_email = user_credentials.email.lower()
        # if current_email not in [email.lower() for email in list_of_emails]:
        #     raise HTTPException(status_code=400, detail="Email is not allowed")        
        check_email = await check_user_email_with_permission(current_email)
        if check_email is None:
            raise HTTPException(status_code=400, detail="Email is not allowed") 
        
        password = hash_helper.verify(user_credentials.password, user["password"])
        if (password) and user["verified"]:
            user["userID"] = str(user.pop("_id"))

            # Get HEMSCID using apiKey
            if user.get("apiKey"):
                api = user["apiKey"]
                hemsc_entry = await hemsc_collection.find_one({"apiKey": api})
                if hemsc_entry:
                    hemsc_entry.get("hemscID")

            # save in log
            await save_user_login_in_log(user)

                
            tokens = signJWT(data={"user_id": user_credentials.email, "type": user["type"]})
            refresh_tokens[user_credentials.email] = tokens['access_token']
            response = {
                "token": tokens,
                "user": remove_sensitive_fields(user)
            }
            return response
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    raise HTTPException(status_code=401, detail="Incorrect email or password")

def remove_sensitive_fields(data: dict) -> dict:
    data.pop('password', None)
    return data

@router.post("/token/refresh")
async def refresh_token(request: TokenRefreshRequest):
    try:
        payload = decodeJWT(request.refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        email = payload.get("user_id")
        if not email or refresh_tokens.get(email) != request.refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = await admin_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_tokens = signJWT(data={"user_id": email, "type": user["type"]})
        refresh_tokens[email] = new_tokens['access_token']
        return new_tokens
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired refresh token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.options("/login")
async def user_login_options():
    allowed_methods = ["POST", "OPTIONS"]
    allowed_headers = ["Authorization", "Content-Type"]
    return {
        "allow": allowed_methods,
        "allow_headers": allowed_headers
    }

@router.post("/")
async def user_signup(user: UserModel = Body(...)):
    await add_default_email_permissions()
    user_exists = await admin_collection.find_one({"email":  user.email}, {"_id": 0})
    if(user_exists):
        return "Email already exists"

    user.password = hash_helper.encrypt(user.password)
    new_user = await add_user(jsonable_encoder(user))
    if new_user != {}:
        if user.apiKey:
           await connect_user_to_homes(user.email)
        return new_user
    else:
        return "Please contact for a pre-registration first!"


