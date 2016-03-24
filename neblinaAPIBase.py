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
from neblinaError import *

###################################################################################


class NeblinaAPIBase(object):
    """
        NeblinaAPIBase serves as a base interface to Neblina communication protocol.
    """
    def __init__(self):
        pass

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

    def stopAllStreams(self):
        """
            Stop all streams.
            For now, calls motionStopStreams which stop all motion streams.
            In the future, this function will stop all streams which are not associated with motion.
            This could be done with a single new commands or multiple separate commands.
        """
        self.motionStopStreams()

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
        while not self.isPacketValid(packet, packetType, subSystem, command):
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

    def motionStopStreams(self):
        self.sendCommand(SubSystem.Motion, Commands.Motion.DisableStreaming, True)
        self.waitForAck(SubSystem.Motion, Commands.Motion.DisableStreaming)

        # Motine Engine commands
    def motionStream(self, streamingType, numPackets=None):
        errorList = []
        # Send command to start streaming
        self.sendCommand(SubSystem.Motion, streamingType, True)
        packet = self.waitForAck(SubSystem.Motion, streamingType)

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
        return packet.data.ledTupleList[0]

    def setLEDs(self, ledValues):
        if type(ledValues) != list and type(ledValues[0]) == tuple:
            logging.warning("Use this function with a list of tuples as an argument.")
            return
        self.sendCommand(SubSystem.LED, Commands.LED.SetVal, ledValueTupleList=ledValues)

    def setLED(self, ledIndex, ledValue):
        ledValues = [(ledIndex, ledValue)]
        self.sendCommand(SubSystem.LED, Commands.LED.SetVal, ledValueTupleList=ledValues)

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