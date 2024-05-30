#! /usr/bin/python
"""
Checks the outside temperature via OpenWeatherMap and turns the porch fan on and off as needed
"""

# pylint: disable=broad-exception-caught,broad-exception-raised


import asyncio
import sys

import requests
from kasa_utils import load_json_file, KacheDevices, set_dirs

TEMP_TURN_ON = 85
TEMP_TURN_OFF = 78
FAN = "Porch Fan"


SITE_FILE = "site.json"  # Parameters for OpenWeatherMap API



def get_temp():
    """Get local current temperature"""
    site = load_json_file(SITE_FILE)

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = f'?lat={site["lat"]}&lon={site["long"]}&appid={site["key"]}&units={site["units"]}'
    response = requests.get(url + params, timeout=20)

    if response.status_code != 200:
        raise Exception("Invalid response from OpenWeatherMap")

    w = response.json()

    return w["main"]["temp"]


#
#########################################
#
async def main():
    """Tests the outside temperature and turns on the porch fan when needed"""

    set_dirs()
    
    devs = KacheDevices("fan_kache.json")

    #
    # If we don't have the right devices we can't go on, so fast fail here.
    #
    try:
        await devs.discover(FAN)
    except Exception as error:
        print("Unable to continue.")
        print(error)
        sys.exit(0)

    #
    #
    ####################################################################
    #
    # Turns the fan on or off depending on the outside weather.
    #
    # Note that turn_on and turn_off check the device state and
    # take no action if it is already set correctly.
    #

    try:
        current_temp = get_temp()
    except Exception as error:
        print("Exiting due to lack of valid temp data")
        print(error)
        sys.exit(0)

    print(f"The temperature is {current_temp} F")
    if current_temp >= TEMP_TURN_ON:
        await devs.turn_on(FAN)

    elif current_temp < TEMP_TURN_OFF:
        await devs.turn_off(FAN)


if __name__ == "__main__":
    asyncio.run(main())
