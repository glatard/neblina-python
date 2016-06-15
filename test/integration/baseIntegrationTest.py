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
import logging

from neblinaDelegate import NeblinaDelegate

###################################################################################


class TestDelegate(NeblinaDelegate):
    def handleEulerAngle(self, data):
        logging.debug("Euler Angle: {0}".format(data))

    def handleExternalForce(self, data):
        logging.debug("External Force: {0}".format(data))

    def handleFingerGesture(self, data):
        logging.debug("Finger Gesture: {0}".format(data))

    def handleIMU(self, data):
        logging.debug("IMU: {0}".format(data))

    def handleMAG(self, data):
        logging.debug("MAG: {0}".format(data))

    def handleMotionState(self, data):
        logging.debug("Motion State: {0}".format(data))

    def handlePedometer(self, data):
        logging.debug("Pedometer: {0}".format(data))

    def handleQuaternion(self, data):
        logging.debug("Quaternion: {0}".format(data))

    def handleRotationInfo(self, data):
        logging.debug("Rotation Info: {0}".format(data))

    def handleSittingStanding(self, data):
        logging.debug("Sitting Standing: {0}".format(data))

    def handleTrajectoryInfo(self, data):
        logging.debug("Trajectory Info: {0}".format(data))


###################################################################################


class BaseIntegrationTest(unittest.TestCase):
    setupHasAlreadyRun = False
    comPort = None
    api = None

    def testMotionStreamEulerAngle(self):
        self.api.setDelegate(TestDelegate())
        self.api.streamEulerAngle(True)
        for i in range(1, 50):
            self.api.getEulerAngle()
        self.api.streamEulerAngle(False)

    def testMotionStreamExternalForce(self):
        self.api.streamExternalForce(True)
        for i in range(1, 50):
            self.api.getExternalForce()
        self.api.streamExternalForce(False)

    def testMotionStreamIMU(self):
        self.api.streamIMU(True)
        for i in range(1, 50):
            self.api.getIMU()
        self.api.streamIMU(False)

    def testMotionStreamMAG(self):
        self.api.streamMAG(True)
        for i in range(1, 50):
            self.api.getMAG()
        self.api.streamMAG(False)

    def testMotionStreamQuaternion(self):
        self.api.streamQuaternion(True)
        for i in range(1, 50):
            self.api.getQuaternion()
        self.api.streamQuaternion(False)

    # def testVersion(self):
    #     versions = self.api.getFirmwareVersion()
    #     logging.info(versions)
    #     self.assertEqual(versions.apiRelease, 1)
    #     for i in range(0, 2):
    #         self.assertNotEqual(versions.bleFWVersion[i], 255)
    #         self.assertNotEqual(versions.mcuFWVersion[i], 255)
    #
    # def testMEMSComm(self):
    #     logging.debug('Checking communication with the LSM9DS1 chip by getting the temperature...')
    #     temp = self.api.getTemperature()
    #     logging.info("Board Temperature: {0} degrees (Celsius)".format(temp))
    #
    # def testPMICComm(self):
    #     batteryLevel = self.api.getBatteryLevel()
    #     logging.info("Board Battery: {0}\%".format(batteryLevel))
    #
    # def testLEDs(self):
    #     self.api.setLED(0, 1)
    #     self.api.getLED(0)
    #     with self.assertRaises(AssertionError):
    #         self.api.getLED(-1)
    #         self.api.getLED(8)
    #         self.api.setLED(-1, 1)
    #         self.api.setLED(8, 1)

    # def testEEPROM(self):
    #     # Verify EEPROM Read/Write limit
    #     with self.assertRaises(AssertionError):
    #         self.api.eepromRead(-1)
    #         self.api.eepromRead(256)
    #         self.api.eepromWrite(-1, "0xFF")
    #         self.api.eepromWrite(256, "0xFF")
    #
    #     # Test Write/Read. Make sure to store current bytes for each page and rewrite it after test.
    #     num = 256
    #     storeBytes = []
    #     # Store EEPROM state
    #     for i in range(0, num):
    #         dataBytes = self.api.eepromRead(i)
    #         storeBytes.append(dataBytes)
    #         logging.debug("EEPROMRead store {0}: {1}".format(i, dataBytes))
    #     # Test write/read
    #     for i in range(0, num):
    #         dataBytes = bytes([i, i, i, i, i, i, i, i])
    #         logging.debug("EEPROMWrite {0} : {1}".format(i, dataBytes))
    #         self.api.eepromWrite(i, dataBytes)
    #     for i in range(0, num):
    #         dataBytes = self.api.eepromRead(i)
    #         logging.debug("EEPROMRead {0} : {1}".format(i, dataBytes))
    #         for j in range(0, 8):
    #             self.assertEqual(dataBytes[j], i)
    #     for i in range(0, num):
    #         logging.debug("EEPROMWrite store {0} : {1}".format(i, storeBytes[i]))
    #         self.api.eepromWrite(i, storeBytes[i])
    #     for i in range(0, num):
    #         dataBytes = self.api.eepromRead(i)
    #         logging.debug("EEPROMRead store {0} : {1}".format(i, dataBytes))
    #         self.assertTrue(dataBytes == storeBytes[i])
    #
    # def testMotionDownsample(self):
    #     numPacket = 1
    #     for i in range(1, 51):
    #         factor = i * 20
    #         logging.info("Downsample factor : {0}".format(factor))
    #         self.api.setDownsample(factor)
    #         self.api.streamIMU(True)
    #         dummy = self.api.getIMU().timestamp
    #         first = self.api.getIMU().timestamp
    #         second = self.api.getIMU().timestamp
    #         self.api.streamIMU(False)
    #         diff = second - first
    #         logging.info("Downsample factor {0} took {1} us".format(factor, diff))
    #         desiredDuration = 1000 * factor
    #         self.assertAlmostEqual(diff, desiredDuration, delta=1000)
    #
    #     with self.assertRaises(AssertionError):
    #         self.api.setDownsample(1)
    #         self.api.setDownsample(1001)
    #     self.api.setDownsample(20)  # Reset to default
    #
    # def testMotionAccRange(self):
    #     with self.assertRaises(AssertionError):
    #         self.api.setAccelerometerRange(-1)
    #         self.api.setAccelerometerRange(17)
    #     self.api.setAccelerometerRange(2)
    #     self.api.setAccelerometerRange(4)
    #     self.api.setAccelerometerRange(8)
    #     self.api.setAccelerometerRange(16)
    #     self.api.setAccelerometerRange(8)   # Reset to default
    #
    # def testMotionStatus(self):
    #     motionStatus = self.api.getMotionStatus()
    #     self.assertFalse(motionStatus.distance)
    #     self.assertFalse(motionStatus.force)
    #     self.assertFalse(motionStatus.euler)
    #     self.assertFalse(motionStatus.quaternion)
    #     self.assertFalse(motionStatus.imuData)
    #     self.assertFalse(motionStatus.motion)
    #     self.assertFalse(motionStatus.steps)
    #     self.assertFalse(motionStatus.magData)
    #     self.assertFalse(motionStatus.sitStand)
    #
    # def testRecorderStatus(self):
    #     recorderStatus = self.api.getRecorderStatus()
    #     self.assertEqual(recorderStatus.status, 0)
    #
    # def testFlashErase(self):
    #     self.api.eraseStorage()
    #     num = self.api.getSessionCount()
    #     self.assertEqual(num, 0)
    #
    # def testFlashRecord(self):
    #     self.api.sessionRecord(True)
    #     self.api.streamQuaternion(True)
    #     self.api.getQuaternion()
    #     self.api.streamQuaternion(False)
    #     self.api.sessionRecord(False)
    #
    # def testFlashSessionInfo(self):
    #     self.api.getSessionInfo(0)
    #
    # def testFlashSessionPlayback(self):
    #     self.api.sessionPlayback(0)

