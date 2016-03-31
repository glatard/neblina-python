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

import logging
import time
import unittest

from neblina import *
from neblinaBLE import NeblinaBLE, NeblinaDelegate
from neblinaError import *
from neblinaResponsePacket import NebResponsePacket
from test import neblinaTestUtilities

###################################################################################


def getSuite(deviceAddress):
    BLEIntegrationTest.deviceAddress = deviceAddress
    return unittest.TestLoader().loadTestsFromTestCase(BLEIntegrationTest)

###################################################################################


class MotionStreamDelegate(NeblinaDelegate):

    def __init__(self):
        NeblinaDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        packet = None
        try:
            packet = NebResponsePacket(data)
        except KeyError as e:
            print("KeyError : " + str(e))
        except NotImplementedError as e:
            print("NotImplementedError : " + str(e))
        except CRCError as e:
            print("CRCError : " + str(e))
        except InvalidPacketFormatError as e:
            print("InvalidPacketFormatError : " + str(e))

        if packet:
            if packet.header.subSystem == SubSystem.Motion:
                if packet.header.command == Commands.Motion.EulerAngle:
                    yaw = packet.data.yaw
                    roll = packet.data.roll
                    pitch = packet.data.pitch
                    logging.info("Yaw : {0}, Pitch : {1}, Roll : {2}".format(yaw, pitch, roll))
            else:
                logging.error("Wrong subsystem.")

###################################################################################


class BLEIntegrationTest(unittest.TestCase):
    setupHasAlreadyRun = False
    deviceAddress = None

    def setUp(self):
        if not self.deviceAddress:
            logging.warn("No Device Address specified. Skipping.")
            raise unittest.SkipTest

        # Give it a break between each test
        time.sleep(2)

        self.ble = NeblinaBLE()
        self.ble.open(self.deviceAddress)
        if not self.ble.isOpened():
            self.fail("Unable to connect to BLE device.")

        self.ble.setStreamingInterface(Interface.BLE)

    def tearDown(self):
        self.ble.close(self.deviceAddress)
    #
    # def testMotionStreamEuler(self):
    #     self.ble.motionStream(Commands.Motion.EulerAngle, 100)
    #
    # def testMotionStreamIMU(self):
    #     self.ble.motionStream(Commands.Motion.IMU, 100)
    #
    # def testMotionStreamMAG(self):
    #     self.ble.motionStream(Commands.Motion.MAG, 100)
    #
    # def testMotionStreamQuaternion(self):
    #     self.ble.motionStream(Commands.Motion.Quaternion, 100)
    #
    def testMotionStreamEulerDelegate(self):
        self.ble.setDelegate(self.deviceAddress, MotionStreamDelegate())
        self.ble.motionStreamWithDelegate(Commands.Motion.EulerAngle, 100)

    # def testVersion(self):
    #     versions = self.ble.debugFWVersions()
    #     logging.info(versions)
    #     self.assertEqual(versions.apiRelease, 1)
    #     for i in range(0, 2):
    #         self.assertNotEqual(versions.bleFWVersion[i], 255)
    #         self.assertNotEqual(versions.mcuFWVersion[i], 255)
    #
    # def testMEMSComm(self):
    #     logging.debug('Checking communication with the LSM9DS1 chip by getting the temperature...')
    #     temp = self.ble.getTemperature()
    #     logging.info("Board Temperature: {0} degrees (Celsius)".format(temp))
    #
    # def testPMICComm(self):
    #     batteryLevel = self.ble.getBatteryLevel()
    #     logging.info("Board Battery: {0}\%".format(batteryLevel))
    #
    # def testLEDs(self):
    #     for i in range(0, 10):
    #         for j in range(0, 2):
    #             self.ble.setLED(j, 1)
    #             time.sleep(0.1)
    #             #self.assertEqual(1, self.uart.getLED(i))
    #         for j in range(0, 2):
    #             self.ble.setLED(j, 0)
    #             time.sleep(0.1)
    #             #self.assertEqual(0, self.uart.getLED(i))
    #     for i in range(0, 10):
    #         self.ble.setLEDs(([0, 1], [1, 1]))
    #         time.sleep(0.1)
    #         #self.assertEqual(1, self.uart.getLED(0))
    #         #self.assertEqual(1, self.uart.getLED(1))
    #         self.ble.setLEDs(([0, 0], [1, 0]))
    #         time.sleep(0.1)
    #         #self.assertEqual(0, self.uart.getLED(0))
    #         #self.assertEqual(0, self.uart.getLED(1))
    #
    # def testEEPROM(self):
    #     # Verify EEPROM Read/Write limit
    #     with self.assertRaises(AssertionError):
    #         self.ble.EEPROMRead(-1)
    #         self.ble.EEPROMRead(256)
    #         self.ble.EEPROMWrite(-1, "0xFF")
    #         self.ble.EEPROMWrite(256, "0xFF")
    #
    #     # Test Write/Read. Make sure to store current bytes for each page and rewrite it after test.
    #     for i in range(0, 256):
    #         storeBytes = self.ble.EEPROMRead(i)
    #         dataBytes = bytes([i, i, i, i, i, i, i, i])
    #         self.ble.EEPROMWrite(i, dataBytes)
    #         time.sleep(1)
    #         dataBytes = self.ble.EEPROMRead(i)
    #         for j in range(0, 8):
    #             self.assertEqual(dataBytes[j], i)
    #         self.ble.EEPROMWrite(i, storeBytes)
    #         logging.info("Got \'{0}\' at page #{1}".format(dataBytes, i))
    #
    # def testMotionDownsample(self):
    #     numPacket = 2
    #     for i in range(1, 51):
    #         factor = i * 20
    #         logging.info("Downsample factor : {0}".format(factor))
    #         self.ble.motionSetDownsample(factor)
    #         start = time.time()
    #         self.ble.motionStream(Commands.Motion.EulerAngle, numPacket)
    #         end = time.time()
    #         self.ble.motionStopStreams()
    #         duration = end - start
    #         logging.info("Downsample factor {0} took {1} seconds".format(factor, duration))
    #         desiredDuration = 1/(1000/factor)*numPacket
    #         #self.assertAlmostEqual(duration, desiredDuration, delta=0.02)
    #         time.sleep(0.1)
    #
    #     with self.assertRaises(AssertionError):
    #         self.ble.motionSetDownsample(1)
    #         self.ble.motionSetDownsample(1001)
    #     self.ble.motionSetDownsample(20)  # Reset to default
    #
    # def testMotionAccRange(self):
    #     with self.assertRaises(AssertionError):
    #         self.ble.motionSetAccFullScale(-1)
    #         self.ble.motionSetAccFullScale(17)
    #     self.ble.motionSetAccFullScale(2)
    #     self.ble.motionSetAccFullScale(4)
    #     self.ble.motionSetAccFullScale(8)
    #     self.ble.motionSetAccFullScale(16)
    #     self.ble.motionSetAccFullScale(8)   # Reset to default
    #
    # def testMotionState(self):
    #     self.ble.motionStopStreams()
    #     motionState = self.ble.motionGetStates()
    #     self.assertFalse(motionState.distance)
    #     self.assertFalse(motionState.force)
    #     self.assertFalse(motionState.euler)
    #     self.assertFalse(motionState.quaternion)
    #     self.assertFalse(motionState.imuData)
    #     self.assertFalse(motionState.motion)
    #     self.assertFalse(motionState.steps)
    #     self.assertFalse(motionState.magData)
    #     self.assertFalse(motionState.sitStand)
