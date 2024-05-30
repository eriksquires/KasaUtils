# check_temp.py
I am a cat living on an outdoor porch in a hot humid climate.  I have adopted a home with a nice man who feeds me and keeps me well hydrated and makes sure I have all my shots and flea meds.  He'd like me to live inside where he has heating, AC and a plush couch but I refuse all his advances.

When I found out he had installed [Kasa smart switches](https://amzn.to/4azRAqf) I wrote this Python script to turn the porch fan on when its too hot and back off when it's nice.  He also discovered my utils could be used to bounce the cable modem when it won't reset itself.  Hazzah! 

## Kacheing
If you are not a dog or a delivery person you may also use this as an example of using the KacheDevices layer which simplifies and speeds up the use of Teemu's original work, below. 

## Configuration
Rename sample.json to site.json and fill in the values with your data, especially your API key from OpenWeatherMap.

## Dependencies and Credits
*  [Python Kasa library](https://github.com/python-kasa/python-kasa) by [Teemu R.](https://github.com/rytilahti)

No longer using [Python Weather](https://github.com/null8626/python-weather) by [Null8626](https://github.com/null8626) as there's some sort of rate limiting, but [OpenWeatherMap](https://openweathermap.org) gives you 100 calls/day for free, which is perfect for this frugal cat. API is too simple to use a module for.


# check_connect.py
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
I am a cat and cannot be sued. If you use this code and regret it that's pretty much on you. 
