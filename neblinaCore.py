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

import asyncio
import logging
import queue
import threading

from neblina import *
from neblinaCommandPacket import NebCommandPacket
from neblinaDevice import NeblinaDevice
from neblinaError import *
from neblinaHeader import NebHeader
from neblinaResponsePacket import NebResponsePacket

###################################################################################


class NeblinaCore(threading.Thread):

    def __init__(self, interface=Interface.UART):
        threading.Thread.__init__(self)
        self.delegate = None
        self.device = None
        self.eventLoop = asyncio.get_event_loop()
        self.interface = interface
        self.isPause = False
        self.receivedPacket = list()
        self.receivedStream = [None]*Commands.Motion.MotionCount
        self.stopRequested = False

    def close(self):
        self.stop()
        if self.device:
            self.device.disconnect()

    def open(self, address):
        self.device = NeblinaDevice(address, self.interface)
        self.device.connect()
        self.start()

    def isOpened(self):
        return self.device and self.device.isConnected()

    def run(self):
        if not self.device:
            return

        while not self.stopRequested:
            if self.isPause:
                continue

            if self.device.isConnected():
                try:
                    packet = self.device.receivedPacket()
                    if packet:
                        packet = NebResponsePacket(packet)
                        if packet.header.packetType is PacketType.RegularResponse and \
                            packet.header.subSystem == SubSystem.Motion:
                            if self.delegate:
                                self.delegate.handle(packet)
                            else:
                                logging.debug("Received Stream : {0}".format(packet.data))
                                self.receivedStream[packet.header.command] = packet
                        else:
                            logging.debug("Received Packet : {0}".format(packet.data))
                            self.receivedPacket.append(packet)
                except Exception:
                    logging.error("Unexpected error : ", exc_info=True)
                    break

    def stop(self):
        self.stopRequested = True
        self.join()

    def sendCommand(self, subSystem, command, enable=True, **kwargs):
        if self.device:
            packet = NebCommandPacket(subSystem, command, enable, **kwargs)
            self.device.sendPacket(packet.stringEncode())

    def setDelegate(self, delegate):
        self.delegate = delegate

    async def waitForNonEmptyPacketFromReceivedStream(self, command):
        while not self.receivedStream[command]:
            await asyncio.sleep(0.001)

    async def waitForNonEmptyPacketFromReceivedPacket(self, packetType, subSystem, command):
        packet = None
        while not packet or \
                (not packet.isPacketValid(packetType, subSystem, command) and
                 not packet.isPacketError()):
            try:
                for i in range(0, len(self.receivedPacket)):
                    packet = self.receivedPacket[i]
                    if packet.isPacketValid(packetType, subSystem, command):
                        return self.receivedPacket.pop(i)
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
                exit()
            except:
                packet = None
                logging.error("Unexpected error : ", exc_info=True)
                continue

    def waitForAck(self, subSystem, command):
        ackPacket = self.waitForPacket(PacketType.Ack, subSystem, command)
        return ackPacket

    def waitForPacket(self, packetType, subSystem, command):
        packet = None
        if packetType is PacketType.RegularResponse and subSystem is SubSystem.Motion:
            self.eventLoop.run_until_complete(self.waitForNonEmptyPacketFromReceivedStream(command))
            packet = self.receivedStream[command]
            self.receivedStream[command] = None
            return packet

        packet = self.eventLoop.run_until_complete(self.waitForNonEmptyPacketFromReceivedPacket(packetType, subSystem, command))
        return packet
