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

from neblina import *
from neblinaCore import NeblinaCore
from neblinaData import *
from neblinaError import *
from neblinaUtilities import NebUtilities

import math
import matplotlib
import random
from numpy import *
from pylab import *
import matplotlib.pyplot as plt
import time

###################################################################################


class NeblinaAPI(object):
    """
        Neblina Application Programming Interface.

        This is used to communicate with Neblina.
    """

    def __init__(self, interface):
        """
            Constructor

            :param interface: Neblina communication interface. See Neblina.Interface.
        """
        self.core = NeblinaCore(interface)

    def close(self):
        """
            Close communication with Neblina.
        """
        self.core.close()

    def open(self, address):
        """
            Open communication with Neblina.

            :param address: Neblina address to reach. It can be UART
        """
        self.core.open(address)

    def isOpened(self):
        """
            Is communication opened ?

            :return: True, if communication opened. False, otherwise.
        """
        return self.core.isOpened()

    def getBatteryLevel(self):
        """
            Retrieve battery level.

            :return: Battery Level (0-100%)
        """
        return self.core.getBatteryLevel()

    def getTemperature(self):
        """
            Retrieve internal temperature

            :return: Temperature (in Celsius)
        """
        self.core.sendCommand(SubSystem.Power, Commands.Power.GetTemperature, True)
        packet = self.core.waitForAck(SubSystem.Power, Commands.Power.GetTemperature)
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Power, Commands.Power.GetTemperature)
        return packet.data.temperature

    def setDataPortState(self, interface, state):
        """
            Set data port state

            :param interface: Neblina.Interface to set.
            :param state: True, to open data port. False, to close data port.
        """
        assert(type(state) is bool)
        self.core.sendCommand(SubSystem.Debug, Commands.Debug.InterfaceState, state, interface=interface)
        logging.debug('Waiting for the module to set data port state...')
        packet = self.core.waitForAck(SubSystem.Debug, Commands.Debug.InterfaceState)
        logging.debug('Module has change its data port state')

    def setInterface(self, interface=Interface.BLE):
        """
            Set communication interface.

            :param interface: Neblina.Interface to used.
        """
        self.core.sendCommand(SubSystem.Debug, Commands.Debug.SetInterface, interface)
        logging.debug('Waiting for the module to switch its interface...')
        packet = self.core.waitForAck(SubSystem.Debug, Commands.Debug.SetInterface)
        logging.debug("Module has switched its interface.")
        numTries = 0
        while (packet == None):
            numTries += 1
            if numTries > 5:
                logging.error('The unit is not responding. Exiting...')
                exit()
            logging.warning('Trying again...')
            self.core.sendCommand(SubSystem.Debug, Commands.Debug.SetInterface, interface)
            packet = self.core.waitForAck(SubSystem.Debug, Commands.Debug.SetInterface)

    def getMotionStatus(self):
        """
            Retrieve current motion streaming status.

            :return: MotionStatusData instance.
        """
        self.core.sendCommand(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        self.core.waitForAck(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        return packet.data.motionStatus

    def getRecorderStatus(self):
        """
            Retrieve current recording status

            :return: RecorderStatusData instance.
        """
        self.core.sendCommand(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        self.core.waitForAck(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        return packet.data.recorderStatus

    def setDownsample(self, factor):
        """
            Set motion streaming downsampling.
            Downsampling must be between 20 and 1000, and a multiple of 20.
            This represent the time in ms between each packet.

            :param factor:  Downsampling factor to use.
        """
        # Limit to factor of 20 and between 20 and 1000.
        assert factor % 20 == 0 and 20 <= factor <= 1000
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.Downsample, factor)
        logging.debug('Sending downsample command. Waiting for acknowledge.')
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.Downsample)
        logging.debug('Acknowledgment received.')

    def setAccelerometerRange(self, factor):
        """
            Set accelerometer range. Must be 2, 4, 8 or 16.

            :param factor:  Accelerometer range to use.
        """
        # Limit factor to 2, 4, 8 and 16
        assert factor == 2 or factor == 4 or factor == 8 or factor == 16
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.AccRange, factor)
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.AccRange)

    def resetTimestamp(self):
        """
            Reset timestamp
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.ResetTimeStamp, True)
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.ResetTimeStamp)

    def streamDisableAll(self):
        """
            Disable all streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.DisableStreaming, True)
        logging.debug("Sending disable streaming command. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.DisableStreaming)
        logging.debug("Acknowledgment received.")

    def getEulerAngle(self):
        """
            Retrieve Euler Angle.
            This is a blocking function until an Euler Angle is retrieve.
            Requires that Euler Angle streaming is activated, otherwise will hang forever.

            :return: EulerAngleData instance.
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.EulerAngle)
        logging.debug("Received EulerAngle.")
        return packet.data

    def getExternalForce(self):
        """
            Retrieve External Force.
            This is a blocking function until an External Force is retrieve.
            Requires that External Force streaming is activated, otherwise will hang forever.

            :return: ExternalForceData instance.
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.ExtForce)
        logging.debug("Received ExternalForce.")
        return packet.data

    def getFingerGesture(self):
        """
            Retrieve Finger Gesture.
            This is a blocking function until a Finger Gesture is retrieve.
            Requires that Finger Gesture streaming is activated, otherwise will hang forever.

            :return: FingerGestureData instance.
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.FingerGesture)
        logging.debug("Received FingerGesture.")
        return packet.data

    def getIMU(self):
        """
            Retrieve IMU (Inertial Motion Unit).
            This is a blocking function until an IMU is retrieve.
            Requires that IMU streaming is activated, otherwise will hang forever.

            :return: IMUData instance.
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.IMU)
        logging.debug("Received IMU.")
        return packet.data

    def getMAG(self):
        """
            Retrieve MAG (Magnetometer).
            This is a blocking function until a MAG is retrieve.
            Requires that MAG streaming is activated, otherwise will hang forever.

            :return: MAGData instance.
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.MAG)
        logging.debug("Received MAG.")
        return packet.data

    def getMotionState(self):
        """
            Retrieve Motion State.
            This is a blocking function until a Motion State is retrieve.
            Requires that Motion State streaming is activated, otherwise will hang forever.

            :return: MotionStateData instance.
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.MotionState)
        logging.debug("Received MotionState.")
        return packet.data

    def getPedometer(self):
        """
            Retrieve Pedometer.
            This is a blocking function until a Pedometer is retrieve.
            Requires that Pedometer streaming is activated, otherwise will hang forever.

            :return: PedometerData instance.
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.Pedometer)
        logging.debug("Received Pedometer.")
        return packet.data

    def getQuaternion(self):
        """
            Retrieve Quaternion.
            This is a blocking function until a Quaternion is retrieve.
            Requires that Quaternion streaming is activated, otherwise will hang forever.

            :return: QuaternionData instance.
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.Quaternion)
        logging.debug("Received Quaternion.")
        return packet.data

    def getRotationInfo(self):
        """
            Retrieve Rotation Information.
            This is a blocking function until a Rotation Information is retrieve.
            Requires that Rotation Information streaming is activated, otherwise will hang forever.

            :return: RotationData instance.
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.RotationInfo)
        logging.debug("Received RotationInfo.")
        return packet.data

    def getSittingStanding(self):
        """
            Retrieve Sitting/Standing.
            This is a blocking function until a Sitting/Standing is retrieve.
            Requires that Sitting/Standing streaming is activated, otherwise will hang forever.

            :return:
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.SittingStanding)
        logging.debug("Received SittingStanding.")
        return packet.data

    def getTrajectoryInfo(self):
        """
            Retrieve Trajectory Information.
            This is a blocking function until a Trajectory Information is retrieve.
            Requires that Trajectory Information is recording and streaming, otherwise will hang forever.

            :return: EulerAngleData instance.
        """
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, Commands.Motion.TrajectoryInfo)
        logging.debug("Received TrajectoryInfo.")
        return packet.data

    def recordTrajectory(self, state):
        """
            Record trajectory information.

            :param state: True, to start recording. False, to stop recording.
        :return:
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.TrajectoryRecStartStop, state)
        logging.debug("Sending recordTrajectory. Waiting for aknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.TrajectoryRecStartStop)
        logging.debug("Acknowledgment received.")

    def streamEulerAngle(self, state):
        """
            Start/Stop Euler Angle streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.EulerAngle, state)
        logging.debug("Sending streamEulerAngle. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.EulerAngle)
        logging.debug("Acknowledgment received.")

    def streamExternalForce(self, state):
        """
            Start/Stop External Force streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.ExtForce, state)
        logging.debug("Sending streamExternalForce. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.ExtForce)
        logging.debug("Acknowledgment received.")

    def streamFingerGesture(self, state):
        """
            Start/Stop Finger Gesture streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.FingerGesture, state)
        logging.debug("Sending streamFingerGesture. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.FingerGesture)
        logging.debug("Acknowledgment received.")

    def streamIMU(self, state):
        """
            Start/Stop IMU streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.IMU, state)
        logging.debug("Sending streamIMU. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.IMU)
        logging.debug("Acknowledgment received.")

    def streamMAG(self, state):
        """
            Start/Stop MAG streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.MAG, state)
        logging.debug("Sending streamMAG. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.MAG)
        logging.debug("Acknowledgment received.")

    def streamMotionState(self, state):
        """
            Start/Stop Motion State streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.MotionState, state)
        logging.debug("Sending streamMotionState. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.MotionState)
        logging.debug("Acknowledgment received.")

    def streamPedometer(self, state):
        """
            Start/Stop Pedometer streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.Pedometer, state)
        logging.debug("Sending streamPedometer. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.Pedometer)
        logging.debug("Acknowledgment received.")

    def streamQuaternion(self, state):
        """
            Start/Stop Quaternion streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.Quaternion, state)
        logging.debug("Sending streamQuaternion. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.Quaternion)
        logging.debug("Acknowledgment received.")

    def streamRotationInfo(self, state):
        """
            Start/Stop Rotation Information streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.RotationInfo, state)
        logging.debug("Sending streamRotationInfo. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.RotationInfo)
        logging.debug("Acknowledgment received.")

    def streamSittingStanding(self, state):
        """
            Start/Stop Sitting/Standing streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.SittingStanding, state)
        logging.debug("Sending streamSittingStanding. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.SittingStanding)
        logging.debug("Acknowledgment received.")

    def streamTrajectoryInfo(self, state):
        """
            Start/Stop Trajectory Information streaming.

            :param state: True, to start streaming. False, to stop streaming.
        """
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.TrajectoryInfo, state)
        logging.debug("Sending streamTrajectoryInfo. Waiting for acknowledge.")
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.TrajectoryInfo)
        logging.debug("Acknowledgment received.")

    def eepromRead(self, readPageNumber):
        """
            Read a page from EEPROM

            :param readPageNumber: EEPROM page number to read.
            :return: EEPROMReadData instance.
        """
        assert 0 <= readPageNumber <= 255
        self.core.sendCommand(SubSystem.EEPROM, Commands.EEPROM.Read, pageNumber=readPageNumber)
        logging.debug("Sending EEPROM Read command. Waiting for acknowledgment.")
        packet = self.core.waitForAck(SubSystem.EEPROM, Commands.EEPROM.Read)
        logging.debug("Acknowledge received.")
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.EEPROM, Commands.EEPROM.Read)
        logging.debug("EEPROM Read packet received.")
        return packet.data.dataBytes

    def eepromWrite(self, writePageNumber, dataString):
        """
            Write a page to EEPROM.

            :param writePageNumber: EEPROM page number to write.
            :param dataString: 8-byte data string to write.
        """
        assert 0 <= writePageNumber <= 255
        self.core.sendCommand(SubSystem.EEPROM, Commands.EEPROM.Write, \
                         pageNumber=writePageNumber, dataBytes=dataString)
        packet = self.core.waitForAck(SubSystem.EEPROM, Commands.EEPROM.Write)

    def getLED(self, index):
        """
            Retrieve LED state.

            :param index: LED index to retrieve.
            :return: LEDGetValData instance.
        """
        assert 0 <= index <= 7
        self.core.sendCommand(SubSystem.LED, Commands.LED.GetVal, ledIndices=[index])
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.LED, Commands.LED.GetVal)
        if not packet:
            return 0xF  # Return anything but 0x0 or 0x1
        return packet.data.ledState[index]

    def setLED(self, ledIndex, ledValue):
        """
            Set LED state.

            :param ledIndex: LED index to use.
            :param ledValue: LED state. True, open. False, close.
        """
        assert 0 <= ledIndex <= 7
        ledValues = [(ledIndex, ledValue)]
        self.core.sendCommand(SubSystem.LED, Commands.LED.SetVal, ledValueTupleList=ledValues)
        self.core.waitForAck(SubSystem.LED, Commands.LED.SetVal)
        self.core.waitForPacket(PacketType.RegularResponse, SubSystem.LED, Commands.LED.GetVal)

    def eraseStorage(self, eraseType=Erase.Quick):
        """
            Erase storage.
            Full erase can take up to 3 minute to complete.

            :param eraseType: Erase Type. Quick or Full.
        """
        assert eraseType==Erase.Mass or eraseType==Erase.Quick

        # Step 1 - Initialization
        self.core.sendCommand(SubSystem.Motion, Commands.Motion.DisableStreaming, True)
        logging.debug('Sending the DisableAllStreaming command, and waiting for a response...')

        # Step 2 - wait for ack
        self.core.waitForAck(SubSystem.Motion, Commands.Motion.DisableStreaming)
        logging.debug('Acknowledge packet was received!')

        # Step 3 - erase the flash command
        self.core.sendCommand(SubSystem.Storage, Commands.Storage.EraseAll, eraseType)
        logging.debug('Sent the EraseAll command, and waiting for a response...')

        # Step 4 - wait for ack
        self.core.waitForAck(SubSystem.Storage, Commands.Storage.EraseAll)
        logging.debug("Acknowledge packet was received!")
        logging.info("Started erasing... This takes up to around 3 minutes...")

        # Step 5 - wait for the completion notice
        self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.EraseAll)
        logging.info('Flash erase has completed successfully!')

    def sessionRecord(self, state):
        """
            Start/Stop recording a session.

            :param state: True, to start recording. False, to stop recording.
            :return: Recording session identifier.
        """
        # Step 1 - Start recording
        self.core.sendCommand(SubSystem.Storage, Commands.Storage.Record, state)
        if state:
            logging.debug('Sending the command to start the flash recorder, and waiting for a response...')
        else:
            logging.debug('Sending the command to stop the flash recorder, and waiting for a response...')

        # Step 2 - wait for ack and the session number
        self.core.waitForAck(SubSystem.Storage, Commands.Storage.Record)
        logging.debug("Acknowledge received.")
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.Record)
        if packet.header.packetType == PacketType.ErrorLogResp:
            logging.warn("Flash is full, not recording.")
        else:
            logging.debug('Acknowledge packet was received with the session number {0}!'.format(packet.data.sessionID))
        sessionID = packet.data.sessionID

        return sessionID

    def sessionPlayback(self, pbSessionID, dump=False):
        """
            Playback a recorded session.

            :param pbSessionID: Recorded session identifier.
            :param dump: True, to dump recorded data to file. False, to skip.
            :return: Number of data retrieved.
        """
        self.core.sendCommand(SubSystem.Storage, Commands.Storage.Playback, True, sessionID=pbSessionID)
        logging.debug('Sent the start playback command, waiting for response...')
        # wait for confirmation
        self.core.waitForAck(SubSystem.Storage, Commands.Storage.Playback)
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.Playback)
        if packet.header.packetType == PacketType.ErrorLogResp:
            logging.error('Playback failed due to an invalid session number request!')
            return 0
        else:
            pbSessionID = packet.data.sessionID
            logging.info('Playback routine started from session number {0}'.format(pbSessionID))
            packetList = self.core.storePacketsUntil(PacketType.RegularResponse, SubSystem.Storage,
                                                     Commands.Storage.Playback)
            logging.info('Finished playback from session number {0}!'.format(pbSessionID))
            if dump:
                logging.info('Saving dump file. Waiting for completion...')
                NebUtilities.saveFlashPlayback(pbSessionID, packetList)
                logging.info('Dump file saving completed.')
            return len(packetList)

    def sessionPlaybackPlot(self, pbSessionID):
        """
            Playback a recorded session and plot the pedometer related data including the thigh's elevation angle and the walking path.

            :param pbSessionID: Recorded session identifier.
            :return: Number of data retrieved.
        """
        self.core.sendCommand(SubSystem.Storage, Commands.Storage.Playback, True, sessionID=pbSessionID)
        logging.debug('Sent the start playback command, waiting for response...')
        # wait for confirmation
        self.core.waitForAck(SubSystem.Storage, Commands.Storage.Playback)
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.Playback)
        if packet.header.packetType == PacketType.ErrorLogResp:
            logging.error('Playback failed due to an invalid session number request!')
            return 0
        else:
            pbSessionID = packet.data.sessionID
            logging.info('Playback routine started from session number {0}'.format(pbSessionID))
            packetList = self.core.storePacketsUntil(PacketType.RegularResponse, SubSystem.Storage,
                                                     Commands.Storage.Playback)
            logging.info('Finished playback from session number {0}!'.format(pbSessionID))
            headingAngles = [0]*len(packetList)
            rollAngles = [0]*len(packetList)
            pitchAngles = [0]*len(packetList)
            pos_x = [0]*len(packetList)
            pos_y = [0]*len(packetList)
            timestamp = [0]*len(packetList)
            count = 0
            stepCounter = 0

            plt.figure(1)
            plt.title('Thigh Elevation Angle')
            plt.ylabel('Angle')
            plt.xlabel('Sample')
            plt.figure(2)
            plt.title('Walking Path')
            plt.xlabel('Walking Position X')
            plt.ylabel('Walking Position Y')

            for packet in packetList:
                if packet.header.subSystem != SubSystem.Motion or packet.header.packetType != PacketType.RegularResponse:
                    continue
                if packet.header.command == Commands.Motion.Pedometer and packet.data.stepsPerMinute>0:
                    headingAngles[stepCounter] = packet.data.walkingDirection
                    stepCounter = stepCounter + 1
                    pos_x[stepCounter] = pos_x[stepCounter-1] + math.sin(headingAngles[stepCounter-1]*math.pi/180)
                    pos_y[stepCounter] = pos_y[stepCounter-1] + math.cos(headingAngles[stepCounter-1]*math.pi/180)
                if packet.header.command == Commands.Motion.Quaternion:
                    a = packet.data.quaternions[0]/32768
                    b = packet.data.quaternions[1]/32768
                    c = packet.data.quaternions[2]/32768
                    d = packet.data.quaternions[3]/32768
                    rollAngles[count] = math.atan2(2*(a*b+c*d),1-2*(b*b+c*c))
                    pitchAngles[count] = math.asin(2*(a*c-b*d))
                    rollAngles[count] = rollAngles[count]*180/math.pi
                    pitchAngles[count] = pitchAngles[count]*180/math.pi
                    count = count + 1
                    timestamp[count] = timestamp[count-1] + 0.02
            rollAngles = rollAngles[0:count-1]
            pitchAngles = pitchAngles[0:count-1]
            headingAngles = headingAngles[0:stepCounter-1]
            pos_x = pos_x[0:stepCounter]
            pos_y = pos_y[0:stepCounter]

            plt.figure(2)
            plt.plot(pos_x[0:stepCounter],pos_y[0:stepCounter],'bo')
            for ii in range(1,stepCounter):
                plt.annotate('', xy=(pos_x[ii], pos_y[ii]), xytext=(pos_x[ii-1], pos_y[ii-1]), arrowprops=dict(facecolor='black', shrink=0.03))
            plt.pause(0.001)

            plt.figure(1)
            plt.plot(timestamp[1:count],rollAngles[0:count-1],'bo-')
            plt.pause(0.001)

            return len(packetList)

    def getSessionCount(self):
        """
            Retrieve number of session recording

            :return: Recorded session count.
        """
        self.core.sendCommand(SubSystem.Storage, Commands.Storage.NumSessions)
        packet = self.core.waitForAck(SubSystem.Storage, Commands.Storage.NumSessions)
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.NumSessions)
        return packet.data.numSessions

    def getSessionInfo(self, sessionID):
        """
            Retrieve a session information.

            :param sessionID: Recorded session identifier
            :return: FlashSessionInfo instance.
        """
        self.core.sendCommand(SubSystem.Storage, Commands.Storage.SessionInfo, sessionID=sessionID)
        self.core.waitForAck(SubSystem.Storage, Commands.Storage.SessionInfo)
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.SessionInfo)
        if packet.data.sessionLength == 0xFFFFFFFF:
            return None
        else:
            return packet.data

    def getFirmwareVersions(self):
        """
            Retrieve firmware versions.

            :return: FirmwareVersionsData instance.
        """
        self.core.sendCommand(SubSystem.Debug, Commands.Debug.FWVersions)
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Debug, Commands.Debug.FWVersions)
        return packet.data

    def debugUnitTestEnable(self, enable=True):
        """
            Debugging/Testing function only.
        """
        self.core.sendCommand(SubSystem.Debug, Commands.Debug.StartUnitTestMotion, enable)
        logging.debug("Sending Start UnitTest Motion. Waiting for acknowledgment.")
        self.core.waitForAck(SubSystem.Debug, Commands.Debug.StartUnitTestMotion)
        logging.debug("Acknowledgment received")

    def debugUnitTestSendBytes(self, bytes):
        """
            Debugging/Testing function only.
        """
        self.core.sendCommandBytes(bytes)
        logging.debug("Sending UnitTest Motion Bytes. Waiting for packet.")
        packet = self.core.waitForPacket(PacketType.RegularResponse, SubSystem.Debug, Commands.Debug.UnitTestMotionData)
        logging.debug("Packet received.")
        return packet
