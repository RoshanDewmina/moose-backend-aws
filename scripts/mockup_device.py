import json
import requests
import sys
import os
import random
import logging
import logging.config
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)
logger = logging.getLogger(__name__)

logger.info(f'Started')
api_url = 'http://127.0.0.1:8000/docs'

# api_url = 'http://localhost:3000/api'
api_key = "123456789"
inverterMac = '38:87:16:39:9f:0a'
MacAddressList = ['74:1c:17:09:17:e9', 'dc:a6:40:60:83:2f', '55:85:7e:66:a8:22']
socMax = 95
socMin = 10
consumption = 0.5
charging = 1

async def post_home_energy():
    try:
        headers = {'content-type': 'application/json', "api_key": api_key}
        payload = {'energy': random.uniform(9, 19)}
        r = requests.post(f'{api_url}/home-energy', data=json.dumps(payload), headers=headers)
        if r.status_code == 200:
            logger.info(f'Consumption is recorded for home {api_key}')
        else:
            logger.info(f'Error, GUI server is not responding for home ID: {api_key}')
    except:
        raise

async def post_device_energy(item):
    try:
        headers = {'content-type': 'application/json', "api_key": api_key}
        payload = {'energy': float(random.uniform(2, 4))}

        r = requests.post(api_url + f'/devices/{item}/energy', data=json.dumps(payload), headers=headers)
        if r.status_code == 200:
            logger.info(f'Consumption is recorded for {item}')
        else:
            logger.info(f'Error, GUI server is not responding for {item}')
    except:
        raise

async def post_der_telemetry():
    try:
        headers = {'content-type': 'application/json', "api_key": api_key}
        payload = {"phaseAVoltage": random.uniform(218, 222),
                   "phaseBVoltage": random.uniform(218, 222),
                   "unitACWatts": random.uniform(10, 13),
                   "frequency": random.uniform(49.5, 50.5),
                   "dcVoltage": random.uniform(392, 402),
                   "dcWatts": random.uniform(10, 13),
                   "soc": random.uniform(90, 95),
                   "availableStorage": random.uniform(90, 95),
                   "batteryVoltage": random.uniform(45, 50),
                   "pvVoltage": random.uniform(45, 50)}
        r = requests.post(f'{api_url}/devices/{inverterMac}/der-telemetry',
                          data=json.dumps(payload),
                          headers=headers)
        if r.status_code == 200:
            logger.info(f'Consumption is recorded for DER {inverterMac}')
        else:
            logger.info(f'Error, GUI server is not responding to DER {inverterMac}')
    except:
        raise

last_soc = socMax  # Initialize the global variable

async def post_battery_soc():
    global last_soc
    if last_soc > socMin:
        last_soc -= consumption
    elif last_soc < 95:
        last_soc += charging

    headers = {'content-type': 'application/json', "x-api-key": api_key}
    payload = {'energy': last_soc}
    r = requests.post(f'{api_url}/devices/{inverterMac}/energy', data=json.dumps(payload), headers=headers)
    if r.status_code == 200:
        logger.info(f'Battery SOC is recorded for DER {inverterMac}: {last_soc}')
    else:
        logger.info(f'Error, GUI server is not responding to DER {inverterMac}')

    return last_soc

async def main():
    global last_soc
    await post_home_energy()
    await asyncio.gather(*(post_device_energy(item) for item in MacAddressList))
    await post_der_telemetry()
    last_soc = await post_battery_soc()

if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    scheduler.add_job(main, 'interval', minutes=10)
    scheduler.start()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()