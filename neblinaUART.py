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
import serial
import serial.tools.list_ports
import time

from pyslip import slip

from neblina import *
from neblinaAPI import NeblinaAPI
from neblinaCommandPacket import NebCommandPacket
from neblinaResponsePacket import NebResponsePacket

###################################################################################


class NeblinaUART(NeblinaAPI):
    """
        NeblinaUART serves as the UART communication protocol.

        This supports only 1 UART COM port.
    """
    def __init__(self):
        NeblinaAPI.__init__(self)
        self.comslip = slip.slip()
        self.comPort = None
        self.sc = None

    def close(self, port=None):
        logging.debug("Closing COM port : {0}".format(self.comPort))
        self.sc.close()

    def open(self, port):
        self.comPort = port

        # Try to open the serial COM port
        self.sc = None
        while self.sc is None:
            try:
                self.sc = serial.Serial(port=self.comPort, baudrate=500000)
            except serial.serialutil.SerialException as se:
                if 'Device or resource busy:' in se.__str__():
                    logging.info('Opening COM port is taking a little while, please stand by...')
                else:
                    logging.error('se: {0}'.format(se))
                time.sleep(1)

        self.sc.flushInput()

    def isOpened(self, port=None):
        return self.sc and self.sc.is_open

    def sendCommand(self, subSystem, command, enable=True, **kwargs):
        commandPacket = NebCommandPacket(subSystem, command, enable, **kwargs)
        self.sendCommandBytes(commandPacket.stringEncode())

    def sendCommandBytes(self, bytes):
        self.comslip.sendPacketToStream(self.sc, bytes)

    def receivePacket(self):
        bytes = self.comslip.receivePacketFromStream(self.sc)
        packet = NebResponsePacket(bytes)
        return packet

    def getBatteryLevel(self):
        self.sendCommand(SubSystem.Power, Commands.Power.GetBatteryLevel, True)
        packet = self.waitForAck(SubSystem.Power, Commands.Power.GetBatteryLevel)
        packet = self.waitForPacket(PacketType.RegularResponse, SubSystem.Power, Commands.Power.GetBatteryLevel)
        return packet.data.batteryLevel
