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

from test.integration.baseIntegrationTest import BaseIntegrationTest
from neblina import *
from neblinaAPI import NeblinaAPI

###################################################################################


def getSuite(deviceAddress):
    BLEIntegrationTest.deviceAddress = deviceAddress
    return unittest.TestLoader().loadTestsFromTestCase(BLEIntegrationTest)

###################################################################################


class BLEIntegrationTest(BaseIntegrationTest):
    setupHasAlreadyRun = False
    deviceAddress = None

    def setUp(self):
        if not self.deviceAddress:
            logging.warn("No Device Address specified. Skipping.")
            raise unittest.SkipTest

        # Give it a break between each test
        time.sleep(2)

        self.api = NeblinaAPI(Interface.BLE)
        self.api.open(self.deviceAddress)
        if not self.api.isOpened():
            self.fail("Unable to connect to BLE device.")
        self.api.streamDisableAll()
        self.api.sessionRecord(False)
        self.api.setDataPortState(Interface.BLE, True)

    def tearDown(self):
        self.api.streamDisableAll()
        self.api.sessionRecord(False)
        self.api.close()
    #
    # def testStreamExtreme(self):
    #     self.ble.eraseStorage()
    #
    #     streamToUse = 10
    #
    #     self.ble.disableStreaming()
    #     self.ble.motionSetDownsample(40)
    #     self.streamIfRequired(1,  Commands.Motion.IMU, streamToUse)
    #     self.streamIfRequired(2,  Commands.Motion.MAG, streamToUse)
    #     self.streamIfRequired(3,  Commands.Motion.Quaternion, streamToUse)
    #     self.streamIfRequired(4,  Commands.Motion.EulerAngle, streamToUse)
    #     self.streamIfRequired(5,  Commands.Motion.ExtForce, streamToUse)
    #     self.streamIfRequired(6,  Commands.Motion.Pedometer, streamToUse)
    #     self.streamIfRequired(7,  Commands.Motion.SittingStanding, streamToUse)
    #     self.streamIfRequired(8,  Commands.Motion.FingerGesture, streamToUse)
    #     self.streamIfRequired(9,  Commands.Motion.RotationInfo, streamToUse)
    #     self.streamIfRequired(10, Commands.Motion.MotionState, streamToUse)
    #     self.ble.flashRecordStart()
    #
    #     count = 0
    #     while count < 100:
    #         self.ble.receivePacket()
    #         count = count + 1
    #
    #     self.ble.flashRecordStop()
    #     self.ble.disableStreaming()
    #
    #     num = self.ble.getSessionCount()
    #     self.assertEqual(num, 1)
    #
    #     packet = self.ble.getSessionInfo(0)
    #     self.assertGreater(packet.sessionLength, 0)
    #
    # def streamIfRequired(self, id, streamingType, streamToUse):
    #     (lambda: None, lambda: self.ble.motionStartStream(streamingType))[streamToUse >= id]()
