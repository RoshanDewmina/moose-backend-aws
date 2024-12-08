import aiohttp
import asyncio
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config

# Replace with your email and password
EMAIL = config('MOCK_USER')
PASSWORD = config('MOCK_PASS')

# Global variables to store the access token and data
access_token = None
data = None

async def authenticate():
    global access_token
    async with aiohttp.ClientSession() as session:
        login_url = 'https://staging.api.moose.jazzsolar.com/api/login'
        login_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        async with session.post(login_url, json=login_data) as login_response:
            if login_response.status == 200:
                login_json = await login_response.json()
                access_token = login_json["token"]["access_token"]
                print("Authentication successful.")
                await fetch_data(session)  # Fetch data once after authentication
            else:
                print(f"Authentication failed with status {login_response.status}")
                access_token = None

async def fetch_data(session):
    global data
    home_url = 'https://staging.api.moose.jazzsolar.com/homes/'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    async with session.get(home_url, headers=headers) as home_response:
        if home_response.status == 200:
            home_json = await home_response.json()
            data = []
            homes = home_json.get('data', [])
            for home_list in homes:
                for home in home_list:
                    home_Id = home.get("_id")
                    devices = home.get("devices", [])
                    device_Ids = [device["_id"] for device in devices]
                    
                    home_data = {
                        "home_Id": home_Id,
                        "device_Ids": device_Ids
                    }
                    data.append(home_data)
            print("Data fetched successfully.")
        else:
            print(f"Failed to fetch data with status {home_response.status}")
            data = None

async def post_device_energy():
    global access_token, data
    if not access_token:
        print("No access token available. Attempting to re-authenticate...")
        await authenticate()
        if not access_token:
            print("Re-authentication failed. Skipping posting energy data.")
            return

    async with aiohttp.ClientSession() as session:
        for item in data:
            home_Id = item["home_Id"]
            device_Ids = item["device_Ids"]
            if device_Ids:
                for device_Id in device_Ids:
                    energy_value = int(random.uniform(90, 120))  # Ensuring energy is an integer
                    devices_energy_url = (
                        f'https://staging.api.moose.jazzsolar.com/homes/{home_Id}/devices/{device_Id}/devicesEnergy/'
                        f'?homeId={home_Id}&deviceID={device_Id}'
                    )
                    headers = {
                        'accept': 'application/json',
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                    payload = {
                        "energy": energy_value,
                        "valid": True
                    }

                    async with session.post(devices_energy_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            print(f"Energy value {energy_value} posted for device {device_Id} in home {home_Id}")
                        elif response.status == 401:  # Unauthorized, need to re-authenticate
                            print("Token expired or unauthorized. Re-authenticating...")
                            access_token = None  # Invalidate the token
                            await authenticate()  # Re-authenticate
                            return  # Exit to allow rescheduling with new token
                        else:
                            response_text = await response.text()
                            print(f"Failed to post energy value for device {device_Id} in home {home_Id} with status {response.status}")
                            print(f"Response: {response_text}")

async def scheduled_task():
    await post_device_energy()

async def main():
    await authenticate()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_task, 'interval', minutes=5)
    scheduler.start()

    # Keep the event loop running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour; the scheduler will keep running
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    asyncio.run(main())
