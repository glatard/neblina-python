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

        dumppath = os.path.join(indexPath, "dump.txt")
        magpath = os.path.join(indexPath, "mag.csv")
        imupath = os.path.join(indexPath, "imu.csv")
        quatpath = os.path.join(indexPath, "quat.csv")
        eulerpath = os.path.join(indexPath, "euler.csv")
        forcepath = os.path.join(indexPath, "force.csv")
        pedopath = os.path.join(indexPath, "pedometer.csv")
        rotatepath = os.path.join(indexPath, "rotation.csv")

        for packet in packetList:
            NebUtilities.appendToFile(dumppath, packet.stringEncode())

            if packet.header.command == Commands.Motion.IMU:
                NebUtilities.appendToFile(imupath, packet.data.csvString())
            elif packet.header.command == Commands.Motion.MAG:
                NebUtilities.appendToFile(magpath, packet.data.csvString())
            elif packet.header.command == Commands.Motion.Quaternion:
                NebUtilities.appendToFile(quatpath, packet.data.csvString())
            elif packet.header.command == Commands.Motion.EulerAngle:
                NebUtilities.appendToFile(eulerpath, packet.data.csvString())
            elif packet.header.command == Commands.Motion.ExtForce:
                NebUtilities.appendToFile(forcepath, packet.data.csvString())
            elif packet.header.command == Commands.Motion.Pedometer:
                NebUtilities.appendToFile(pedopath, packet.data.csvString());
            elif packet.header.command == Commands.Motion.RotationInfo:
                NebUtilities.appendToFile(rotatepath, packet.data.csvString());
            else:
                assert False

    def appendToFile(path, string):
        file = open(path, "a")
        file.write("{0}\n".format(string))
        file.close()