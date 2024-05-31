"""Simplifies the use of Kasa devices and allows access by name instead of IP.  There is also 
a kache layer KacheDevices to improve discovery response times. """

# Relies on https://github.com/python-kasa/python-kasa
import json
import sys
import os

from kasa import Discover


# pylint: disable=broad-exception-raised, broad-exception-caught

def set_dirs():
    """ Ensure working directory = script directory. """
    if sys.path[0] != os.getcwd():
        print(f"Changing working directory to {sys.path[0]}")
        os.chdir( sys.path[0] )
    else:
        print("Working and script directories match.")
        
def load_json_file(fname):
    """Loads json file"""

    try:
        with open(fname, "r", encoding="utf-8") as sfile:
            json_data = json.load(sfile)

    except Exception as error:
        print(f"An exception while loading json file {fname}", error)        
        print(f"The current directory is: {os.getcwd()}")
        print(f"The system path is: {sys.path[0]}")
        raise

    return json_data

class KasaDevices:
    """Manages Kasa devices by alias instead of by IP address"""

    def __init__(self):
        """Dummy constructor.  You should call await discover() immediately after"""
        self.devices = {}
        self.addresses = {}

    async def discover(self):
        """This is the real constructor, call it with await"""
        self.devices = {}
        self.addresses = {}
        print("Looking for local Kasa devices")
        discovered = await Discover.discover()

        # Remake the device list so we can
        # use alias names to locate devices instead of
        # IP addresses.
        for _ in discovered:
            alias = discovered[_].alias
            self.devices[alias] = discovered[_]
            self.addresses[alias] = _

        return len(self.devices)

    async def turn_on(self, dev):
        """Turns a Kasa device on based on the device alias and returns status"""
        if not dev in self.devices:
            print(f"Can't find device to turn on: {dev}")
            return None
        
        if self.devices[dev].is_on:
            print(f"Device {dev} is already on")
        else:
            print(f"Turning {dev} on")
            await self.devices[dev].turn_on()
            await self.devices[dev].update()
        return self.devices[dev].is_on

    async def turn_off(self, dev):
        """Turns a Kasa device off based on the device alias and returns status"""
        if not dev in self.devices:
            print(f"Can't find device to turn off: {dev}")
            return None
        
        if self.devices[dev].is_off:
            print(f"Device {dev} is already off")
        else:
            print(f"Turning {dev} off")
            await self.devices[dev].turn_off()
            await self.devices[dev].update()
        return self.devices[dev].is_off

    def get(self, dev):
        """Returns a single device"""
        if not dev in self.devices:
            print(f"No such device: {dev}")
            return None
        else:
            return self.devices[dev]

    def is_on(self, dev):
        """Returns whether the device is on or not"""
        if not dev in self.devices:
            print(f"No such device: {dev}")
            return None
        return self.devices[dev].is_on

    def report(self, dev):
        """Checks to see if a device exists in the current list"""
        if not dev in self.devices:
            print(f"No such device: {dev}")
            return None

        state = self.devices[dev].is_on
        if state:
            print(f"{dev} is on.")
        else:
            print(f"{dev} is off.")

        return state

    async def update(self, dev):
        """Updates a single device."""
        if not dev in self.devices:
            print(f"No such device: {dev}")
            return None

        await self.devices[dev].update()


class KacheDevices(KasaDevices):
    """We cache the device aliases and their IP addresses, but not the state. 
    Upon loading the cache we get the actual device states.  Speeds up the script which 
    can be slow (20-30s) if it has to discover all devices on the net.
    """


    def __init__(self, kache_fname = "kache.json"):
        self.devices = {}
        self.addresses = {}
        self.kfile = kache_fname
        super().__init__()

    async def refresh(self):
        """Forces a complete refresh/rediscovery of all devices and saves the new results to cache"""
        print("Refreshing cache")
        await super().discover()
        self.write()

    async def discover(self, *targets):
        """Looks to see if we have valid kache entries for targets, 
        forces a full discovery otherwise
        """
        self.devices = {}
        self.addresses = {}

        is_refreshed = False

        if not targets:
            raise Exception("No devices passed, so can't validate list.")

        print(f"Looking for {len(targets)} devices.")

        # tries = 0
        try:
            cache = load_json_file(self.kfile)

            for _ in targets:
                if _ in cache:
                    await self._discover_single(cache[_], _)
                else:
                    raise Exception(f"Device {_} not found in cache list.")

            print("Found them.")

        except Exception as error:
            print("An exception while looking for the devices forced a refresh:", error)
            await self.refresh()
            is_refreshed = True

        if is_refreshed:
            for _ in targets:
                if _ in self.devices and _ in self.addresses:
                    pass
                else:
                    raise RuntimeError(f"Can't find {_} in device list after a refresh")

        return len(self.devices)

    async def _discover_single(self, addy, alias):
        """Gets the device at addy, and checks the alias to see if we have the
         expected device or not."""
        single = await Discover.discover_single(addy)

        if not single:
            raise Exception(f"No device found at {addy}")

        if single.alias == alias:
            self.addresses[alias] = addy
            self.devices[alias] = single
        else:
            print(f"Alias mismatch, wanted: {alias} but got {single.alias} ")
            raise Exception(f"{alias} not found at {addy}")

    def write(self):
        """Saves the current device cache"""
        print("Writing new kache")
        with open(self.kfile, "w", encoding="utf-8") as jf:
            json.dump(self.addresses, jf)
