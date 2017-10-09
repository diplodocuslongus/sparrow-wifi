#!/usr/bin/python3
# 
# Copyright 2017 ghostop14
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import os
import subprocess
import re
from gps3 import gps3
from gps3.agps3threaded import AGPS3mechanism
from time import sleep
from threading import Thread

class GPSThread(Thread):
    def __init__(self, gpsEngine):
        super(GPSThread, self).__init__()
        self.signalStop = False
        self.threadRunning = False
        self.mainEngine = gpsEngine

        self.agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
        self.agps_thread.stream_data()  # From localhost (), or other hosts, by example, (host='gps.ddns.net')
        self.agps_thread.run_thread()  # Throttle time to sleep after an empty lookup, default '()' 0.2 two tenths of a second

    def run(self):
        self.threadRunning = True
        
        while (not self.signalStop):
            try:
                gpsResult = SparrowGPS()
                
                try:
                    gpsResult.altitude = float(self.agps_thread.data_stream.alt)
                    gpsResult.latitude = float(self.agps_thread.data_stream.lat)
                    gpsResult.longitude = float(self.agps_thread.data_stream.lon)
                    gpsResult.speed = float(self.agps_thread.data_stream.speed)
                    gpsResult.isValid = True
                except:
                    gpsResult.isValid = False
                    
                self.mainEngine.onGPSResult(gpsResult)
                        
            except:
                pass

            sleep(0.3)
            
        self.agps_thread.stop()
        self.threadRunning = False


class GPSStatus(object):
    def __init__(self):
        super().__init__()
        self.gpsInstalled = False
        self.gpsRunning = False
        self.gpsSynchronized = False
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.speed = 0.0
    
class GPSEngine(object):
    def __init__(self):
        super().__init__()
        
        self.lastCoord = None
        
        self.gpsThread = None
        
        if GPSEngine.GPSDRunning():
            self.gpsAvailable = True
        else:
            self.gpsAvailable = False

    def getLastCoord(self):
        return self.lastCoord
        
    def gpsValid(self):
        if self.lastCoord is None:
            return False
            
        return self.lastCoord.isValid
        
    def onGPSResult(self, gpsResult):
        self.lastCoord = gpsResult
        
    def start(self):
        self.gpsThread = GPSThread(self)
        self.gpsThread.start()

    def stop(self):
        if self.gpsThread and self.gpsThread.threadRunning:
            self.gpsThread.signalStop = True
            while self.gpsThread.threadRunning:
                sleep(0.1)
            
    def engineRunning(self):
        if self.gpsThread is None:
            return False
            
        return self.gpsThread.threadRunning
        
    def GPSDInstalled():
        if os.path.isfile('/usr/sbin/gpsd'):
            return True
        else:
            if os.path.isfile('/usr/local/sbin/gpsd'):
                return True
            else:
                return False
                
    def GPSDRunning():
        # ps = subprocess.Popen("ps aux | grep gpsd | grep -v grep", shell=True, stdout=subprocess.PIPE)
        # output = ps.stdout.read()
        # ps.stdout.close()
        # ps.wait()

        # gpsResult = output.decode('ASCII')

        # if re.search('/gpsd', gpsResult) is None:
        #    return False
        #else:
        #    return True
        gps_socket = gps3.GPSDSocket()
        try:
            gps_socket.connect()
            gps_socket.close()
            return True
        except:
            return False


class SparrowGPS(object):
    def __init__(self):
        super().__init__()
        
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.speed = 0.0
        self.isValid = False
        
    def __str__(self):
        retVal = ""
        
        retVal += "Is Valid: " +str(self.isValid) + "\n"
        retVal += "Latitude: " +str(self.latitude) + "\n"
        retVal += "Longitude: " +str(self.longitude) + "\n"
        retVal += "Altitude: " +str(self.altitude) + "\n"
        retVal += "Speed: " +str(self.speed) + "\n"

        return retVal