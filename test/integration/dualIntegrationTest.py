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

import unittest
import time

from neblina import *
from neblinaBLE import NeblinaBLE
from neblinaUART import NeblinaUART
import neblinaTestUtilities

###################################################################################


def getSuite(comPort, deviceAddress):
    DUALIntegrationTest.comPort = comPort
    DUALIntegrationTest.deviceAddress = deviceAddress
    return unittest.TestLoader().loadTestsFromTestCase(DUALIntegrationTest)

###################################################################################


class DUALIntegrationTest(unittest.TestCase):
    comPort = None
    deviceAddress = None

    def setUp(self):
        if not self.comPort:
            raise unittest.SkipTest("No COM port specified.")
        if not self.deviceAddress:
            raise unittest.SkipTest("No device address specified.")

        # Give it a break between each test
        time.sleep(1)

        self.uart = NeblinaUART()
        self.ble = NeblinaBLE()

    def tearDown(self):
        pass

    def connectBLE(self):
        self.ble.open(self.deviceAddress)
        if not self.ble.isOpened():
            self.fail("Unable to connect to BLE device.")
        self.ble.setStreamingInterface(Interface.BLE)

    def disconnectBLE(self):
        self.ble.motionStopStreams()
        self.ble.close(self.deviceAddress)

    def connectUART(self):
        self.uart.open(self.comPort)
        if not self.uart.isOpened(self.comPort):
            self.fail("Unable to connect to COM port.")
        self.uart.setStreamingInterface(Interface.UART)

    def disconnectUART(self):
        self.uart.motionStopStreams()
        self.uart.close()

    def testFlashPlaybackDump(self):
        self.connectBLE()
        self.ble.flashErase()
        self.ble.motionSetDownsample(40)
        self.ble.motionStartStreams(Commands.Motion.IMU)
        self.ble.motionStartStreams(Commands.Motion.MAG)
        self.ble.motionStartStreams(Commands.Motion.Quaternion)
        self.ble.motionStartStreams(Commands.Motion.EulerAngle)
        self.ble.motionStartStreams(Commands.Motion.ExtForce)
        self.ble.flashRecordStart()

        count = 0
        while count < 200:
            self.ble.receivePacket()
            count += 1

        self.ble.flashRecordStop()
        self.ble.motionStopStreams()
        self.disconnectBLE()

        time.sleep(1)

        self.connectUART()
        self.uart.flashPlayback(0, True)
        self.disconnectUART()