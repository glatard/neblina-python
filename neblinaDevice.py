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

import threading

from neblina import *
from neblinaUART2 import NeblinaUART2

bleSupported = True
try:
    from neblinaBLE2 import NeblinaBLE2
except ImportError:
    print("Unable to import BLE. BLE is unsupported and can not be used.")
    bleSupported = False

###################################################################################


class NeblinaDevice(object):

    def __init__(self, address, interface):
        self.address = address

        if interface is Interface.UART:
            self.communication = NeblinaUART2(self.address)
        else:
            assert bleSupported
            self.communication = NeblinaBLE2(self.address)

    def connect(self):
        self.communication.connect()

    def disconnect(self):
        self.communication.disconnect()

    def isConnected(self):
        return self.communication.isConnected()

    def receivedPacket(self):
        if self.isConnected():
            return self.communication.receivedPacket()
        else:
            return None

    def sendPacket(self, packet):
        self.communication.sendPacket(packet)

