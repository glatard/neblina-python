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

import binascii
import struct

from neblina import *
from neblinaUtilities import NebUtilities as nebUtilities

###################################################################################


class AckData(object):

    def __init__(self):
        pass

    def __str__(self):
        return "Acknowledgment"


###################################################################################


class BlankData(object):
    """ This object is for packet data
        containing no meaningful info in it.
    """
    def __init__(self, dataString):
        if len(dataString) > 0:
            self.blankBytes = struct.unpack(Formatting.Data.Blank, dataString)
        else:
            self.blankBytes = ('\000'*17).encode('utf-8')

    def __str__(self):
        return '{0}'.format(self.blankBytes)

    def encode(self):
        garbage = ('\000'*17).encode('utf-8')
        return struct.pack(Formatting.Data.Blank, garbage)

###################################################################################


class MotionStatusData(object):
    def __init__(self, distance=False, force=False, euler=False, quaternion=False, imu=False,
                 motion=False, steps=False, mag=False, sitStand=False):
        self.distance = distance
        self.force = force
        self.euler = euler
        self.quaternion = quaternion
        self.imu = imu
        self.motion = motion
        self.steps = steps
        self.mag = mag
        self.sitStand = sitStand

    def __str__(self):
        return "Distance: {0}, Force:{1}, Euler:{2}, Quaternion:{3}, IMUData:{4}, Motion:{5}, Steps:{6}, MAGData:{7}, SitStand:{8}"\
        .format(self.distance, self.force, self.euler, self.quaternion,\
                self.imuData, self.motion, self.steps, self.magData,\
                self.sitStand)

###################################################################################


class RecorderStatusData(object):
    recorderStatusStrings = {
        0:"Off",
        1:"Recording",
        2:"Playback",
    }

    def __init__(self, status=0):
        self.status = 0

    def __str__(self):
        return "RecorderStatus:{0}"\
            .format(RecorderStatusData.recorderStatusStrings[self.status])

###################################################################################


class MotAndFlashRecStateData(object):
    """ Neblina motion and flash recording state

        Formatting:
        - Timestamp (unused for now)
    """

    recorderStatusStrings = {
        0:"Off",
        1:"Recording",
        2:"Playback",
    }

    def __init__(self, dataString):
        self.motionStatus = MotionStatusData()
        self.recorderStatus = RecorderStatusData()

        self.timestamp, \
        motionEngineStatusBytes,\
        self.recorderStatus.status,\
        garbage = struct.unpack(Formatting.Data.MotionAndFlash, dataString)

        # Extract motion engine state
        self.motionStatus = MotionStatusData()
        self.motionStatus.distance = ((motionEngineStatusBytes[0] & 0x01) == 1)
        self.motionStatus.force = (((motionEngineStatusBytes[0] & 0x02) >> 1) == 1)
        self.motionStatus.euler = (((motionEngineStatusBytes[0] & 0x04) >> 2) == 1)
        self.motionStatus.quaternion = (((motionEngineStatusBytes[0] & 0x08) >> 3) == 1)
        self.motionStatus.imuData = (((motionEngineStatusBytes[0] & 0x10) >> 4) == 1)
        self.motionStatus.motion = (((motionEngineStatusBytes[0] & 0x20) >> 5) == 1)
        self.motionStatus.steps = (((motionEngineStatusBytes[0] & 0x40) >> 6) == 1)
        self.motionStatus.magData = (((motionEngineStatusBytes[0] & 0x80) >> 7) == 1)
        self.motionStatus.sitStand = ((motionEngineStatusBytes[1] & 0x01) == 1)

    def __str__(self):
        return "{0}. {1}"\
            .format(self.motionStatus, self.recorderStatus)

###################################################################################


class EEPROMReadData(object):
    """ Neblina EEPROM read data

        Formatting:
        - Page number
        - 8 bytes R/W data
    """
    def __init__(self, dataString):
        self.pageNumber, \
        self.dataBytes  = struct.unpack(Formatting.Data.EEPROMRead, dataString)

    def __str__(self):
        return "Page# {0} Data Bytes:{1} ".format(self.pageNumber, self.dataBytes)

###################################################################################


class LEDGetValData(object):
    """ Neblina LED retrieval data

        Formatting:
        - Number of LEDs (defines the number of index/value pair to be use)
        - LED Index (one for each LEDs)
        - LED Value (one for each LEDs)
    """
    def __init__(self, dataString):
        self.ledState = [0]*8
        self.ledState[0], self.ledState[1], self.ledState[2], \
        self.ledState[3], self.ledState[4], self.ledState[5], self.ledState[6], \
        self.ledState[7] = struct.unpack(Formatting.Data.LEDGetVal, dataString)

    def __str__(self):
        return "LED Values: {0}".format(self.ledState)

###################################################################################


class BatteryLevelData(object):
    """ Neblina battery level data

        Formatting:
        - Battery level (%)
    """
    def __init__(self, dataString):
        # timestamp = 0
        # timestamp, \
        self.batteryLevel = struct.unpack(Formatting.Data.BatteryLevel, dataString)
        self.batteryLevel = self.batteryLevel[0]/10

    def __str__(self):
        return "batteryLevel: {0}%".format(self.batteryLevel)

###################################################################################


class TemperatureData(object):
    """ Neblina temperature data

        Formatting:
        - Temperature in Celsius (x100)
    """
    def __init__(self, dataString):
        # timestamp = 0
        # self.timestamp, \
        self.temperature = struct.unpack(Formatting.Data.Temperature, dataString)
        self.temperature = self.temperature[0]/100

    def __str__(self):
        return "Temperature: {0}".format(self.temperature)

    def encode(self):
        # garbage = ('\000'*10).encode('utf-8')
        packetString = struct.pack(Formatting.Data.Temperature, self.temperature)
        # return packetString('utf-8')
        return packetString

###################################################################################


class FlashSessionData(object):
    """ Neblina flash session data

        Formatting:
        - Open/Close
        - Session ID
    """
    def __init__(self, dataString):
        # timestamp,\
        openCloseByte,\
        self.sessionID = struct.unpack(Formatting.CommandData.FlashSession, dataString)
        # open = True, close = False
        self.openClose = (openCloseByte == 1)

    def __str__(self):
        openCloseString = 'open' if self.openClose else 'close'
        return "Session {0}: {1}"\
        .format(self.sessionID, openCloseString)

###################################################################################


class FlashSessionInfoData(object):
    """ Neblina flash session information data

        Formatting:
        - Timestamp
        - Session ID
    """
    def __init__(self, dataString):
        self.sessionLengthBytes,\
        self.sessionID = struct.unpack(Formatting.Data.FlashSessionInfoResponse, dataString)
        if self.sessionLengthBytes > 0:
            self.sessionLength = self.sessionLengthBytes / 18
        else:
            self.sessionLength = self.sessionLengthBytes

    def __str__(self):
        return "Session {0}: {1} bytes"\
        .format(self.sessionID, self.sessionLengthBytes)

###################################################################################


class FlashNumSessionsData(object):
    """ Neblina flash number of sessions data

        Formatting:
        - Number of sessions
    """
    def __init__(self, dataString):
        self.numSessions = struct.unpack(Formatting.Data.FlashNumSessions, dataString)

    def __str__(self):
        return "Number of sessions: {0}"\
        .format(self.numSessions)

###################################################################################


class FirmwareVersionsData(object):
    """ Neblina firmware versions data

        Formatting:
        - API release
        - MCU Major/Minor/Build
        - BLE Major/Minor/Build
        - Device ID
    """
    def __init__(self, deviceID, apiRelease, mcuFWVersion, bleFWVersion):
        assert len(mcuFWVersion)==3
        assert len(bleFWVersion)==3

        self.deviceID = deviceID
        self.apiRelease = apiRelease
        self.mcuFWVersion = mcuFWVersion
        self.bleFWVersion = bleFWVersion

    def __str__(self):
        string = "API Release: {0}\n".format(self.apiRelease)
        string += "BLE Version: {0}.{1}.{2}\n".format(self.bleFWVersion[0], self.bleFWVersion[1], self.bleFWVersion[2])
        string += "MCU Version: {0}.{1}.{2}\n".format(self.mcuFWVersion[0], self.mcuFWVersion[1], self.mcuFWVersion[2])
        string += "Device ID: {0}".format(binascii.hexlify(self.deviceID))
        return string

    @classmethod
    def decode(cls, dataString):
        mcuFWVersion = [0]*3
        bleFWVersion = [0]*3

        apiRelease,\
        mcuFWVersion[0], mcuFWVersion[1], mcuFWVersion[2],\
        bleFWVersion[0], bleFWVersion[1], bleFWVersion[2],\
        deviceID = struct.unpack(Formatting.Data.FWVersions, dataString)

        return cls(deviceID, apiRelease, mcuFWVersion, bleFWVersion)

    def encode(self):
        packetString = struct.pack(Formatting.Data.FWVersions, self.apiRelease, \
            self.mcuFWVersion[0], self.mcuFWVersion[1], self.mcuFWVersion[2],\
            self.bleFWVersion[0], self.bleFWVersion[1], self.bleFWVersion[2], self.deviceID)
        return packetString



###################################################################################

# Special 70 byte packet
# motion, imu+mag, quaternion, euler, force, error, motion track, motion track progress, timestamp, stepCount, walkingDirection, sitStand
class UnitTestMotionData(object):
    """ Neblina motion data (used for debugging and testing)

        Formatting:
        - Motion State
        - Accelerometer (x,y,z)
        - Gyroscope (x,y,z)
        - Magnetometer (x,y,z)
        - Quaternion (quat0,quat1,quat2,quat3)
        - Euler (yaw,pitch,roll)
        - External forces (x,y,z)
        - Euler angle errors (x,y,z)
        - Motion track counter
        - Motion track progress
        - Timestamp
        - Steps
        - Direction
        - Sit stand
        - Sit time
        - Stand time
    """

    motionStrings = {
        0: "No Change",
        1: "Stops Moving",
        2: "Starts Moving",
    }

    def __init__(self, dataString):
        self.accel = [0]*3
        self.gyro = [0]*3
        self.mag = [0]*3
        self.quaternions = [0]*4
        self.eulerAngleErrors = [0]*3
        self.externalForces = [0]*3
        self.startStop,\
        self.accel[0], self.accel[1], self.accel[2],\
        self.gyro[0], self.gyro[1], self.gyro[2],\
        self.mag[0], self.mag[1], self.mag[2],\
        self.quaternions[0], self.quaternions[1],\
        self.quaternions[2], self.quaternions[3],\
        self.yaw, self.pitch, self.roll,\
        self.externalForces[0],\
        self.externalForces[1],\
        self.externalForces[2],\
        self.eulerAngleErrors[0],\
        self.eulerAngleErrors[1],\
        self.eulerAngleErrors[2],\
        self.motionTrack, self.motionTrackProgress,\
        self.timestamp, self.stepCount,\
        self.walkingDirection,\
        self.sitStand, self.sitTime, self.standTime,\
        = struct.unpack(Formatting.Data.UnitTestMotion, dataString)

    def __str__(self):
        return "Motion: {0} \n\
        accelxyz:({1},{2},{3}) gyroxyz:({4},{5},{6}) \
        magxyz: ({7}, {8}, {9}),\n\
        quat0:{10} quat1:{11} quat2:{12} quat3:{13} \n\
        yaw/pitch/roll:({14},{15},{16})) \n\
        externalForces(x,y,z):({17},{18},{19}) \n\
        eulerAngleErrors(x,y,z):({20},{21},{22}) \n\
        motionTrackCounter: {24} \
        motionTrackProgress: {25} \n\
        timestamp: {26} \n\
        steps: {27} \
        direction: {28} \n\
        sitStand: {29}, sitTime:{30}, standTime:{31}"\
        .format(Formatting.Data.UnitTestMotion,\
            UnitTestMotionData.motionStrings[self.startStop],\
            self.startStop,\
            self.accel[0], self.accel[1], self.accel[2],\
            self.gyro[0], self.gyro[1], self.gyro[2],\
            self.mag[0], self.mag[1], self.mag[2],\
            self.quaternions[0], self.quaternions[1],\
            self.quaternions[2], self.quaternions[3],\
            self.yaw, self.pitch, self.roll,\
            self.externalForces[0],\
            self.externalForces[1],\
            self.externalForces[2],\
            self.eulerAngleErrors[0],\
            self.eulerAngleErrors[1],\
            self.eulerAngleErrors[2],\
            self.motionTrack, self.motionTrackProgress,\
            self.timestamp, self.stepCount,\
            self.walkingDirection,\
            self.sitStand, self.sitTime, self.standTime)

    def encode(self):
        packetBytes = struct.pack(Formatting.Data.UnitTestMotion,\
            self.startStop,\
            self.accel[0], self.accel[1], self.accel[2],\
            self.gyro[0], self.gyro[1], self.gyro[2],\
            self.mag[0], self.mag[1], self.mag[2],\
            self.quaternions[0], self.quaternions[1],\
            self.quaternions[2], self.quaternions[3],\
            self.yaw, self.pitch, self.roll,\
            self.externalForces[0],\
            self.externalForces[1],\
            self.externalForces[2],\
            self.eulerAngleErrors[0],\
            self.eulerAngleErrors[1],\
            self.eulerAngleErrors[2],\
            self.motionTrack, self.motionTrackProgress,\
            self.timestamp, self.stepCount,\
            self.walkingDirection,\
            self.sitStand, self.sitTime, self.standTime)
        return packetBytes

###################################################################################


class MotionStateData(object):
    """ Neblina motion state data

        Formatting:
        - Timestamp
        - Start/Stop
    """
    def __init__(self, dataString):
        self.timestamp,\
        startStopByte = struct.unpack(Formatting.Data.MotionState, dataString)
        self.startStop = (startStopByte == 1)

    def __str__(self):
        return "{0}us: startStop:{1}"\
        .format(self.timestamp,self.startStop)

    def encode(self):
        # garbage = ('\000'*11).encode('utf-8')
        packetString = struct.pack(Formatting.Data.MotionState, self.timestamp,\
        self.startStop)
        return packetString


###################################################################################


class RSSIData(object):
    """ Neblina RSSI data

        Formatting:
        - Timestamp
        - RSSI in dB
    """
    def __init__(self, dataString):
        self.timestamp,\
        self.RSSI,\
        garbage = struct.unpack(Formatting.Data.MotionState, dataString)

    def __str__(self):
        return "{0}us: RSSI:{1}"\
        .format(self.timestamp,self.RSSI-256)

    def encode(self):
        garbage = ('\000'*11).encode('utf-8')
        packetString = struct.pack(Formatting.Data.RSSI, self.timestamp,\
        self.RSSI, garbage)
        return packetString


###################################################################################


class ExternalForceData(object):
    """ Neblina external force data

        Formatting:
        - Timestamp
        - External forces (x,y,z)
    """
    def __init__(self, dataString):
        self.externalForces = [0]*3
        self.timestamp,\
        self.externalForces[0],\
        self.externalForces[1],\
        self.externalForces[2] = struct.unpack(Formatting.Data.ExternalForce, dataString)

    def __str__(self):
        return "{0}us: externalForces(x,y,z):({1},{2},{3})"\
        .format(self.timestamp,self.externalForces[0],\
            self.externalForces[1], self.externalForces[2])

    def encode(self):
        garbage = ('\000'*6).encode('utf-8')
        packetString = struct.pack(Formatting.Data.ExternalForce, self.timestamp,\
        self.externalForces[0], self.externalForces[1], self.externalForces[2])
        return packetString

    def csvString(self):
        packetString = "{0};{1};{2};{3};".format(self.timestamp,\
            self.externalForces[0], self.externalForces[1], self.externalForces[2])
        return packetString

###################################################################################


class TrajectoryDistanceData(object):
    """ Trajectory distance data

        Formatting:
        - Timestamp
        - Euler angle errors (x,y,z)
        - Repeat count
        - Completion percentage (%)
    """
    def __init__(self, dataString):
        self.eulerAngleErrors = [0]*3
        self.timestamp,\
        self.eulerAngleErrors[0],\
        self.eulerAngleErrors[1],\
        self.eulerAngleErrors[2],\
        self.count,\
        self.progress = struct.unpack(Formatting.Data.TrajectoryDistance, dataString)

    def __str__(self):
        return "{0}us: eulerAngleErrors(yaw,pitch,roll):({1},{2},{3}), count:{4}, progress:{5}%"\
        .format(self.timestamp,self.eulerAngleErrors[0],\
            self.eulerAngleErrors[1], self.eulerAngleErrors[2], self.count, self.progress)

    def encode(self):
        # garbage = ('\000'*3).encode('utf-8')
        packetString = struct.pack(Formatting.Data.TrajectoryDistance, self.timestamp,\
        self.eulerAngleErrors[0], self.eulerAngleErrors[1], self.eulerAngleErrors[2], self.count, self.progress)
        return packetString


###################################################################################


class PedometerData(object):
    """ Neblina pedometer data

        Formatting:
        - Timestamp
        - Step count
        - Steps per minute
        - Walking direction
        - Toe-off timestamp
        - Stairs up count
        - Stairs down count
    """
    def __init__(self, dataString):
        self.timestamp,self.stepCount,\
        self.stepsPerMinute,\
        self.walkingDirection,\
        self.toeoffTimestamp,\
        self.stairsUpCount,\
        self.stairsDownCount = struct.unpack(Formatting.Data.Pedometer, dataString)
        self.walkingDirection /= 10.0


    def encode(self):
        packetString = struct.pack(Formatting.Data.Pedometer, self.timestamp,\
        self.stepCount, self.stepsPerMinute, int(self.walkingDirection*10), self.toeoffTimestamp, self.stairsUpCount, self.stairsDownCount)
        return packetString

    def __str__(self):
        return "{0}us: stepCount:{1}, stepsPerMinute:{2}, walkingDirection:{3}, toeoffTimestamp: {4}, stairsUpCount: {5}, stairsDownCount: {6}"\
        .format(self.timestamp, self.stepCount,\
        self.stepsPerMinute, self.walkingDirection, self.toeoffTimestamp, self.stairsUpCount, self.stairsDownCount)

    def csvString(self):
        packetString = "{0};{1};{2};{3};{4};{5};{6}".format(self.timestamp,\
            self.stepCount, self.stepsPerMinute, self.walkingDirection, self.toeoffTimestamp, self.stairsUpCount, self.stairsDownCount)
        return packetString

###################################################################################


class FingerGestureData(object):
    """ Neblina finger gesture data

        Formatting:
        - Timestamp
        - Swipe pattern
    """

    def __init__(self, dataString):
        self.timestamp,self.gesture = struct.unpack(Formatting.Data.FingerGesture, dataString)

    def __str__(self):
        if self.gesture==0:
            return "{0}us: Gesture:Swiped Left".format(self.timestamp)
        elif self.gesture==1:
            return "{0}us: Gesture:Swiped Right".format(self.timestamp)
        elif self.gesture==2:
            return "{0}us: Gesture:Swiped Up".format(self.timestamp)
        elif self.gesture==3:
            return "{0}us: Gesture:Swiped Down".format(self.timestamp)
        elif self.gesture==4:
            return "{0}us: Gesture:Flipped Left".format(self.timestamp)
        elif self.gesture==5:
            return "{0}us: Gesture:Flipped Right".format(self.timestamp)
        elif self.gesture==6:
            return "{0}us: Gesture:Double Tap".format(self.timestamp)
        else:
            return "{0}us: Gesture:None ".format(self.timestamp)

    def encode(self):
        # garbage = ('\000'*11).encode('utf-8')
        packetString = struct.pack(Formatting.Data.FingerGesture, self.timestamp,\
        self.gesture)
        return packetString

###################################################################################


class RotationData(object):
    """ Neblina rotation data

        Formatting:
        - Timestamp
        - Rotation count
        - Speed (RPM)
    """
    def __init__(self, dataString):
        self.timestamp,self.rotationCount,\
        self.rpm = struct.unpack(Formatting.Data.RotationInfo, dataString)
        self.rpm = self.rpm/10.0

    def __str__(self):
        return "{0}us: rotationCount:{1}, rpm:{2}"\
        .format(self.timestamp, self.rotationCount,\
        self.rpm)

    def encode(self):
        # garbage = ('\000'*6).encode('utf-8')
        packetString = struct.pack(Formatting.Data.RotationInfo, self.timestamp,\
        self.rotationCount, int(self.rpm*10))
        return packetString

    def csvString(self):
        packetString = "{0};{1};{2};".format(self.timestamp,\
        self.rotationCount, self.rpm)
        return packetString

###################################################################################


class QuaternionData(object):
    """ Neblina quaternion data

        Formatting:
        - Timestamp
        - Quaternion (quat1,quat2,quat3,quat4)
    """
    def __init__(self, dataString):
        self.quaternions = [0]*4
        self.timestamp,\
        self.quaternions[0],\
        self.quaternions[1],\
        self.quaternions[2],\
        self.quaternions[3] = struct.unpack(Formatting.Data.Quaternion, dataString)

    def encode(self):
        packetString = struct.pack(Formatting.Data.Quaternion, self.timestamp,\
        self.quaternions[0], self.quaternions[1],\
        self.quaternions[2], self.quaternions[3])
        return packetString

    def __str__(self):
        return "{0}us: quat0:{1} quat1:{2} quat2:{3} quat3:{4}".format(\
            self.timestamp, self.quaternions[0], self.quaternions[1],\
            self.quaternions[2], self.quaternions[3])

    def csvString(self):
        packetString = "{0};{1};{2};{3};{4};".format(self.timestamp,\
            self.quaternions[0], self.quaternions[1], self.quaternions[2], self.quaternions[3])
        return packetString

###################################################################################


class IMUData(object):
    """ Neblina IMU data

        Formatting:
        - Timestamp
        - Accelerometer (x,y,z)
        - Gyroscope (x,y,z)
    """
    def __init__(self, timestamp, accel, gyro):
        self.accel = [0]*3
        self.gyro = [0]*3
        assert len(accel)==3
        assert len(gyro)==3

        self.timestamp = timestamp
        self.accel[0] = int(accel[0])
        self.accel[1] = int(accel[1])
        self.accel[2] = int(accel[2])
        self.gyro[0] = int(gyro[0])
        self.gyro[1] = int(gyro[1])
        self.gyro[2] = int(gyro[2])

    def __str__(self):
        return "{0}us: accelxyz:({1},{2},{3}) gyroxyz:({4},{5},{6})"\
        .format(self.timestamp,
                self.accel[0], self.accel[1], self.accel[2],
                self.gyro[0], self.gyro[1], self.gyro[2])

    @classmethod
    def decode(cls, dataString):
        accel = [0]*3
        gyro = [0]*3

        timestamp, \
        accel[0], accel[1], accel[2],\
        gyro[0], gyro[1], gyro[2] \
        = struct.unpack(Formatting.Data.IMU, dataString)

        return cls(timestamp, accel, gyro)


    def encode(self):
        packetString = struct.pack(Formatting.Data.IMU,\
            self.timestamp, self.accel[0], self.accel[1], self.accel[2],\
            self.gyro[0], self.gyro[1], self.gyro[2])
        return packetString

    def csvString(self):
        packetString = "{0};{1};{2};{3};{4};{5};{6}".format(self.timestamp,\
            self.accel[0], self.accel[1], self.accel[2], self.gyro[0], self.gyro[1], self.gyro[2])
        return packetString

###################################################################################

class AccMAGData(object):
    """ Neblina accelerometer/magnetometer data

        Formatting:
        - Timestamp
        - Magnetometer (x,y,z)
        - Accelerometer (x,y,z)
    """
    def __init__(self, timestamp, mag, accel):
        self.mag = [0]*3
        self.accel = [0]*3
        assert len(mag) == 3
        assert len(accel) == 3

        self.timestamp = timestamp
        self.mag[0] = int(mag[0])
        self.mag[1] = int(mag[1])
        self.mag[2] = int(mag[2])
        self.accel[0] = int(accel[0])
        self.accel[1] = int(accel[1])
        self.accel[2] = int(accel[2])

    def __str__(self):
        return "{0}us: accelxyz:({1},{2},{3}) magxyz:({4},{5},{6})"\
        .format(self.timestamp,
                self.mag[0], self.mag[1], self.mag[2],
                self.accel[0], self.accel[1], self.accel[2])

    @classmethod
    def decode(cls, dataString):
        mag = [0]*3
        accel = [0]*3

        timestamp, \
        mag[0], mag[1], mag[2],\
        accel[0], accel[1], accel[2] \
        = struct.unpack(Formatting.Data.ACCMAG, dataString)

        return cls(timestamp, mag, accel)

    def encode(self):
        packetString = struct.pack(Formatting.Data.ACCMAG, \
            self.timestamp, self.mag[0], self.mag[1], self.mag[2],\
            self.accel[0], self.accel[1], self.accel[2])
        return packetString

    def csvString(self):
        packetString = "{0};{1};{2};{3};{4};{5};{6}".format(self.timestamp,\
            self.mag[0], self.mag[1], self.mag[2], self.accel[0], self.accel[1], self.accel[2])
        return packetString

###################################################################################

class MAGData(object):
    """ Neblina magnetometer data

        Formatting:
        - Timestamp
        - Magnetometer (x,y,z)
    """
    def __init__(self, timestamp, mag):
        self.mag = [0]*3
        assert len(mag) == 3

        self.timestamp = timestamp
        self.mag[0] = int(mag[0])
        self.mag[1] = int(mag[1])
        self.mag[2] = int(mag[2])

    def __str__(self):
        return "{0}us: magxyz:({1},{2},{3})"\
        .format(self.timestamp,
                self.mag[0], self.mag[1], self.mag[2])

    @classmethod
    def decode(cls, dataString):
        mag = [0]*3

        timestamp, \
        mag[0], mag[1], mag[2],\
        = struct.unpack(Formatting.Data.MAG, dataString)

        return cls(timestamp, mag)

    def encode(self):
        packetString = struct.pack(Formatting.Data.MAG, \
            self.timestamp, self.mag[0], self.mag[1], self.mag[2])
        return packetString

    def csvString(self):
        packetString = "{0};{1};{2};{3}".format(self.timestamp,\
            self.mag[0], self.mag[1], self.mag[2])
        return packetString

###################################################################################

class EulerAngleData(object):
    """ Neblina euler angle data

        Formatting:
        - Timestamp
        - Euler angle (yaw,pitch,roll)
    """
    def __init__(self, dataString):
        self.timestamp, self.yaw, self.pitch, self.roll = struct.unpack(Formatting.Data.Euler, dataString)
        self.yaw = self.yaw/10.0
        self.pitch = self.pitch/10.0
        self.roll = self.roll/10.0
        # self.demoHeading = self.demoHeading/10.0

    def encode(self):
        # garbage = ('\000'*4).encode('utf-8')
        packetString = struct.pack(Formatting.Data.Euler, self.timestamp,\
            int(self.yaw*10), int(self.pitch*10), int(self.roll*10))
        return packetString

    def __str__(self):
        return "{0}us: yaw/pitch/roll:({1},{2},{3}))".format(self.timestamp, self.yaw, self.pitch, self.roll)

    def csvString(self):
        packetString = "{0};{1};{2};{3}".format(self.timestamp,\
            self.yaw, self.pitch, self.roll)
        return packetString

###################################################################################


class DataPortStatusData(object):
    """ Neblina data port status data

        Formatting:
        - Data port ID
        - Open/Close
    """
    def __init__(self, portID, openClose):
        self.portID = portID
        self.openClose = openClose

    def __str__(self):
        return "portID: {0}, openClose: {1}" \
            .format(self.portID, self.openClose)

    @classmethod
    def decode(cls, dataString):
        portID, openClose = struct.unpack(Formatting.CommandData.SetDataPortState, dataString)
        return cls(portID, openClose)

    def encode(self):
        packetString = struct.pack(Formatting.CommandData.SetDataPortState, \
                                   self.portID, self.openClose)
        return packetString