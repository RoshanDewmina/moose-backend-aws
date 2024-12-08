import json
import requests
import sys
import os
import aiohttp
import random
import logging
import logging.config
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from service.mockup_deviceEnergy import *

# logging.basicConfig(level=logging.INFO)
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# console_handler.setFormatter(formatter)
# logging.getLogger().addHandler(console_handler)
# logger = logging.getLogger(__name__)

logger.info(f'Started')

api_url = 'http://127.0.0.1:8000'
home_Id = "66a556f5b0f6b029e3d245b7"
device_Id = "66a556f5b0f6b029e3d245ba"
api_key = "123456789"

async def get_token_from_apiKey(api_key:str):
    token =  await token_from_apiKey(api_key)
    if token is None:
       logger.info(f'There is no user with the provided APIKey= 123456789')

    logger.info(f'find suitable user for this Apikey')
    return token

async def post_device_energy():
    try:
        auth_token = await get_token_from_apiKey(api_key)
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
        energy_value = random.randint(200, 250)
        payload = {
            'energy': energy_value,
            'valid': True
        }
        url = f'{api_url}/homes/{home_Id}/devices/{device_Id}/devicesEnergy/?homeId={home_Id}&deviceID={device_Id}'

        # logger.info(f'Sending request to URL: {url} with payload: {payload}')
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                # f'{api_url}/homes/{home_Id}/devices/{device_Id}/devicesEnergy/?homeId={home_Id}&deviceID={device_Id}',
                json=payload,
                headers=headers
            ) as response:
                response_text = await response.text()
                # logger.info(f'Response Status: {response.status}')
                logger.info(f'Response Text: {response_text}')
                # if response.status == 200:
                #     logger.info(f'Consumption is recorded for {home_Id}')
                # else:
                #     error_message = await response.text()
                #     logger.info(f'Error, GUI server is not responding for {home_Id}. Response: {error_message}')
    except Exception as e:
        logger.exception(f"An error occurred: {e}")

async def main(api_token: Optional[str] = None):
    logger.info("Running main function")
    if not api_token:
        raise ValueError("API token is required")
    await post_device_energy()
    logger.info("Finished main function")

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(post_device_energy, 'interval', minutes=1)
    scheduler.start()
    return scheduler

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    scheduler = start_scheduler()
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown")
    finally:
        scheduler.shutdown()
        loop.close()

