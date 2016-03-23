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

try:
    from bluepy.btle import *
except ImportError:
    print("Unable to locate bluepy. It is a required module to use neblinaBLE API.")

from neblina import *
from neblinaAPIBase import NeblinaAPIBase
from neblinaResponsePacket import NebResponsePacket

###################################################################################

ServiceBatteryUUID = "0000180f-0000-1000-8000-00805f9b34fb"
ServiceBatteryDataUUID = "00002a19-0000-1000-8000-00805f9b34fb"

ServiceNeblinaUUID = "0DF9F021-1532-11E5-8960-0002A5D5C51B"
ServiceNeblinaCtrlUUID = "0DF9F023-1532-11E5-8960-0002A5D5C51B"
ServiceNeblinaDataUUID = "0DF9F022-1532-11E5-8960-0002A5D5C51B"

###################################################################################


class NeblinaDelegate(DefaultDelegate):

    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print("handleNotification")
        pass

###################################################################################


class NeblinaDevice(object):

    def __init__(self, address):
        self.address = address
        self.connected = False
        self.connect(self.address)

    def connect(self, deviceAddress):
        connected = False
        peripheral = None
        count = 0
        while(not connected and count < 5):
            count += 1
            try:
                peripheral = Peripheral(deviceAddress, "random")
                connected = True
                break
            except BTLEException as e:
                logging.warning("Unable to connect to BLE device, retrying in 1 second.")
            time.sleep(1)

        if connected:
            self.peripheral = peripheral
            self.peripheral.setDelegate(NeblinaDelegate())
            self.connected = True

            self.serviceBattery = self.peripheral.getServiceByUUID(ServiceBatteryUUID)
            self.readBatteryCh = self.serviceBattery.getCharacteristics(ServiceBatteryDataUUID)[0]

            self.serviceNeblina = self.peripheral.getServiceByUUID(ServiceNeblinaUUID)
            self.writeNeblinaCh = self.serviceNeblina.getCharacteristics(ServiceNeblinaCtrlUUID)[0]
            self.readNeblinaCh = self.serviceNeblina.getCharacteristics(ServiceNeblinaDataUUID)[0]

    def disconnect(self):
        if self.connected:
            self.peripheral.disconnect()

    def printInfo(self, peripheral):
        print("Printing peripheral information.")
        services = list(peripheral.getServices())
        for x in range(0, len(services)):
            service = services[x]
            print(str(service))

            ch = list(service.getCharacteristics())
            for y in range(0, len(ch)):
                print("    " + str(ch[y]))

    def readBattery(self):
        batteryLevel = self.readBatteryCh.read()
        return struct.unpack("<B", batteryLevel)[0]

    def readNeblina(self):
        return self.readNeblinaCh.read()

    def writeNeblina(self, string):
        self.writeNeblinaCh.write(string)

###################################################################################


class NeblinaBLE(NeblinaAPIBase):
    """
        NeblinaBLE is the Neblina Bluetooth Low Energy (BLE) Application Program Interface (API)
    """

    def __init__(self):
        super(NeblinaBLE, self).__init__()
        self.devices = []

    def close(self, deviceAddress=None):
        logging.info("Disconnected from BLE device : " + deviceAddress)
        device = self.getDevice(deviceAddress)
        device.disconnect()

    def open(self, deviceAddress):
        device = NeblinaDevice(deviceAddress)
        if device.connected:
            logging.info("Successfully connected to BLE device : " + deviceAddress)
            self.devices.append(device)
        else:
            logging.warning("Unable to connect to BLE Device : " + deviceAddress)

    def closeAll(self):
        for device in self.devices:
            self.close(device.address)

    def getDevice(self, deviceAddress=None):
        if deviceAddress:
            for device in self.devices:
                if device.address == deviceAddress:
                    return device
            logging.warning("Device not found : " + deviceAddress)
            return None
        else:
            for device in self.devices:
                if device.connected:
                    return device
            logging.warning("No device is connected.")
            return None

    def isOpened(self, deviceAddress=None):
        device = self.getDevice(deviceAddress)
        return device and device.connected

    def sendCommand(self, packetString):
        device = self.getDevice()
        if device and device.connected:
            device.writeNeblina(packetString)

    def receivePacket(self):
        device = self.getDevice()
        if device and device.connected:
            bytes = device.readNeblina()
            packet = NebResponsePacket(bytes)
            return packet
        return None

    def getBatteryLevel(self):
        device = self.getDevice()
        if device and device.connected:
            bytes = device.readBattery()
            return bytes
        return None

