#!/usr/bin/env python
# MIT License

# Copyright (c) [2021] [Ryan Pennings]

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import csv


def tcp_to_list(tcp):
    list = []
    for i in range(7, 13):
        list.append(tcp.__dict__["input_double_register_%i" % i])
    return list


def list_to_tcp(tcp, list):
    k = 0
    for i in range(7, 13):
        tcp.__dict__["input_double_register_%i" % i] = list[k]
        k += 1
    return tcp


def tcppayload_to_list(tcp_payload):
    list = []
    for i in range(14, 15):
        list.append(tcp_payload.__dict__["input_double_register_%i" % i])
    return list


def list_to_tcppayload(tcp_payload, list):
    k = 0
    for i in range(14, 15):
        tcp_payload.__dict__["input_double_register_%i" % i] = list[k]
        k += 1
    return tcp_payload


def setp_to_list(setp):
    list = []
    for i in range(0, 6):
        list.append(setp.__dict__["input_double_register_%i" % i])
    return list


def list_to_setp(setp, list):
    for i in range(0, 6):
        setp.__dict__["input_double_register_%i" % i] = list[i]
    return setp


def createSpeed(speed, new_speed):
    speed.__dict__["input_double_register_18"] = new_speed
    return speed


def createZone(zone, new_zone):
    zone.__dict__["input_double_register_19"] = new_zone
    return zone


def importTCP(tcpfilename):
    """
    Returns the TCP given a TCP file name.
            Parameters:
                    tcpfilename (string): Filename
            Returns:
                    tcpPos (list): list of 6 ints
                    tcpPayload (list): list - mass, cogx, cogy, cogz
    """
    # 0,1,2,3,4,5 are point locations for tcp
    # x,y,z,rx,ry,rz
    # 6 weight in kg
    # 7,8,9 are Centre of Gravity
    tcpPos = [0, 0, 0, 0, 0, 0]
    tcpPayload = [0, 0, 0, 0]
    with open(tcpfilename) as f2:
        reader2 = csv.reader(f2, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
        f2.seek(0)
        for row in reader2:
            tcpPos = [row[0], row[1], row[2], row[3], row[4], row[5]]
            tcpPayload = [row[6], row[7], row[8], row[9]]
            print("{0} loaded".format(tcpfilename))
            return tcpPos, tcpPayload


def importPoints(printfilename):
    """
    Imports all the points into lists and turns them.
            Parameters:
                    printfilename (string): Filename
            Returns:
                    points (list): list of points
                    speeds (list): list of speeds
                    zones (list): list of zones
    """
    # 0,1,2,3,4,5 are point locations
    # x,y,z,rx,ry,rz
    # 6 is speed in m/s
    # 7 is zone in m

    listOfPoints = []
    listOfSpeeds = []
    listOfZones = []

    with open(printfilename) as f:
        reader = csv.reader(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
        w, h = 6, len(list(f))
        f.seek(0)
        listOfPoints = [[0 for x in range(w)] for y in range(h)]
        listOfSpeeds = [0 for y in range(h)]
        listOfZones = [0 for y in range(h)]
        k = 0
        for row in reader:
            # listOfPoints.append([])
            listOfPoints[k] = [row[0], row[1], row[2], row[3], row[4], row[5]]
            listOfSpeeds[k] = row[6]
            listOfZones[k] = row[7]
            k += 1
        print("{0} loaded".format(printfilename))
        return listOfPoints, listOfSpeeds, listOfZones


def importPoints_IO(printfilename):
    """
    Imports all the points into lists and turns them.
            Parameters:
                    printfilename (string): Filename
            Returns:
                    points (list): list of points
                    speeds (list): list of speeds
                    zones (list): list of zones
                    io's (list): list of IO's
    """
    # 0,1,2,3,4,5 are point locations
    # x,y,z,rx,ry,rz
    # 6 is speed in m/s
    # 7 is zone in m
    # 8 is IO on or off, defined in URP

    listOfPoints = []
    listOfSpeeds = []
    listOfZones = []
    listOfIO = []

    numParams = 8

    with open(printfilename) as f:
        reader = csv.reader(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
        w, h = numParams, len(list(f))
        f.seek(0)
        listOfPoints = [[0 for x in range(w)] for y in range(h)]
        listOfSpeeds = [0 for y in range(h)]
        listOfZones = [0 for y in range(h)]
        k = 0
        for row in reader:
            # listOfPoints.append([])
            listOfPoints[k] = [row[0], row[1], row[2], row[3], row[4], row[5]]
            listOfSpeeds[k] = row[6]
            listOfZones[k] = row[7]
            listOfIO[k] = row[8]
            k += 1
        print("{0} loaded".format(printfilename))
        return listOfPoints, listOfSpeeds, listOfZones, listOfIO
