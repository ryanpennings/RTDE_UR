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

import argparse
import logging
import sys

sys.path.append("..")
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config
import time
import ringBuffer as rb


def main():

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    print("Universal Robots - (semi) Real Time Point Streaming ring buffer")
    print("Ryan Pennings - 2021")
    print("For enquiries/suppport visit: https://github.com/ryanpennings/RTDE_UR")
    print("")
    print("loading files...")

    tcp_pos, tcp_cog = rb.importTCP(args.tcpfile)
    points, speeds, zones = rb.importPoints(args.printfile)

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
    # Setup setp
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
            rb.list_to_tcp(tcp, new_tcp)
            con.send(tcp)

            # Send TCP Weight & COG
            new_payload = tcp_cog
            print("TCP Payload: ", new_payload)
            rb.list_to_tcppayload(tcp_payload, new_payload)
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

            rb.list_to_setp(setp, new_setp)
            con.send(setp)

            # Send Speed
            new_speed = speeds[j]
            rb.createSpeed(speed, new_speed)
            con.send(speed)

            # Send Zone
            new_zone = zones[j]
            rb.createZone(zone, new_zone)
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

