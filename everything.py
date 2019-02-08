#!/usr/bin/python2 -u

import time
import datetime
import ephem
import urllib
import urllib2
import socket
import json
import re
import atexit
import os
import sys
from convertdate import hebrew

#from geopy import geocoders
#ADDRESS = "1600 Pennsylvania Avenue, Washington DC"
#g = geocoders.GoogleV3()
#location = g.geocode(ADDRESS)

HMONTHS = {True: ("", "Nisan", "Iyar", "Sivan", "Tammuz", "Av", "Elul", "Tishrei", "Heshvan", "Kislev", "Tevet", "Shevat", "Adar1", "Adar2"), False: ("", "Nisan", "Iyar", "Sivan", "Tammuz", "Av", "Elul", "Tishrei", "Heshvan", "Kislev", "Tevet", "Shevat", "Adar")}

def ord(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

ipapi = json.loads(urllib2.urlopen("http://ip-api.com/json").read().decode('utf-8'))

homeloc = ephem.Observer()
#homeloc.lat, homeloc.lon = location.longitude*ephem.pi/180, location.longitude*ephem.pi/180
homeloc.lat, homeloc.lon = ipapi['lat']*ephem.pi/180, ipapi['lon']*ephem.pi/180

sun = ephem.Sun()
#sun.compute(homeloc)


if time.localtime().tm_isdst > 0:
    tzseconds = time.altzone
else:
    tzseconds = time.timezone

timenow = datetime.datetime.utcnow()
localtimenow = (timenow - datetime.timedelta(seconds=tzseconds))

d = datetime.datetime.utcnow()
nowstring = ("{0.year}/{0.month}/{0.day} {0.hour}:{0.minute}:{0.second}").format(d)
homeloc.date = nowstring

sunup = False
hebdateoffset = 0
if homeloc.previous_rising(sun) > homeloc.previous_setting(sun):
    sunup = True
    prevriseset = homeloc.previous_rising(sun)
    nextriseset = homeloc.next_setting(sun)
else:
    prevriseset = homeloc.previous_setting(sun)
    nextriseset = homeloc.next_rising(sun)
    if localtimenow.hour >= 12:
        hebdateoffset=12
nextriseset12hr = (ephem.localtime(nextriseset).hour+11)%12+1

oldhorizon = homeloc.horizon
# All horizon math is from top of sun disk
# We need to take into account sun's radius, averaging .266 degrees
homeloc.horizon = "-8.233" # middle of sun 8.5 deg
tzeit = homeloc.next_setting(sun)
#tzeit12hr = (ephem.localtime(tzeit).hour+11)%12+1
homeloc.horizon = oldhorizon
hebgregdate = localtimenow + datetime.timedelta(hours=hebdateoffset)
#print "{} {} {}".format(hebgregdate.year, hebgregdate.month, hebgregdate.day)
hebdate = hebrew.from_gregorian(hebgregdate.year, hebgregdate.month, hebgregdate.day)
#hebdatestr = "{} {}".format(hebdate[2], HMONTHS[hebrew.leap(hebdate[0])][hebdate[1]])
hebdatestr1 = "{} of ".format(ord(hebdate[2]))
hebdatestr2 = "{} ".format(HMONTHS[hebrew.leap(hebdate[0])][hebdate[1]])
if (hebdate[1] == 1 and hebdate[2] >= 16) or hebdate[1] == 2 or (hebdate[1] ==3 and hebdate[2] < 6):
    hebdatestr1 = "{} {}".format(hebdate[2], hebdatestr2)
    omercount = hebdate[2] - 15
    if hebdate[1] > 1: omercount += 30
    if hebdate[1] > 2: omercount += 29
    hebdatestr2 = "{} omer ".format(omercount)

timenow = datetime.datetime.utcnow()
nowstring = ("{0.year}/{0.month}/{0.day} {0.hour}:{0.minute}:{0.second}").format(timenow)
homeloc.date = nowstring
halfdayfrac = (timenow-prevriseset.datetime()).total_seconds()/(nextriseset.datetime()-prevriseset.datetime()).total_seconds()
# seconds, not chalakim
cheleklength = (nextriseset-prevriseset)*2
chalakimperhour = 3600
chalakimperminute = 60

chalakim = int(halfdayfrac * 12 * chalakimperhour)

benhashmashot = False
if sunup:
    pass
elif (tzeit > homeloc.date) and (tzeit - ephem.hour < homeloc.date):
    benhashmashot = True
    tiltzeit = int(((tzeit.datetime()-datetime.timedelta(microseconds=tzeit.datetime().microsecond)) - (timenow-datetime.timedelta(microseconds=timenow.microsecond))).total_seconds())
    #print tiltzeit
    secstiltzeit = tiltzeit % 60
    minstiltzeit = tiltzeit // 60

chalakimhours = chalakim//chalakimperhour
wallshaot1 = "{}.{:02d}".format(chalakimhours, (chalakim%chalakimperhour)//chalakimperminute)
#wallshaot2 = ".{:02d}".format((chalakim%1080)%18)
wallshaot2 = ".{:02d}".format((chalakim%chalakimperhour)%chalakimperminute)

localtimenow = (timenow - datetime.timedelta(seconds=tzseconds))
walltime = "{}:{}:{}".format(int(localtimenow.strftime("%I")), localtimenow.strftime("%M"), localtimenow.strftime("%S"))
hrsdigits = int(localtimenow.strftime("%I"))//10 + 1

print(wallshaot1 + wallshaot2)
