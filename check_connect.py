#! /usr/bin/python
"""
Checks to see if we are on the preferred network or not.  If not a lamp is turned on and the 
modem is bounced to attempt to reconnect. 
"""
import os
import sys
import asyncio

from time import sleep

from kasa_utils import KacheDevices, set_dirs
from timer import Timer

# pylint: disable=broad-exception-caught


def net_test(net_name="hargray.net", steps=7):
    """Test to see if we are on the right WAN or not."""
    print(f"Looking for {net_name}")
    found = net_name in os.popen(f"traceroute -m {steps} 1.1.1.1").read()
    if found:
        print(f"Found {net_name}")
    else:
        print(f"Did not find {net_name}")

    return found


async def main():
    """Tests our network and reboots the modem when needed"""

    set_dirs()

    devs = KacheDevices("kache.json")

    #
    # If we don't have the right devices we can't go on, so fast fail here.
    #
    try:
        await devs.discover("Modem", "Net lamp")
    except Exception as error:
        print("Unable to continue.")
        print(error)
        sys.exit(0)

    #
    #
    ####################################################################
    #
    # If we are not on the preferred network....
    if not net_test():

        # Alert that the network has switched
        await devs.turn_on("Net lamp")

        #
        # Bounce the modem
        #

        # Start the timer.
        t = Timer()
        print("Attempting to bounce the modem.")

        if devs.is_on("Modem"):
            print("Turning modem off and waiting to cool down.")
            await devs.turn_off("Modem")
            sleep(30)
        else:
            print("Modem was already off.")
        await devs.turn_on("Modem")
        print("Modem is back on, testing network every 30 seconds.")

        #
        # Wait for the modem to come back and the router to see it
        #
        while t.elapsed() <= 300:
            sleep(30)
            if net_test():
                print("Hargray is back!")
                print(f"Seconds to reconnect: {t}")
                await devs.turn_off("Net lamp")
                break

            print(f"Still waiting at {t} seconds.")
        else:
            print("Ran out of time checking for network.")

    else:
        # We're already where we want to be, just double check the
        # lamp is off.
        await devs.turn_off("Net lamp")


if __name__ == "__main__":
    asyncio.run(main())
