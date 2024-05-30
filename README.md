# NetTest
This is a trivial Python project which relies on Kasa smart plugs to power cycle my primary Internet modem when I lose connection to my service provider (currently Hargray) and alert me of Internet problems by turning on a lamp until the situation is cleared. 

## Smart Plugs
The external requirements of this script are [Kasa Smart Plugs (shameless Amazon Associate Link provided!)](https://amzn.to/3QRZwwb) and I have to say I'm pretty happy with the overall Kasa ecosystem so far. 

## What does it do
A cron job runs check_connect.py every 10 minutes to see if my primary Internet provider is the one being used.  

*If Active*
* Check the status lamp is off
* Exits

*If Inactive*
* Turns on a lamp 
* Power cycles the modem
* Waits up to 3 minutes for the router to switch back
* If the router has switched back the lamp goes back off
* Exits, potentially with the lamp still on depending on the Internet status

The script interacts with the modem and indicator lamp but not the router.  Instead it relies on the router to automatically detect when the primary modem has reconnected, which works very reliably. 

## Purpose
I often work remotely but my primary Internet provider goes out about twice a month.  As a result I've had to supplement it with a T-Mobile 5G modem and a router to detect outages and failover. The router's status detection for the two Internet modems works fine but the primary modem may NEVER recover if it is not power cycled.  This is a limitation of the modem, not the router.  In addition to cycling the modem I wanted a way to notice when I was having issues, so that's why I turn on a dedicated lamp. 

Originally I was going to run this on the Linux powered router itself but it didn't have all the OS package prerequisites needed for the Python Kasa library without possibly some major low level hackery which could have prevented future updates.  This _should_ work on a Raspberry Pi though. 

## Cool Parts
I've written a couple of classes on top of the Kasa lib, which are in kasa_utils: 
* KasaDevices - Inverts the devices map so I can address devices by name instead of IP address.  Adds utility functions for those devices.
* KacheDevices - A kache (haha) wrapper for KasaDevices which normally eliminates the ~20 seconds of discovery time on my home network.  It validates that kache entries for the lamp and modem are still valid for the named devices before using them and will refresh if not. 

## Cron 
Because crafting a working cron job is sometimes tricky, here is what I use: 
```
*/10 * * * * /usr/bin/python /home/erik/bin/check_connect.py 2>&1 | /usr/bin/logger -t NetTest
```
## Testing
The only testing done here is what's shown in check_connect.py.  I assume the kache layer will work for any Kasa device, but the only use of the underlying library I've tried is for smart plugs. 

## Credits
This repo relies on the [Python Kasa library](https://github.com/python-kasa/python-kasa) by [Teemu R.](https://github.com/rytilahti) and I'm very grateful for it. 

## Warranty
As you should imagine, this free/hobby code is provided with no warranty whatsoever and any potential safety risks in automating appliances is assumed entirely by the user. 

Automating plugs supplying 120V / 15A is not entirely risk free, especially if used for anything more important than a cable modem and indicator lamp. 