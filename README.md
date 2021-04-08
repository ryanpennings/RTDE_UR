#### Updated April 2021
A new cleaner script. Expect more updates soon. Code is currently incomplete but does work.

## RTDE_UR
Real Time Data Exchange streaming for universal robots. (Streams points to robot, for running large files)
This was specifically developed to run large, complex 3D prints (i.e. 500,000 points and above, however it doesnt work for that as lots of points in quick succession cause jumpy movement, look at other commands.. [servoJ] from memory)

Currently this script only streams with moveL commands. moveJ, speedJ and servoJ will be added soon.
You will be able to pause and play from the robot controller.
It also sends TCP data, so set this in grasshopper.

It uses a simple ring buffer of ten points, normally the ring buffer fills so fast that it never empty's.

## Instructions

- Copy contents of UR folder to usb (with nothing else on it)
- Plug into controller as per https://www.universal-robots.com/download/?option=16588#section16578
- Load "rtde_moveL_1.urp" on the robot
- Adjust the initial move position (moveJ) to something suitable for your program
- Copy this move position into grasshopper file for simulation purposes
- Create your program in grasshopper, and save text files to the same directory as "ringBufferUR.py"
- Make sure UR program is at start, press play. Robot will move into position, and a popup will tell you start script on PC.
- Start the script with the following command: `python ringBufferUR.py --host 192.168.1.100`, it should connect to the robot. Make sure to change the IP to that of your robot.
- Once connected, press continue on the robot, the script should start streaming points.
- Once all the points are sent, do not close the script. Let the robot finish moving first.

Script was written for Python 3.8.

## Troubleshooting

###### The script sends all the points at once.
Try resetting the script to the start, a variable is set wrong. If that doesn't work, restart the robot.

###### Fieldbus Disconnected error on robot
Most likely you started the main part of the robot program before the script on the pc connected to the robot. If it happens during the program running, the network connection has been lost.

#### See this link for more information
https://www.universal-robots.com/how-tos-and-faqs/how-to/ur-how-tos/real-time-data-exchange-rtde-guide-22229/
https://www.universal-robots.com/articles/ur/interface-communication/connecting-to-client-interfaces-within-ursim/

Licensed with MIT License