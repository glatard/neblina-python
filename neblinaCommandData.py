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

import struct

from neblina import *
from neblinaError import *

###################################################################################


class NebCommandData(object):
    """ Neblina command data

        Formatting:
        - Enable/Disable
    """

    def __init__(self, enable):
        self.enable = enable
        # self.timestamp = 0 # Not really used for now

    def encode(self):
        #garbage = ('\000'*11).encode('utf-8')
        #commandDataString = struct.pack(Formatting.CommandData.Command,\
        #    self.timestamp, self.enable, garbage)
        commandDataString = struct.pack(Formatting.CommandData.Command,\
            self.enable)
        return commandDataString

    def __str__(self):
        return "enable: {0}".format(self.enable)

###################################################################################


class NebFlashPlaybackCommandData(object):
    """ Neblina flash playback command data

        Formatting:
        - Open/Close
        - Session ID
    """
    def __init__(self, openClose, sessionID):
        self.openClose = openClose
        self.sessionID = sessionID

    def __str__(self):
        openCloseString = 'open' if self.openClose else 'close'
        return "Flash Command Session {0}: {1}"\
        .format(self.sessionID, openCloseString)

    def encode(self):
        #garbage = ('\000'*9).encode('utf-8')
        #timestamp = 0
        if self.openClose == 1:
            pass
        openCloseVal = 1 if self.openClose else 0
        #commandDataString = struct.pack(Formatting.CommandData.FlashSession,\
        #    timestamp, openCloseVal, self.sessionID, garbage)
        commandDataString = struct.pack(Formatting.CommandData.FlashSession,\
            openCloseVal, self.sessionID)
        return commandDataString

###################################################################################


class NebFlashSessionInfoCommandData(object):
    """ Neblina flash session information command data

        Formatting:
        - Session ID
    """
    def __init__(self, sessionID):
        self.sessionID = sessionID

    def __str__(self):
        return "Flash Command Info Session {0}"\
        .format(self.sessionID)

    def encode(self):
        #garbage = ('\000'*10).encode('utf-8')
        #timestamp = 0
        #commandDataString = struct.pack(Formatting.CommandData.FlashSessionInfo,\
        #    timestamp, self.sessionID, garbage)
        commandDataString = struct.pack(Formatting.CommandData.FlashSessionInfo,\
            self.sessionID)
        return commandDataString

###################################################################################

# Special 26 byte packet
class NebUnitTestMotionDataCommandData(object):
    """Neblina motion data command data (used for debugging and unit testing)

        Formatting:
        - Timestamp
        - Accelerometer
        - Gyroscope
        - Magnetometer
    """
    def __init__(self, timestamp, accel, gyro, mag):
        self.timestamp = timestamp
        self.accel = accel
        self.gyro = gyro
        self.mag = mag

    def encode(self):
        commandDataString = struct.pack(Formatting.CommandData.UnitTestMotion,\
            self.timestamp, self.accel[0], self.accel[1], self.accel[2],\
            self.gyro[0], self.gyro[1], self.gyro[2],\
            self.mag[0], self.mag[1], self.mag[2])
        return commandDataString

###################################################################################


class NebAccRangeCommandData(NebCommandData):
    """ Neblina accelerometer full-scale range command data

        Formatting:
        - Downsampling factor
    """
    rangeCodes = {2: 0x00, 4: 0x01, 8: 0x02, 16: 0x03}

    def encode(self):
        rangeCode = self.rangeCodes[self.enable]
        commandDataString = struct.pack(Formatting.CommandData.AccRange,\
            rangeCode)
        return commandDataString

###################################################################################


class NebDownsampleCommandData(NebCommandData):
    """ Neblina downsampling factor command data

        Formatting:
        - Downsampling factor
    """

    def encode(self):
        commandDataString = struct.pack(Formatting.CommandData.Downsample,\
            self.enable)
        return commandDataString

###################################################################################


class NebGetLEDCommandData(object):
    """ Neblina LED state retrieval command data

        Formatting:
        - Number of LEDs (defines the number of index/value pair to be use)
        - LED Index (one for each LEDs)
        - LED Value (one for each LEDs)
    """
    def __init__(self, ledIndices):
        if(len(ledIndices) > 7):
            raise InvalidPacketFormatError("You can't request more than 7 LED Values")
        self.ledIndices = ledIndices

    def encode(self):
        numLEDs = len(self.ledIndices)
        maxLEDbytes = 7

        # Extract the values of LEDs
        ledIndexBytes = b''
        for ledIndex in self.ledIndices:
            ledIndexBytes += struct.pack('>B', ledIndex)

        # numGarbageBytes = len(ledIndexBytes)+1
        #numGarbageBytes = (maxLEDbytes-len(ledIndexBytes))+8
        #garbage = b'00'*numGarbageBytes

        stringFormat = Formatting.CommandData.GetLED.format(numLEDs, 0)
        commandDataString = struct.pack(stringFormat, numLEDs, ledIndexBytes)
        return commandDataString

###################################################################################


class NebSetLEDCommandData(object):
    """ Neblina LED settings command data

        Formatting:
        - Number of LEDs (defines the number of index/value pair to be use)
        - LED Index (one for each LEDs)
        - LED Value (one for each LEDs)
    """
    def __init__(self, ledValueTupleList):
        if(len(ledValueTupleList) > 7):
            raise InvalidPacketFormatError("The packet can't hold more than 7 LED Values")
        self.ledValues = ledValueTupleList

    def encode(self):
        numLEDs = len(self.ledValues)
        bytesPerLED = 2
        maxLEDbytes = 14

        # Extract the values of LEDs
        ledValueBytes = b''
        for ledTuple in self.ledValues:
            ledValueBytes += struct.pack('>BB', \
                ledTuple[0], ledTuple[1])

        # numGarbageBytes = len(ledValueBytes)+1
        #numGarbageBytes = (maxLEDbytes-len(ledValueBytes))+1
        #garbage = b'00'*numGarbageBytes

        stringFormat = Formatting.CommandData.SetLED.format(numLEDs*bytesPerLED,\
         0)
        commandDataString = struct.pack(\
            stringFormat, numLEDs, ledValueBytes)
        return commandDataString

###################################################################################


class NebEEPROMCommandData(object):
    """ Neblina EEPROM command data

        Formatting:
        - Page number
        - 8 bytes R/W data
    """
    def __init__(self, readWrite, pageNumber, dataBytes=b'00'*8):
        self.readWrite = readWrite # read = False, write = True
        self.pageNumber = pageNumber
        self.dataBytes = dataBytes

    def encode(self):
        #garbage = b'00'*6
        commandDataString = struct.pack(Formatting.CommandData.EEPROM,\
            self.pageNumber, self.dataBytes)
        return commandDataString

###################################################################################


class NebDataPortState(object):
    """ Neblina data port status

        Formatting:
        - Data port ID
        - Open/Close
    """
    def __init__(self, openClose, portID ):
        self.portID = portID
        self.openClose = openClose

    def __str__(self):
        string = 'open' if self.openClose else 'close'
        return "DataPortState Command {0}: {1}"\
        .format(self.portID, string)

    def encode(self):
        openCloseVal = 1 if self.openClose else 0
        commandDataString = struct.pack(Formatting.CommandData.SetDataPortState, \
                                        self.portID, openCloseVal)
        return commandDataString

###################################################################################