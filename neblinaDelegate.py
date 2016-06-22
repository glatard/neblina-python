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

###################################################################################


class NeblinaDelegate(object):

    def __init__(self):
        pass

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