import argparse
from datetime import datetime
from datetime import timedelta
import json
from os import path
import pytz
import requests
import re
import urllib.request

#args
argparser = argparse.ArgumentParser(description='YouTube Channel Scraper')
argparser.add_argument("-profiles", default=False, help="If fed 'True', forces downloading of channel profile images")
profiles = argparser.parse_args().profiles
print("[HOLORIPPER] Downloading profile images: " + str(profiles))

# misc.
today = datetime.today()
utc = pytz.timezone('UTC')
updatejson = {}

# Get master data

# From URL
#with urllib.request.urlopen("https://example.url.com/Master.json") as url:
#    master = json.loads(url.read().decode())

# From Local
with open("data/Master.json", encoding='utf-8') as local:
    master = json.load(local)


for idol in master:
    
    # Logging
    print("[HOLORIPPER] " + master[idol]["nameEN"] + "...", end="")

    # Make rip container and add baseline info
    rip = {}
    rip["name"] = master[idol]["nameEN"]
    rip["ID"] = idol

    # Check for upcoming streams & fetch profile picture
    upcomingurl = "https://www.youtube.com/channel/" + idol + "/videos?view=2&live_view=502" # upcoming videos
    channel = requests.get(upcomingurl)
    channel.encoding = 'utf-8'  

    if (profiles): # Don't download existing profile images unless requested via '--profiles True' argument
        print("...getting images...")
        profurl = re.findall('(.{66}?)=s100-c-k-c0xffffffff', channel.text, re.MULTILINE|re.DOTALL)
        profile = requests.get(profurl[0])
        profname = idol + ".png" # Profile images are always .png
        with open("assets/profile/" + profname, 'wb') as image:
            image.write(profile.content)
    
    title = re.findall('<title>(.*?)</title>', channel.text, re.MULTILINE|re.DOTALL) # Getting data between <title> tags because all the HTML parsers choke
    title = "".join(map(str, title))
    final = title.replace("\n - YouTube", "")
    final = final.strip()

    # Add channel title to rip
    rip["channel"] = final

    # Checking for upcoming streams
    grugcounter = 0
    while (grugcounter < 3):
        if channel.text.find("livereminder") > -1:
            grugcounter = 4
        else:
            channel = requests.get(upcomingurl) # Grug try again
            channel.encoding = 'utf-8'
            grugcounter += 1
            
    if channel.text.find("livereminder") > -1: # One of a tiny handful of consistent HTML indicators for upcoming streams
        
        # Add upcoming status to rip
        rip["upcoming"] = "true"
        rip["upcomingVideos"] = {}
        
        streamslist = re.findall(r'(data-context-item-id=".{11})', channel.text)
        for s in streamslist:
            s = s[22:]

            # New container for each video
            broadrip = {}
            broadrip["ID"] = s
            
            broadcasturl = "https://www.youtube.com/watch?v=" + s
            broadcast = requests.get(broadcasturl)

            title = re.findall('<title>(.*?)</title>', broadcast.text, re.MULTILINE|re.DOTALL) # Getting data between <title> tags because all the HTML parsers choke
            totrim = "".join(map(str, title))
            trimmed = re.findall('(.*?) - YouTube', totrim)
            plswork = "".join(map(str, trimmed))

            # Add title to broadrip
            broadrip["title"] = plswork
            
            #Date parsing
            regex = r'((January|February|March|April|May|June|July|August|September|October|November|December) ([0-9]?[0-9])),( ([0-9]{4}),)? ([0-1]?[0-9]:[0-9][0-9] [A|P][M]) (([A-Z][A-Z][A-Z])(\+[0-9])?)'
            date = re.search(regex, broadcast.text)

            # Reformat Month
            month = date.group(2)
            month = datetime.strptime(month, "%B").strftime("%m")

            day = str(date.group(3))
            if date.group(5) is None:
                year = str(today.year) # Broadcasts scheduled for current year do not display the year in HTML, we will supply our own
            else:
                year = str(date.group(5))

            # Reformat Time
            time = date.group(6)
            ampm = time[-2:]
            time = datetime.strptime(time, "%H:%M %p").strftime("%H:%M:%S")
            
            
            # Hard-coded timezones. This is a bad idea but the only way to convert from 3-letter timezones due to overlap and deprecated codes.
            # IN THEORY for this specific use-case we should only need these two anyway, but if it breaks then I told you so
            if date.group(7) == "PDT":
                timezone = "US/Pacific"
            elif date.group(7) == "GMT+9":
                timezone = "Japan"

            # Begin building a proper timestamp
            naivezone = "-".join([year, month, day]) + " " + time
            naivezone = datetime.strptime(naivezone, "%Y-%m-%d %H:%M:%S")
            awarezone = pytz.timezone(timezone).localize(naivezone)
            if (ampm == "PM"):
                awarezone = awarezone + timedelta(hours = 12) # Bring back AM/PM data we stripped earlier
                

            # Finally, we arrive at ISO 8601 in UTC
            timestamp = awarezone.astimezone(utc).isoformat()

            # Add ETA to broadrip
            broadrip["ETA"] = timestamp

            # Append upcomingVideos
            rip["upcomingVideos"][s] = broadrip            
        
    else:

        # Add upcoming status to rip
        rip["upcoming"] = "false"
        rip["upcomingVideos"] = []
    
    # Check for live streams
    liveurl = "https://www.youtube.com/channel/" + idol + "/videos?view=2&live_view=501" # live videos
    channel = requests.get(liveurl)
    channel.encoding = 'utf-8'
    channel = channel.text

    if channel.find("yt-badge-live") > -1:

        # Add live status to rip
        rip["live"] = "true"
        streamslist = re.findall(r'(data-context-item-id=".{11})', channel)
        streamID = streamslist[0][22:]

        # Add streamID to rip
        rip["streamID"] = streamID

    else:

        # Add live status to rip
        rip["live"] = "false"
        rip["streamID"] = ""

    # Append this rip to the collection
    updatejson[master[idol]["nameEN"]] = rip
    rip = None

    # Logging
    print(" Done!")

# Save data to file
with open('HoloLive.json', 'w', encoding='utf8') as outfile:
    json.dump(updatejson, outfile, indent=4, ensure_ascii=False)

