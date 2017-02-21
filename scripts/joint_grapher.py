#!/usr/bin/env python

import argparse
import rospy
import time
import matplotlib.pyplot as plt
import math

# import baxter_interface
from sensor_msgs.msg import JointState

accessTime = 0.0

#Values from joint state message w/o the arm specification
armKeys = ['_s0', '_s1', '_e0', '_e1', '_w0', '_w1', '_w2']
numVals = 500
values = {}
desiredValueName = ""


def callback(data):
    global values

    #Desired Values
    dv = eval("data."+desiredValueName)
    dat = dict(zip(data.name, dv))
    keyTest = 'right_w0'
    #Sanity check, sometimes the incoming data does not have the arm joints
    if keyTest in dat:
        for key in armKeys:
            values[key].append(dat[key])
            values[key].pop(0)

def main():
    arg_fmt = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=arg_fmt)
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '-l', '--limb', required=True, choices=['left', 'right'],
        help='Specifies which limb to monitor.'
    )
    required.add_argument(
        '-v', '--valueName', required=True,
        choices=['position', 'velocity', 'effort'],
        help='Specifies which values to monitor.'
    )
    args = parser.parse_args(rospy.myargv()[1:])

    global values, armKeys, desiredValueName

    #Adjust the keys to match arm parameter
    armKeys = [args.limb + k for k in armKeys]

    #Setup 
    desiredValueName = args.valueName
    
    #Initialize lines, value and x values
    lines = {k:None  for k in armKeys}
    values = {k:[0.0]*numVals for k in armKeys}
    x = range(numVals) #Used as time

    print("Initializing node... ")
    rospy.init_node("joint_grapher")

    rospy.Subscriber("robot/joint_states", JointState, callback)

    #Setup plot lines 
    fig =plt.figure()
    for k in armKeys:
        lines[k], = plt.plot(x, values[k])
    plt.ion()
    plt.show()

    #Set bounds on y axis
    bounds = {
    "position":(-4.0,4.0),
    "velocity":(-10.0,10.0),
    "effort":(-15.0,15.0)
    }
    plt.ylim(bounds[desiredValueName])

    while not rospy.is_shutdown():
        time.sleep(0.1)
        for key in armKeys:
            lines[key].set_ydata(values[key])
        plt.draw()

    print("Done.")

if __name__ == '__main__':
    main()
