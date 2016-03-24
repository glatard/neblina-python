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
import serial
import serial.tools.list_ports
import time
import csv
import array
import logging

from neblina import *
from neblinaUART import NeblinaUART
from test import neblinaTestUtilities

###################################################################################


def getSuite(comPort):
    UARTIntegrationTest.comPort = comPort
    return unittest.TestLoader().loadTestsFromTestCase(UARTIntegrationTest)

###################################################################################


class UARTIntegrationTest(unittest.TestCase):
    setupHasAlreadyRun = False
    comPort = None

    def setUp(self):
        if not self.comPort:
            raise unittest.SkipTest("No COM port specified.")

        # Give it a break between each test
        time.sleep(1)

        self.uart = NeblinaUART()
        self.uart.open(self.comPort)
        if not self.uart.isOpened(self.comPort):
            self.fail("Unable to connect to COM port.")

        self.uart.setStreamingInterface(Interface.UART)
        self.uart.stopAllStreams()

    def tearDown(self):
        self.uart.close()

    # def testMotionStreamEuler(self):
    #     self.uart.motionStream(Commands.Motion.EulerAngle, 100)
    #
    # def testMotionStreamIMU(self):
    #     self.uart.motionStream(Commands.Motion.IMU, 100)
    #
    # def testMotionStreamMAG(self):
    #     self.uart.motionStream(Commands.Motion.MAG, 100)
    #
    # def testMotionStreamQuaternion(self):
    #     self.uart.motionStream(Commands.Motion.Quaternion, 100)
    #
    # def testVersion(self):
    #     versions = self.uart.debugFWVersions()
    #     logging.info(versions)
    #     self.assertEqual(versions.apiRelease, 1)
    #     for i in range(0, 2):
    #         self.assertNotEqual(versions.bleFWVersion[i], 255)
    #         self.assertNotEqual(versions.mcuFWVersion[i], 255)
    #
    # def testMEMSComm(self):
    #     logging.debug('Checking communication with the LSM9DS1 chip by getting the temperature...')
    #     temp = self.uart.getTemperature()
    #     logging.info("Board Temperature: {0} degrees (Celsius)".format(temp))
    #
    # def testPMICComm(self):
    #     batteryLevel = self.uart.getBatteryLevel()
    #     logging.info("Board Battery: {0}\%".format(batteryLevel))
    #
    #
    # def testMotionEngine(self):
    #     testInputVectorPacketList = neblinaTestUtilities.csvVectorsToList('motEngineInputs.csv')
    #     testOutputVectorPacketList = neblinaTestUtilities.csvVectorsToList('motEngineOutputs.csv')
    #     self.uart.debugUnitTestEnable(True)
    #     for idx,packetBytes in enumerate(testInputVectorPacketList):
    #         # logging.debug('Sending {0} to stream'.format(binascii.hexlify(packetBytes)))
    #         packet = self.uart.debugUnitTestSendBytes(packetBytes)
    #         # self.api.comslip.sendPacketToStream(self.api.sc, packetBytes)
    #         # packet = self.api.waitForPacket(PacketType.RegularResponse, \
    #         #                                 SubSystem.Debug, Commands.Debug.UnitTestMotionData)
    #         self.assertEqual(testOutputVectorPacketList[idx], packet.stringEncode())
    #         print("Sent %d testVectors out of %d\r" % (idx+1, len(testInputVectorPacketList)), end="", flush=True)
    #     print("\r")
    #     self.uart.debugUnitTestEnable(False)
    #
    def testLEDs(self):
        for i in range(0, 10):
            self.uart.setLED(i, 1)
            self.assertEqual(1, self.uart.getLED(i))
        time.sleep(1)
        for i in range(0, 10):
            self.uart.setLED(i, 0)
            #self.assertEqual(0, self.api.getLED(i))