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
from neblinaData import *
from neblinaError import *
from neblinaUtilities import NebUtilities

###################################################################################


class NeblinaAPIBase(object):
    """
        NeblinaAPIBase serves as a base interface to Neblina communication protocol.

        This can not be used directly, only derived from.
    """
    def __init__(self):
        # Prevent self instantiation
        assert type(self) != NeblinaAPIBase

    def close(self):
        raise NotImplementedError("close not override in child.")

    def open(self, port):
        raise NotImplementedError("open not override in child.")

    def isOpened(self, port=None):
        raise NotImplementedError("isOpened not override in child.")

    def sendCommand(self, subSystem, command, enable=True, **kwargs):
        raise NotImplementedError("sendCommand not override in child.")

    def sendCommandBytes(self, bytes):
        raise NotImplementedError("sendCommandBytes not override in child.")

    def receivePacket(self):
        raise NotImplementedError("receivePacket not override in child.")

    def getBatteryLevel(self):
        raise NotImplementedError("getBatteryLevel not override in child")

    def getTemperature(self):
        self.sendCommand(SubSystem.Power, Commands.Power.GetTemperature, True)
        packet = self.waitForAck(SubSystem.Power, Commands.Power.GetTemperature)
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Power, Commands.Power.GetTemperature)
        return packet.data.temperature

    def setStreamingInterface(self, interface=Interface.BLE):
        self.sendCommand(SubSystem.Debug, Commands.Debug.SetInterface, interface)
        logging.debug('Waiting for the module to switch its interface...')
        packet = self.waitForAck(SubSystem.Debug, Commands.Debug.SetInterface)
        logging.debug("Module has switched its interface.")
        numTries = 0
        while (packet == None):
            numTries += 1
            if numTries > 5:
                logging.error('The unit is not responding. Exiting...')
                exit()
            logging.warning('Trying again...')
            self.sendCommand(SubSystem.Debug, Commands.Debug.SetInterface, interface)
            packet = self.waitForAck(SubSystem.Debug, Commands.Debug.SetInterface)

    def stopEverything(self, noack=False):
        self.stopAllStreams(noack)
        self.flashRecordStop()

    def stopAllStreams(self, noack=False):
        """
            Stop all streams.
            For now, calls motionStopStreams which stop all motion streams.
            In the future, this function will stop all streams which are not associated with motion.
            This could be done with a single new commands or multiple separate commands.
        """
        self.motionStopStreams(noack)

    def isPacketError(self, packet):
        error = False
        if packet:
            error |= packet.header.packetType == PacketType.ErrorLogResp
        return error

    def isPacketValid(self, packet, packetType, subSystem, command):
        valid = (packet != None)
        if valid:
            valid = self.isPacketHeaderValid(packet.header, packetType, subSystem, command)
        return valid

    def isPacketHeaderValid(self, header, packetType, subSystem, command):
        valid = (header.packetType == packetType)
        valid &= (header.subSystem == subSystem)
        valid &= (header.command == command)
        return valid

    def waitForAck(self, subSystem, command):
        ackPacket = self.waitForPacket(PacketType.Ack, subSystem, command)
        return ackPacket

    def waitForPacket(self, packetType, subSystem, command):
        packet = None
        while not self.isPacketValid(packet, packetType, subSystem, command) and \
              not self.isPacketError(packet):
            try:
                packet = self.receivePacket()
            except NotImplementedError as e:
                logging.error("Dropped bad packet.")
                packet = None
                continue
            except InvalidPacketFormatError as e:
                logging.error("InvalidPacketFormatError.")
                packet = None
                continue
            except CRCError as e:
                logging.error("CRCError : " + str(e))
                packet = None
                continue
            except KeyError as e:
                logging.error("Tried creating a packet with an invalid subsystem or command : " + str(e))
                packet = None
                continue
            except TimeoutError as e:
                logging.error('Read timed out.')
                return None
            except KeyboardInterrupt as e:
                logging.error("KeyboardInterrupt.")
                exit()
            except:
                packet = None
                logging.error("Unexpected error : ", exc_info=True)
                continue
        return packet

    def motionGetStates(self):
        self.sendCommand(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        self.waitForAck(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        return packet.data
        # return (packet.data.distance, packet.data.force, packet.data.euler, packet.data.quaternion, \
        #         packet.data.imuData, packet.data.motion, packet.data.steps, packet.data.magData, packet.data.sitStand)

    def motionSetDownsample(self, factor):
        # Limit to factor of 20 and between 20 and 1000.
        assert factor % 20 == 0 and 20 <= factor <= 1000
        self.sendCommand(SubSystem.Motion, Commands.Motion.Downsample, factor)
        self.waitForAck(SubSystem.Motion, Commands.Motion.Downsample)

    def motionSetAccFullScale(self, factor):
        # Limit factor between 0 and 3 inclusively
        assert factor == 2 or factor == 4 or factor == 8 or factor == 16
        self.sendCommand(SubSystem.Motion, Commands.Motion.AccRange, factor)
        self.waitForAck(SubSystem.Motion, Commands.Motion.AccRange)

    def motionResetTimestamp(self):
        self.sendCommand(SubSystem.Motion, Commands.Motion.ResetTimeStamp, True)
        self.waitForAck(SubSystem.Motion, Commands.Motion.ResetTimeStamp)

    def motionStopStreams(self, noack=False):
        self.sendCommand(SubSystem.Motion, Commands.Motion.DisableStreaming, True)
        if not noack:
            self.waitForAck(SubSystem.Motion, Commands.Motion.DisableStreaming)

    def motionStartStreams(self, streamingType):
        # Send command to start streaming
        self.sendCommand(SubSystem.Motion, streamingType, True)
        logging.debug("Sending start motion command. Waiting for acknowledge.")
        packet = self.waitForAck(SubSystem.Motion, streamingType)
        logging.debug("Acknowledgment received.")
        return packet

    # Motine Engine commands
    def motionStream(self, streamingType, numPackets=None):
        errorList = []
        packet = self.motionStartStreams(streamingType)

        # Timeout mechanism.
        numTries = 0
        while (packet == None):
            logging.warning('Timed out. Trying again.')
            self.sendCommand(SubSystem.Motion, streamingType, True)
            packet = self.waitForAck(SubSystem.Motion, streamingType)
            numTries += 1
            if numTries > 5:
                logging.error('Tried {0} times and it doesn\'t respond. Exiting.'.format(numTries))
                exit()
        numTries = 0

        # Stream forever if the number of packets is unspecified (None)
        keepStreaming = (numPackets == None or numPackets > 0)
        while(keepStreaming):
            try:
                packet = self.receivePacket()
                if (packet.header.subSystem == SubSystem.Motion and packet.header.command == streamingType):
                    logging.info(packet.data)
                elif (packet.header.subSystem != SubSystem.Debug):
                    logging.warning('Unexpected packet: {0}'.format(packet.stringEncode()))
                if (numPackets != None):
                    numPackets -= 1
                keepStreaming = (numPackets == None or numPackets > 0)
            except NotImplementedError as nie:
                logging.error("NotImplementedError : " + str(nie))
            # In the event of Ctrl-C
            except KeyboardInterrupt as ki:
                break
            except CRCError as e:
                logging.error("CRCError : " + str(e))
            except TimeoutError as te:
                if ( streamingType != Commands.Motion.RotationInfo and \
                     streamingType != Commands.Motion.Pedometer and \
                     streamingType != Commands.Motion.FingerGesture and \
                     streamingType != Commands.Motion.TrajectoryInfo):
                    logging.warning('Timed out, sending command again.')
                    numTries += 1
                    self.sendCommand(SubSystem.Motion, streamingType, True)
                    if numTries > 3:
                        logging.error('Tried {0} times and it doesn\'t respond. Exiting.'.format(numTries))
                        exit()
            except Exception as e:
                logging.error("Exception : " + str(e))

        # Stop whatever it was streaming
        self.sendCommand(SubSystem.Motion, streamingType, False)

    def EEPROMRead(self, readPageNumber):
        assert 0 <= readPageNumber <= 255
        self.sendCommand(SubSystem.EEPROM, Commands.EEPROM.Read, pageNumber=readPageNumber)
        packet = self.waitForAck(SubSystem.EEPROM, Commands.EEPROM.Read)
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.EEPROM, Commands.EEPROM.Read)
        return packet.data.dataBytes

    def EEPROMWrite(self, writePageNumber, dataString):
        assert 0 <= writePageNumber <= 255
        self.sendCommand(SubSystem.EEPROM, Commands.EEPROM.Write, \
                         pageNumber=writePageNumber, dataBytes=dataString)
        packet = self.waitForAck(SubSystem.EEPROM, Commands.EEPROM.Write)

    def getLEDs(self, ledIndices):
        if type(ledIndices) != list:
            logging.warning("Use this function with a list of leds you want to know the value as an argument.")
            return
        self.sendCommand(SubSystem.LED, Commands.LED.GetVal, ledIndices=ledIndices)
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.LED, Commands.LED.GetVal)
        return packet.data.ledTupleList

    def getLED(self, index):
        self.sendCommand(SubSystem.LED, Commands.LED.GetVal, ledIndices=[index])
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.LED, Commands.LED.GetVal)
        if not packet:
            return 0xF  # Return anything but 0x0 or 0x1
        return packet.data.ledTupleList[0]

    def setLEDs(self, ledValues):
        if type(ledValues) != list and type(ledValues[0]) == tuple:
            logging.warning("Use this function with a list of tuples as an argument.")
            return
        self.sendCommand(SubSystem.LED, Commands.LED.SetVal, ledValueTupleList=ledValues)
        self.waitForAck(SubSystem.LED, Commands.LED.SetVal)

    def setLED(self, ledIndex, ledValue):
        ledValues = [(ledIndex, ledValue)]
        self.sendCommand(SubSystem.LED, Commands.LED.SetVal, ledValueTupleList=ledValues)
        self.waitForAck(SubSystem.LED, Commands.LED.SetVal)

    def flashGetState(self):
        self.sendCommand(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        self.waitForAck(SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Debug, Commands.Debug.MotAndFlashRecState)
        return MotAndFlashRecStateData.recorderStatusStrings[packet.data.recorderStatus]

    def flashErase(self, eraseType=Erase.Quick):
        # Step 1 - Initialization
        self.sendCommand(SubSystem.Motion, Commands.Motion.DisableStreaming, True)
        logging.debug('Sending the DisableAllStreaming command, and waiting for a response...')

        # Step 2 - wait for ack
        self.waitForAck(SubSystem.Motion, Commands.Motion.DisableStreaming)
        logging.debug('Acknowledge packet was received!')

        # Step 3 - erase the flash command
        self.sendCommand(SubSystem.Storage, Commands.Storage.EraseAll, eraseType)
        logging.debug('Sent the EraseAll command, and waiting for a response...')

        # Step 4 - wait for ack
        self.waitForAck(SubSystem.Storage, Commands.Storage.EraseAll)
        logging.debug("Acknowledge packet was received!")
        logging.info("Started erasing... This takes up to around 3 minutes...")

        # Step 5 - wait for the completion notice
        self.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.EraseAll)
        logging.info('Flash erase has completed successfully!')

    def flashRecordStart(self, streamingType=None):
        if streamingType:
            self.sendCommand(SubSystem.Motion, streamingType, False)
            logging.debug('Sending the stop streaming command, and waiting for a response...')

            self.waitForAck(SubSystem.Motion, Commands.Motion.DisableStreaming)
            logging.debug('Acknowledge packet was received!')

        # Step 1 - Initialization
        # self.sendCommand(SubSystem.Motion, Commands.Motion.DisableStreaming, True)
        # logging.debug('Sending the DisableAllStreaming command, and waiting for a response...')

        # Step 2 - wait for ack
        # self.waitForAck(SubSystem.Motion, Commands.Motion.DisableStreaming)
        # logging.debug('Acknowledge packet was received!')

        # Step 3 - Start recording
        self.sendCommand(SubSystem.Storage, Commands.Storage.Record, True)
        logging.debug('Sending the command to start the flash recorder, and waiting for a response...')

        # Step 4 - wait for ack and the session number
        self.waitForAck(SubSystem.Storage, Commands.Storage.Record)
        logging.debug("Acknowledge received.")
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.Record)
        if packet.header.packetType == PacketType.ErrorLogResp:
            logging.warn("Flash is full, not recording.")
        else:
            logging.debug('Acknowledge packet was received with the session number {0}!'.format(packet.data.sessionID))
        sessionID = packet.data.sessionID

        # Step 5 - enable streaming
        # self.sendCommand(SubSystem.Motion, streamingType, True)
        # logging.debug('Sending the enable streaming command, and waiting for a response...')

        # Step 6 - wait for ack
        # self.waitForAck(SubSystem.Motion, streamingType)
        # logging.debug('Acknowledge packet was received!')

        return sessionID

    def flashRecordStop(self, streamingType=None):
        # Step 8 - Stop the streaming
        #self.sendCommand(SubSystem.Motion, dataType, False)
        #logging.debug('Sending the stop streaming command, and waiting for a response...')

        # Step 9 - wait for ack
        #self.waitForAck(SubSystem.Motion, dataType)
        #logging.debug('Acknowledge packet was received!')

        # Step 10 - Stop the recording
        self.sendCommand(SubSystem.Storage, Commands.Storage.Record, False)
        logging.debug('Sending the command to stop the flash recorder, and waiting for a response...')

        # Step 11 - wait for ack and the closed session confirmation
        self.waitForAck(SubSystem.Storage, Commands.Storage.Record)
        logging.debug("The acknowledge packet is received")
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.Record)

        return packet.data.sessionID

    def flashRecord(self, numSamples, streamingType):
        sessionID = self.flashRecordStart(streamingType)

        # Step 7 Receive Packets
        for x in range(1, numSamples + 1):
            packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Motion, streamingType)
            print('Recording {0} packets, current packet: {1}'.format(numSamples, x), end="\r", flush=True)

        self.flashRecordStop(streamingType)

        logging.info("Session {0} is closed successfully".format(sessionID))

    def flashPlayback(self, pbSessionID, dump=False):
        self.sendCommand(SubSystem.Storage, Commands.Storage.Playback, True, sessionID=pbSessionID)
        logging.debug('Sent the start playback command, waiting for response...')
        # wait for confirmation
        self.waitForAck(SubSystem.Storage, Commands.Storage.Playback)
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.Playback)
        if packet.header.packetType == PacketType.ErrorLogResp:
            logging.error('Playback failed due to an invalid session number request!')
            return 0
        else:
            pbSessionID = packet.data.sessionID
            logging.info('Playback routine started from session number {0}'.format(pbSessionID))
            packetList = self.storePacketsUntil(PacketType.RegularResponse, SubSystem.Storage,
                                                Commands.Storage.Playback)
            logging.info('Finished playback from session number {0}!'.format(pbSessionID))
            if dump:
                NebUtilities.saveFlashPlayback(pbSessionID, packetList)
            return len(packetList)

    def flashGetSessions(self):
        self.sendCommand(SubSystem.Storage, Commands.Storage.NumSessions)
        packet = self.waitForAck(SubSystem.Storage, Commands.Storage.NumSessions)
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.NumSessions)
        return packet.data.numSessions

    def flashGetSessionInfo(self, sessionID):
        self.sendCommand(SubSystem.Storage, Commands.Storage.SessionInfo, sessionID=sessionID)
        self.waitForAck(SubSystem.Storage, Commands.Storage.SessionInfo)
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Storage, Commands.Storage.SessionInfo)
        if packet.data.sessionLength == 0xFFFFFFFF:
            return None
        else:
            return packet.data

    def storePacketsUntil(self, packetType, subSystem, command):
        packetList = []
        packet = None
        while not self.isPacketValid(packet, packetType, subSystem, command):
            try:
                if (packet != None and packet.header.subSystem != SubSystem.Debug):
                    packetList.append(packet)
                    print('Received {0} packets'.format(len(packetList)), end="\r", flush=True)
                packet = self.receivePacket()
            except NotImplementedError as e:
                packet = None
                logging.error("Packet {0} - Dropped bad packet : {1}".format(len(packetList), str(e)))
                continue
            except KeyError as e:
                packet = None
                logging.error("Packet {0} - Tried creating a packet with an invalid subsystem or command : {1}".format(\
                    len(packetList), str(e)))
                continue
            except CRCError as e:
                packet = None
                logging.error("Packet {0} - CRCError : {1} ".format(len(packetList), str(e)))
                continue
            except Exception as e:
                packet = None
                logging.error("Packet {0} - Exception : {1}".format(len(packetList), str(e)))
                continue
            except:
                packet = None
                logging.error("Packet {0} - Unexpected error".format(len(packetList)), exc_info=True)
                continue

        logging.info('Total IMU Packets Read: {0}'.format(len(packetList)))
        return packetList

    def debugFWVersions(self):
        self.sendCommand(SubSystem.Debug, Commands.Debug.FWVersions)
        versionPacket = self.waitForPacket(PacketType.RegularResponse, SubSystem.Debug, Commands.Debug.FWVersions)
        return versionPacket.data

    def debugUnitTestEnable(self, enable=True):
        self.sendCommand(SubSystem.Debug, Commands.Debug.StartUnitTestMotion, enable)
        self.waitForAck(SubSystem.Debug, Commands.Debug.StartUnitTestMotion)

    def debugUnitTestSendBytes(self, bytes):
        self.sendCommandBytes(bytes)
        return self.waitForPacket(PacketType.RegularResponse, SubSystem.Debug, Commands.Debug.UnitTestMotionData)