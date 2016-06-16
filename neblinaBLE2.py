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
import queue

from neblinaCommunication import NeblinaCommunication

try:
    from bluepy.btle import *
except ImportError:
    raise ImportError("Unable to locate bluepy. It is a required module to use neblinaBLE API.")

###################################################################################

ServiceBatteryUUID = "0000180f-0000-1000-8000-00805f9b34fb"
ServiceBatteryDataUUID = "00002a19-0000-1000-8000-00805f9b34fb"

ServiceNeblinaUUID = "0DF9F021-1532-11E5-8960-0002A5D5C51B"
ServiceNeblinaCtrlUUID = "0DF9F023-1532-11E5-8960-0002A5D5C51B"
ServiceNeblinaDataUUID = "0DF9F022-1532-11E5-8960-0002A5D5C51B"

###################################################################################


class BLEDelegate(DefaultDelegate):

    def __init__(self):
        DefaultDelegate.__init__(self)
        self.packets = queue.Queue()

    def handleNotification(self, cHandle, data):
        self.packets.put(data)
        logging.debug("handleNotification : {0}".format(data))

###################################################################################


class NeblinaBLE2(NeblinaCommunication):

    def __init__(self, address):
        NeblinaCommunication.__init__(self, address)
        self.connected = False
        self.delegate = BLEDelegate()
        self.peripheral = None

        self.serviceBattery = None
        self.readBatteryCh = None

        self.serviceNeblina = None
        self.writeNeblinaCh = None
        self.readNeblinaCh = None

    def connect(self):
        logging.debug("Opening BLE address : {0}".format(self.address))
        connected = False
        peripheral = None
        count = 0
        while not connected and count < 5:
            count += 1
            try:
                peripheral = Peripheral(self.address, "random")
                connected = True
                break
            except BTLEException as e:
                logging.warning("Unable to connect to BLE device, retrying in 1 second.")
            time.sleep(1)

        if connected:
            self.connected = True
            self.peripheral = peripheral

            self.serviceBattery = self.peripheral.getServiceByUUID(ServiceBatteryUUID)
            self.readBatteryCh = self.serviceBattery.getCharacteristics(ServiceBatteryDataUUID)[0]

            self.serviceNeblina = self.peripheral.getServiceByUUID(ServiceNeblinaUUID)
            self.writeNeblinaCh = self.serviceNeblina.getCharacteristics(ServiceNeblinaCtrlUUID)[0]
            self.readNeblinaCh = self.serviceNeblina.getCharacteristics(ServiceNeblinaDataUUID)[0]

            self.peripheral.withDelegate(self.delegate)
            self.enableNeblinaNotification()

    def disconnect(self):
        logging.debug("Closing BLE address : {0}".format(self.address))
        if self.connected:
            try:
                self.disableNeblinaNotification()
                self.peripheral.disconnect()
            except BrokenPipeError:
                pass
            self.connected = False

    def isConnected(self):
        return self.connected

    def getBatteryLevel(self):
        if self.connected:
            batteryLevel = self.readBatteryCh.read()
            return struct.unpack("<B", batteryLevel)[0]

        return None

    def receivePacket(self):
        self.peripheral.waitForNotifications(None)
        if not self.delegate.packets.empty():
            data = self.delegate.packets.get(False)
            return data
        else:
            return None

    def sendPacket(self, packet):
        try:
            self.writeNeblinaCh.write(packet)
        except BTLEException as e:
            logging.error("BTLEException : {0}".format(e))
        except BrokenPipeError:
            return

    def enableNeblinaNotification(self):
        self.peripheral.writeCharacteristic(self.readNeblinaCh.handle + 2, struct.pack('<bb', 0x01, 0x00))

    def disableNeblinaNotification(self):
        self.peripheral.writeCharacteristic(self.readNeblinaCh.handle + 2, struct.pack('<bb', 0x00, 0x00))

