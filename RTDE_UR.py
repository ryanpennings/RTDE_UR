#!/usr/bin/env python
# Copyright (c) 2016, Universal Robots A/S,
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Universal Robots A/S nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL UNIVERSAL ROBOTS A/S BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import logging

import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import math
import csv
import time

print("Universal Robots - Real Time Point Streaming Application")
print("Ryan Pennings - 2017")
print("For enquiries/suppport contact design@ryanpennings.com")
print("")
print("connecting.....")
time.sleep(2)

####################################################################
# Setup var's
####################################################################

#logging.basicConfig(level=logging.INFO)

# Set IP of robot or simulation here
ROBOT_HOST = '192.168.40.128' #ROBOT_HOST = '192.168.100.132' 192.168.2.11
ROBOT_PORT = 30004
config_filename = 'control_loop_configuration.xml'

keep_running = True

logging.getLogger().setLevel(logging.INFO)

conf = rtde_config.ConfigFile(config_filename)
state_names, state_types = conf.get_recipe('state')
setp_names, setp_types = conf.get_recipe('setp')
tcp_names, tcp_types = conf.get_recipe('tcp')
tcp_payload_names, tcp_payload_types = conf.get_recipe('tcp_payload')
speed_names, speed_types = conf.get_recipe('speed')
zone_names, zone_types = conf.get_recipe('zone')
watchdog_names, watchdog_types = conf.get_recipe('watchdog')

sendPointSwitch = False

####################################################################
# Connect to Robot
####################################################################


con = rtde.RTDE(ROBOT_HOST, ROBOT_PORT)
con.connect()
print("Robot Connected.....")
time.sleep(2)
# get controller version
con.get_controller_version()

####################################################################
# Setup recipes
####################################################################

con.send_output_setup(state_names, state_types)
setp = con.send_input_setup(setp_names, setp_types)
tcp = con.send_input_setup(tcp_names, tcp_types)
tcp_payload = con.send_input_setup(tcp_payload_names, tcp_payload_types)
speed = con.send_input_setup(speed_names, speed_types)
zone = con.send_input_setup(zone_names, zone_types)
watchdog = con.send_input_setup(watchdog_names, watchdog_types)

####################################################################
# Import Commands from file
####################################################################
# 0,1,2,3,4,5 are point locations
# x,y,z,rx,ry,rz
# 6 is speed in m/s
# 7 is zone in m

listOfPoints = []
listOfSpeeds = []
listOfZones = []

with open('printing.txt') as f:
    reader = csv.reader(f,delimiter=',',quoting=csv.QUOTE_NONNUMERIC)
    w, h = 6, len(list(f))
    f.seek(0)
    listOfPoints = [[0 for x in range(w)] for y in range(h)] 
    listOfSpeeds = [0 for y in range(h)]
    listOfZones = [0 for y in range(h)]
    k = 0
    for row in reader:
        #listOfPoints.append([])
        listOfPoints[k]=[row[0],row[1],row[2],row[3],row[4],row[5]]
        listOfSpeeds[k] = row[6]
        listOfZones[k] = row[7]
        k += 1

# Read TCP

# 0,1,2,3,4,5 are point locations for tcp
# x,y,z,rx,ry,rz
# 6 weight in kg
# 7,8,9 are Centre of Gravity

tcpPos = [0,0,0,0,0,0]
tcpPayload = [0,0,0]

with open('tcp.txt') as f2:
    reader2 = csv.reader(f2,delimiter=',',quoting=csv.QUOTE_NONNUMERIC)
    f2.seek(0)
    for row in reader2:
        tcpPos = [row[0],row[1],row[2],row[3],row[4],row[5]]
        tcpPayload = [row[6],row[7],row[8],row[9]]

####################################################################
# Setup Points to send  - setp
####################################################################

setp.input_double_register_0 = 0
setp.input_double_register_1 = 0
setp.input_double_register_2 = 0
setp.input_double_register_3 = 0
setp.input_double_register_4 = 0
setp.input_double_register_5 = 0
setp.input_double_register_6 = 0
  
# The function "rtde_set_watchdog" in the "rtde_control_loop.urp" creates a 1 Hz watchdog
watchdog.input_int_register_0 = 0

def setp_to_list(setp):
    list = []
    for i in range(0,6):
        list.append(setp.__dict__["input_double_register_%i" % i])
    return list

def list_to_setp(setp, list):
    for i in range (0,6):
        setp.__dict__["input_double_register_%i" % i] = list[i]
    return setp

####################################################################
# Setup TCP & TCP Payload
####################################################################

tcp.input_double_register_7 = 0
tcp.input_double_register_8 = 0
tcp.input_double_register_9 = 0
tcp.input_double_register_10 = 0
tcp.input_double_register_11 = 0
tcp.input_double_register_12 = 0
tcp.input_double_register_13 = 0

tcp_payload.input_double_register_14 = 0
tcp_payload.input_double_register_15 = 0
tcp_payload.input_double_register_16 = 0
tcp_payload.input_double_register_17 = 0

def tcp_to_list(tcp):
    list = []
    for i in range(7,13):
        list.append(tcp.__dict__["input_double_register_%i" % i])
    return list

def list_to_tcp(tcp, list):
    k = 0
    for i in range (7,13):
        tcp.__dict__["input_double_register_%i" % i] = list[k]
        k += 1
    return tcp

def tcppayload_to_list(tcp_payload):
    list = []
    for i in range(14,15):
        list.append(tcp_payload.__dict__["input_double_register_%i" % i])
    return list

def list_to_tcppayload(tcp_payload, list):
    k = 0
    for i in range (14,15):
        tcp_payload.__dict__["input_double_register_%i" % i] = list[k]
        k += 1
    return tcp_payload

####################################################################
# Setup Speed & Zone
####################################################################

speed.input_double_register_18 = 0
zone.input_double_register_19 = 0

def createSpeed(speed, new_speed):
    speed.__dict__["input_double_register_18"] = new_speed
    return speed

def createZone(zone, new_zone):
    zone.__dict__["input_double_register_19"] = new_zone
    return zone

####################################################################
# Start Sync
####################################################################

#start data synchronization
if not con.send_start():
    sys.exit()

####################################################################
# Send TCP
####################################################################
tcpSent = False

while tcpSent == False:
    state = con.receive()

    if state is None:
        print "No State - Take me to Church"

    # Set switch
    if state.output_int_register_0 == 2:
        sendPointSwitchTCP = True

    # if robot is ready for a point, send it and move to next one
    if state.output_int_register_0 != 0 and sendPointSwitchTCP == True:
        sendPointSwitchTCP = False
        tcpSent = True
        # Send TCP
        new_tcp = tcpPos
        print "TCP Position: ", new_tcp
        list_to_tcp(tcp, new_tcp)
        con.send(tcp)

        # Send TCP Weight & COG
        new_payload = tcpPayload
        print "TCP Payload: ", new_payload
        list_to_tcppayload(tcp_payload, new_payload)
        con.send(tcp_payload)

        con.send(watchdog)


####################################################################
# Sync Loop
####################################################################

j = 0
while keep_running:
    # receive the current state
    state = con.receive()
    
    if state is None:
        break;

    if j >= h:
        break;

    # Set switch
    if state.output_int_register_0 == 1:
        sendPointSwitch = True

    # if robot is ready for a point, send it and move to next one
    if state.output_int_register_0 != 0 and sendPointSwitch == True:
        sendPointSwitch = False

        # Send Point
        new_setp = listOfPoints[j]
        print new_setp
        list_to_setp(setp, new_setp)
        con.send(setp)

        # Send Speed
        new_speed = listOfSpeeds[j]
        print new_speed
        createSpeed(speed, new_speed)
        con.send(speed)

        # Send Zone
        new_zone = listOfZones[j]
        print new_zone
        createZone(zone, new_zone)
        con.send(zone)

        j += 1

    # kick watchdog
    con.send(watchdog)


print("Finished Sending Points.. Waiting for robot to finish...")
print("Do NOT close this window...")


# wait for robot to finish printing
while True:
    state = con.receive()
    con.send(watchdog)
    if state.output_int_register_0 == 3:
        con.send_pause()
        con.disconnect()
        sys.exit()
