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
from neblinaCommandPacket import NebCommandPacket
from neblinaDevice import NeblinaDevice
from neblinaError import *
from neblinaResponsePacket import NebResponsePacket

###################################################################################


class NeblinaCore(object):

    def __init__(self, interface=Interface.UART):
        self.delegate = None
        self.device = None
        self.interface = interface

    def close(self):
        self.stop()
        if self.device:
            self.device.disconnect()

    def open(self, address):
        self.device = NeblinaDevice(address, self.interface)
        self.device.connect()

    def isOpened(self):
        return self.device and self.device.isConnected()

    def getBatteryLevel(self):
        if self.device:
            if self.interface is Interface.UART:
                self.sendCommand(SubSystem.Power, Commands.Power.GetBatteryLevel, True)
                packet = self.waitForAck(SubSystem.Power, Commands.Power.GetBatteryLevel)
                packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Power, Commands.Power.GetBatteryLevel)
                return packet.data.batteryLevel
            else:
                self.device.getBatteryLevel()

    def stop(self):
        self.device.disconnect()

    def sendCommand(self, subSystem, command, enable=True, **kwargs):
        if self.device:
            packet = NebCommandPacket(subSystem, command, enable, **kwargs)
            self.device.sendPacket(packet.stringEncode())

    def setDelegate(self, delegate):
        self.delegate = delegate

    def storePacketsUntil(self, packetType, subSystem, command):
        packetList = []
        packet = None
        while not packet or \
                (not packet.isPacketValid(packetType, subSystem, command) and
                 not packet.isPacketError()):
            try:
                if packet and packet.header.subSystem != SubSystem.Debug:
                    packetList.append(packet)
                    print('Received {0} packets'.format(len(packetList)), end="\r", flush=True)
                bytes = self.device.receivePacket()
                if bytes:
                    packet = NebResponsePacket(bytes)
                else:
                    packet = None
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
                return None
            except:
                packet = None
                logging.error("Unexpected error : ", exc_info=True)
                continue
        return packetList

    def waitForAck(self, subSystem, command):
        ackPacket = self.waitForPacket(PacketType.Ack, subSystem, command)
        return ackPacket

    def waitForPacket(self, packetType, subSystem, command):
        packet = None
        while not packet or \
                (not packet.isPacketValid(packetType, subSystem, command) and
                 not packet.isPacketError()):
            try:
                bytes = self.device.receivePacket()
                if bytes:
                    packet = NebResponsePacket(bytes)
                else:
                    packet = None
            except NotImplementedError as e:
                logging.error("Dropped bad packet.")
                packet = None
                continue
            except InvalidPacketFormatError as e:
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
                return NebResponsePacket.createEmptyResponsePacket(subSystem, command)
            except KeyboardInterrupt as e:
                logging.error("KeyboardInterrupt.")
                return NebResponsePacket.createEmptyResponsePacket(subSystem, command)
            except:
                packet = None
                logging.error("Unexpected error : ", exc_info=True)
                return NebResponsePacket.createEmptyResponsePacket(subSystem, command)
        return packet
