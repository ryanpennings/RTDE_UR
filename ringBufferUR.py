#!/usr/bin/env python
# copyright message here

import argparse
import logging
import sys

sys.path.append("..")
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import rtde.csv_writer as csv_writer
import rtde.csv_binary_writer as csv_binary_writer
import time
import csv

# move all these into a module
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


def main():

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    print("Universal Robots - (semi) Real Time Point Streaming ring buffer")
    print("Ryan Pennings - 2021")
    print("For enquiries/suppport visit: https://github.com/ryanpennings/RTDE_UR")
    print("")
    print("loading files...")

    tcp_pos, tcp_cog = importTCP(args.tcpfile)
    points, speeds, zones = importPoints(args.printfile)

    print("")
    print("connecting.....")
    time.sleep(2)

    keep_running = True
    sendPointSwitch = False
    sendPointSwitchTCP = False

    ####################################################################
    # Setup var's
    ####################################################################

    conf = rtde_config.ConfigFile(args.config)
    state_names, state_types = conf.get_recipe("state")
    setp_names, setp_types = conf.get_recipe("setp")
    tcp_names, tcp_types = conf.get_recipe("tcp")
    tcp_payload_names, tcp_payload_types = conf.get_recipe("tcp_payload")
    speed_names, speed_types = conf.get_recipe("speed")
    zone_names, zone_types = conf.get_recipe("zone")
    watchdog_names, watchdog_types = conf.get_recipe("watchdog")

    ####################################################################
    # Connect to Robot
    ####################################################################

    con = rtde.RTDE(args.host, args.port)
    con.connect()
    print("Robot Connected")

    # get controller version
    con.get_controller_version()

    ####################################################################
    # Setup recipes
    ####################################################################

    # if not con.send_output_setup(output_names, output_types, frequency=args.frequency):
    #    logging.error("Unable to configure output")
    #    sys.exit()

    # find way to get these to check as above
    con.send_output_setup(state_names, state_types, frequency=args.frequency)
    setp = con.send_input_setup(setp_names, setp_types)
    tcp = con.send_input_setup(tcp_names, tcp_types)
    tcp_payload = con.send_input_setup(tcp_payload_names, tcp_payload_types)
    speed = con.send_input_setup(speed_names, speed_types)
    zone = con.send_input_setup(zone_names, zone_types)
    watchdog = con.send_input_setup(watchdog_names, watchdog_types)

    ###############################
    # Setup step
    ###############################

    setp.input_double_register_0 = 0
    setp.input_double_register_1 = 0
    setp.input_double_register_2 = 0
    setp.input_double_register_3 = 0
    setp.input_double_register_4 = 0
    setp.input_double_register_5 = 0
    setp.input_double_register_6 = 0

    # The function "rtde_set_watchdog" in the "rtde_control_loop.urp" creates a 1 Hz watchdog
    watchdog.input_int_register_0 = 0

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

    ####################################################################
    # Setup Speed & Zone
    ####################################################################

    speed.input_double_register_18 = 0
    zone.input_double_register_19 = 0

    ####################################################################
    # Start Sync
    ####################################################################

    # start data synchronization
    if not con.send_start():
        sys.exit()

    ####################################################################
    # Send TCP
    ####################################################################

    tcpSent = False

    print("Waiting to send TCP - please start robot program now....")

    while tcpSent == False:

        state = con.receive()

        if state is None:
            print("No State")

        # Set switch
        if state.output_int_register_0 == 2:
            sendPointSwitchTCP = True

        # if robot is ready for a point, send it and move to next one
        if state.output_int_register_0 != 0 and sendPointSwitchTCP == True:
            sendPointSwitchTCP = False
            tcpSent = True
            # Send TCP
            new_tcp = tcp_pos
            print("TCP Position: ", new_tcp)
            list_to_tcp(tcp, new_tcp)
            con.send(tcp)

            # Send TCP Weight & COG
            new_payload = tcp_cog
            print("TCP Payload: ", new_payload)
            list_to_tcppayload(tcp_payload, new_payload)
            con.send(tcp_payload)

            print("TCP sent.")

        con.send(watchdog)

    ####################################################################
    # Main Sync Loop
    ####################################################################

    print("starting main sync loop....")
    j = 0
    while keep_running:
        # receive the current state
        state = con.receive()

        if state is None:
            break

        if state.output_int_register_0 == 3:
            con.send_pause()
            con.disconnect()
            sys.exit()

        # Set switch
        if state.output_int_register_0 == 1:
            sendPointSwitch = True

        # if robot is ready for a point, send it and move to next one
        if state.output_int_register_0 != 0 and sendPointSwitch == True:
            sendPointSwitch = False

            # Send Point
            new_setp = points[j]

            list_to_setp(setp, new_setp)
            con.send(setp)

            # Send Speed
            new_speed = speeds[j]
            createSpeed(speed, new_speed)
            con.send(speed)

            # Send Zone
            new_zone = zones[j]
            createZone(zone, new_zone)
            con.send(zone)

            print("Line: {3} : {0},{1},{2}".format(new_setp, new_speed, new_zone, j))
            j += 1

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


if __name__ == "__main__":
    # start program
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", default="localhost", help="name of host to connect to (localhost)"
    )
    parser.add_argument("--port", type=int, default=30004, help="port number (30004)")
    parser.add_argument(
        "--frequency",
        type=int,
        default=125,
        help="the sampling frequency in Herz (125hz max for CB series, 500hz max for E Series",
    )
    parser.add_argument(
        "--config",
        default="control_loop_configuration.xml",
        help="data configuration file to use (record_configuration.xml)",
    )
    parser.add_argument(
        "--verbose", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "--notbuffered",
        default=True,
        help="disable buffered receive which doesn't skip data",
        action="store_false",
    )
    parser.add_argument(
        "-pf",
        "--printfile",
        help="file name of print file to send",
        required=False,
        default="printing.txt",
    )
    parser.add_argument(
        "-tcp",
        "--tcpfile",
        help="file name of tcp to send",
        required=False,
        default="tcp.txt",
    )

    args = parser.parse_args()
    main()

