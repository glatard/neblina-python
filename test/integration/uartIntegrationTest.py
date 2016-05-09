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
from neblinaAPIBase import NeblinaAPIBase
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

    def tearDown(self):
        self.uart.close()

    def testMotionStreamEuler(self):
        self.uart.motionStream(Commands.Motion.EulerAngle, 100)

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
    # def testLEDs(self):
    #     for i in range(0, 10):
    #         for j in range(0, 2):
    #             self.uart.setLED(j, 1)
    #             time.sleep(0.1)
    #         for j in range(0, 2):
    #             self.uart.setLED(j, 0)
    #             time.sleep(0.1)
    #     for i in range(0, 10):
    #         self.uart.setLEDs(([0, 1], [1, 1]))
    #         time.sleep(0.1)
    #         self.uart.setLEDs(([0, 0], [1, 0]))
    #         time.sleep(0.1)
    #
    # def testEEPROM(self):
    #     # Verify EEPROM Read/Write limit
    #     with self.assertRaises(AssertionError):
    #         self.uart.EEPROMRead(-1)
    #         self.uart.EEPROMRead(256)
    #         self.uart.EEPROMWrite(-1, "0xFF")
    #         self.uart.EEPROMWrite(256, "0xFF")
    #
    #     # Test Write/Read. Make sure to store current bytes for each page and rewrite it after test.
    #     for i in range(0, 256):
    #         storeBytes = self.uart.EEPROMRead(i)
    #         dataBytes = bytes([i, i, i, i, i, i, i, i])
    #         self.uart.EEPROMWrite(i, dataBytes)
    #         time.sleep(0.01)
    #         dataBytes = self.uart.EEPROMRead(i)
    #         for j in range(0, 8):
    #             self.assertEqual(dataBytes[j], i)
    #         self.uart.EEPROMWrite(i, storeBytes)
    #         #logging.info("Got \'{0}\' at page #{1}".format(dataBytes, i))
    #
    # def testMotionDownsample(self):
    #     numPacket = 1
    #     for i in range(1, 51):
    #         factor = i * 20
    #         logging.info("Downsample factor : {0}".format(factor))
    #         self.uart.motionSetDownsample(factor)
    #         start = time.time()
    #         self.uart.motionStream(Commands.Motion.IMU, numPacket)
    #         end = time.time()
    #         self.uart.motionStopStreams()
    #         duration = end - start
    #         logging.info("Downsample factor {0} took {1} seconds".format(factor, duration))
    #         desiredDuration = 1/(1000/factor)*numPacket
    #         self.assertAlmostEqual(duration, desiredDuration, delta=0.02)
    #
    #     with self.assertRaises(AssertionError):
    #         self.uart.motionSetDownsample(1)
    #         self.uart.motionSetDownsample(1001)
    #     self.uart.motionSetDownsample(20)  # Reset to default
    #
    # def testMotionAccRange(self):
    #     with self.assertRaises(AssertionError):
    #         self.uart.motionSetAccFullScale(-1)
    #         self.uart.motionSetAccFullScale(17)
    #     self.uart.motionSetAccFullScale(2)
    #     self.uart.motionSetAccFullScale(4)
    #     self.uart.motionSetAccFullScale(8)
    #     self.uart.motionSetAccFullScale(16)
    #     self.uart.motionSetAccFullScale(8)   # Reset to default
    #
    # def testMotionState(self):
    #     self.uart.motionStopStreams()
    #     motionState = self.uart.motionGetStates()
    #     self.assertFalse(motionState.distance)
    #     self.assertFalse(motionState.force)
    #     self.assertFalse(motionState.euler)
    #     self.assertFalse(motionState.quaternion)
    #     self.assertFalse(motionState.imuData)
    #     self.assertFalse(motionState.motion)
    #     self.assertFalse(motionState.steps)
    #     self.assertFalse(motionState.magData)
    #     self.assertFalse(motionState.sitStand)
    #
    # def testFlashErase(self):
    #     self.uart.flashErase()
    #     num = self.uart.flashGetSessions()
    #     self.assertEqual(num, 0)
    #
    # def testFlashRecord(self):
    #     self.uart.flashRecord(198, Commands.Motion.Quaternion)
    #     time.sleep(1)
    #
    #     self.uart.flashRecord(199, Commands.Motion.IMU)
    #     time.sleep(1)
    #
    #     self.uart.flashRecord(200, Commands.Motion.MAG)
    #     time.sleep(1)
    #
    #     self.uart.flashRecord(201, Commands.Motion.MAG)
    #     time.sleep(1)
    #
    # def testFlashSessionInfo(self):
    #     packet = self.uart.flashGetSessionInfo(0)
    #     self.assertEqual(packet.sessionLength, 198)
    #
    #     packet = self.uart.flashGetSessionInfo(1)
    #     self.assertEqual(packet.sessionLength, 199)
    #
    #     packet = self.uart.flashGetSessionInfo(2)
    #     self.assertEqual(packet.sessionLength, 200)
    #
    #     packet = self.uart.flashGetSessionInfo(3)
    #     self.assertEqual(packet.sessionLength, 201)
    #
    # def testFlashSessionPlayback(self):
    #     num = self.uart.flashPlayback(0)
    #     self.assertEqual(num, 198)
    #
    #     num = self.uart.flashPlayback(1)
    #     self.assertEqual(num, 199)
    #
    #     num = self.uart.flashPlayback(2)
    #     self.assertEqual(num, 200)
    #
    #     num = self.uart.flashPlayback(3)
    #     self.assertEqual(num, 201)

    # def testFlashXtreme(self):
    #     first = 100
    #     second = 932000
    #
    #     self.uart.flashErase(Erase.Mass)
    #     self.uart.flashRecord(first, Commands.Motion.Quaternion)
    #     self.uart.flashRecord(second, Commands.Motion.IMU)
    #
    #     num = self.uart.flashGetSessions()
    #     self.assertEqual(num, 2)
    #
    #     num = self.uart.flashPlayback(0)
    #     self.assertEqual(num, first)
    #     num = self.uart.flashPlayback(1)
    #     self.assertEqual(num, second)
    #
    #     packet = self.uart.flashGetSessionInfo(0)
    #     self.assertEqual(packet.sessionLength, first)
    #     packet = self.uart.flashGetSessionInfo(1)
    #     self.assertEqual(packet.sessionLength, second)

