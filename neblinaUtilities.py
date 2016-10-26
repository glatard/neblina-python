#!/usr/bin/env python
###################################################################################
#
# Copyright (c)     2010-2016   Motsai
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
###################################################################################

import os
import time
import math

from itertools import zip_longest

from neblina import *

###################################################################################

class NebUtilities(object):

    # http://stackoverflow.com/questions/434287/what-is-the-most-pythonic-way-to-iterate-over-a-list-in-chunks
    def grouper(iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    def crc8(bytes):
        crc = 0
        for byte in bytes:
            ee = (crc) ^ (byte)
            ff = (ee) ^ (ee>>4) ^ (ee>>7)
            crc = ((ff<<1)%256) ^ ((ff<<4) % 256)
        return crc

    # Special CRC routine that skips the expected position of the CRC calculation
    # in a Neblina packet
    def genNebCRC8(packetBytes):
        crc = 0
        # The CRC should be placed as the third byte in the packet
        crc_backup = packetBytes[2]
        packetBytes[2] = 255
        ii = 0
        while ii < len(packetBytes):
           ee = (crc) ^ (packetBytes[ii])
           ff = (ee) ^ (ee>>4) ^ (ee>>7)
           crc = ((ff<<1)%256) ^ ((ff<<4) % 256)
           ii += 1
        packetBytes[2] = crc_backup
        return crc

    def saveFlashPlayback(sessionID, packetList):
        path = os.path.dirname(__file__)
        recordPath = os.path.join(path, "record/")
        if not os.path.exists(recordPath):
            os.makedirs(recordPath)

        date = time.strftime("%Y-%m-%d/")
        datePath = os.path.join(recordPath, date)
        if not os.path.exists(datePath):
            os.makedirs(datePath)

        sessionPath = os.path.join(datePath, "Session-{0}/".format(sessionID))
        if not os.path.exists(sessionPath):
            os.makedirs(sessionPath)

        os.listdir(sessionPath)
        indexPath = None
        count = 0
        while(True):
            indexPath = os.path.join(sessionPath, "{0}/".format(count))
            if not os.path.exists(indexPath):
                break
            count += 1

        os.makedirs(indexPath)

        size = (Commands.Motion.MotionCount+1)
        filepath = [0]*size
        filehandle = [0]*size
        filesize = [0]*size
        filesizeQuatToEuler = 0
        filehandleQuatToEuler = [0]

        filepath[0] = os.path.join(indexPath, "dump.txt")
        filepath[Commands.Motion.MAG] = os.path.join(indexPath, "mag.csv")
        filepath[Commands.Motion.IMU] = os.path.join(indexPath, "imu.csv")
        filepath[Commands.Motion.Quaternion] = os.path.join(indexPath, "quat.csv")
        filepath[Commands.Motion.EulerAngle] = os.path.join(indexPath, "euler.csv")
        filepath[Commands.Motion.ExtForce] = os.path.join(indexPath, "force.csv")
        filepath[Commands.Motion.Pedometer] = os.path.join(indexPath, "pedometer.csv")
        filepath[Commands.Motion.RotationInfo] = os.path.join(indexPath, "rotation.csv")

        for i in range(size):
            if filepath[i]:
                filehandle[i] = open(filepath[i], "a")

        for packet in packetList:
            if packet.header.subSystem != SubSystem.Motion or packet.header.packetType != PacketType.RegularResponse:
                continue

            filesize[0] += 1
            filehandle[0].write("{0}\n".format(packet.stringEncode()))

            if filehandle[packet.header.command]:
                filesize[packet.header.command] += 1
                filehandle[packet.header.command].write("{0}\n".format(packet.data.csvString()))

            if packet.header.command==Commands.Motion.Quaternion:
                a = packet.data.quaternions[0]/32768;
                b = packet.data.quaternions[1]/32768;
                c = packet.data.quaternions[2]/32768;
                d = packet.data.quaternions[3]/32768;
                timestamp = packet.data.timestamp
                roll = math.atan2(2*(a*b+c*d), 1-2*(b*b+c*c))
                pitch = math.asin(2*(a*c-b*d))
                yaw = math.atan2(2*(a*d+b*c), 1-2*(d*d+c*c))
                filesizeQuatToEuler += 1
                if filesizeQuatToEuler==1:
                    filehandleQuatToEuler = open(os.path.join(indexPath, "QuatToEuler.csv"), "a")
                filehandleQuatToEuler.write("{0},{1},{2},{3}\n".format(timestamp,yaw,pitch,roll))

        for i in range(size):
            if filepath[i]:
                filehandle[i].close()

        for i in range(size):
            if filesize[i]==0 and filepath[i]:
                os.remove(filepath[i])



