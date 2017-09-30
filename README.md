# RTDE_UR
Real Time Data Exchange streaming for universal robots. (Streams points to robot, for running large files)
This was specifically developed to run large, complex 3D prints (i.e. 500,000 points and above)

WIP... still updating repo with example files.

Uses python 2.7

This script only streams move L commands, along with speed and radius/zone information per target.
You will be able to pause and play from the robot controller.
It also sends TCP data, so set this in grasshopper.

It uses a simple ring buffer of ten points, normally the ring buffer fills so fast that it never empty's.

#### Instructions
- Copy contents of UR folder to usb (with nothing else on it)
- Plug into controller as per https://www.universal-robots.com/download/?option=16588#section16578
- Load "rtde_2.urp" on the robot
- Adjust the initial move position to something suitable for your program
- Copy this move position into grasshopper file for simulation purposes
- Create your program in grasshopper, and save text files to the same directory as "RTDE_UR.py"
- Make sure UR program is at start, press play. Robot will move into position, press play again and a popup will tell you start script on PC.
- Make sure you have adjusted the IP to match your robots IP in "RTDE_UR.py"
- Start the script, it should connect to the robot.
- Once connected, press play on the robot, the script should start streaming points.
- Once all the points are sent, do not close the script. Let the robot finish moving first.

#### Troubleshooting

###### The script sends all the points at once.
Try resetting the script to the start, a variable is set wrong. If that doesn't work, restart the robot.

###### Fieldbus Disconnected error on robot
Most likely you started the main part of the robot program before the script on the pc connected to the robot. If it happens during the program running, the network connection has been lost.

#### See this link for more information
https://www.universal-robots.com/how-tos-and-faqs/how-to/ur-how-tos/real-time-data-exchange-rtde-guide-22229/
