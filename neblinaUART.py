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
import time
import os

from neblinaCommunication import NeblinaCommunication

from pyslip import slip

###################################################################################


class NeblinaUART(NeblinaCommunication):

    def __init__(self, address):
        NeblinaCommunication.__init__(self, address)
        self.comslip = slip.slip()
        self.sc = None

    def connect(self):
        # Try to open the serial COM port
        logging.debug("Opening COM port : {0}".format(self.address))
        self.sc = None
        while self.sc is None:
            try:
                self.sc = serial.Serial(port=self.address, baudrate=576000)
            except serial.serialutil.SerialException as se:
                if 'Device or resource busy:' in se.__str__():
                    logging.info('Opening COM port is taking a little while, please stand by...')
                else:
                    logging.error('se: {0}'.format(se))
                time.sleep(1)

        self.sc.flushInput()

    def disconnect(self):
        logging.debug("Closing COM port : {0}".format(self.address))
        self.sc.close()

    def isConnected(self):
        if os.name == "posix":
            return self.sc and self.sc.is_open
        else:
            return self.sc and self.sc.isOpen()

    def receivePacket(self):
        packet = None
        try:
            packet = self.comslip.receivePacketFromStream(self.sc)
        except KeyboardInterrupt:
            pass
        return packet

    def sendPacket(self, packet):
        self.comslip.sendPacketToStream(self.sc, packet)
