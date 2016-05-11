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
import threading
import socket

try:
    from bluepy.btle import *
except ImportError:
    raise ImportError("Unable to locate bluepy. It is a required module to use neblinaBLE API.")

from neblina import *
from neblinaAPIBase import NeblinaAPIBase
from neblinaCommandPacket import NebCommandPacket
from neblinaError import *
from neblinaResponsePacket import NebResponsePacket

###################################################################################

ServiceBatteryUUID = "0000180f-0000-1000-8000-00805f9b34fb"
ServiceBatteryDataUUID = "00002a19-0000-1000-8000-00805f9b34fb"

ServiceNeblinaUUID = "0DF9F021-1532-11E5-8960-0002A5D5C51B"
ServiceNeblinaCtrlUUID = "0DF9F023-1532-11E5-8960-0002A5D5C51B"
ServiceNeblinaDataUUID = "0DF9F022-1532-11E5-8960-0002A5D5C51B"

###################################################################################


class NeblinaDelegate(DefaultDelegate):

    def __init__(self, device):
        DefaultDelegate.__init__(self)
        self.device = device
        self.packets = queue.Queue()

    def handleNotification(self, cHandle, data):
        self.packets.put(data)
        #logging.debug("Delegate - Received packet : {0}".format(data))

        # try:
        #     packet = NebResponsePacket(data)
        # except KeyError as e:
        #     print("KeyError : " + str(e))
        # except NotImplementedError as e:
        #     print("NotImplementedError : " + str(e))
        # except CRCError as e:
        #     print("CRCError : " + str(e))
        # except InvalidPacketFormatError as e:
        #     print("InvalidPacketFormatError : " + str(e))
        # except:
        #     logging.error("Unexpected error : ", exc_info=True)
        #
        # self.packet = packet
        # logging.debug("Delegate - Received packet : {0}".format(packet.data))

###################################################################################


class NeblinaDevice(object):

    def __init__(self, address):
        self.address = address
        self.connected = False
        self.delegate = NeblinaDelegate(self)

    def connect(self):
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
            self.peripheral = peripheral
            self.connected = True

            self.serviceBattery = self.peripheral.getServiceByUUID(ServiceBatteryUUID)
            self.readBatteryCh = self.serviceBattery.getCharacteristics(ServiceBatteryDataUUID)[0]

            self.serviceNeblina = self.peripheral.getServiceByUUID(ServiceNeblinaUUID)
            self.writeNeblinaCh = self.serviceNeblina.getCharacteristics(ServiceNeblinaCtrlUUID)[0]
            self.readNeblinaCh = self.serviceNeblina.getCharacteristics(ServiceNeblinaDataUUID)[0]

            self.peripheral.withDelegate(self.delegate)
            self.enableNeblinaNotification()

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

    def enableNeblinaNotification(self):
        self.peripheral.writeCharacteristic(self.readNeblinaCh.handle+2, struct.pack('<bb', 0x01, 0x00))

    def disableNeblinaNotification(self):
        self.peripheral.writeCharacteristic(self.readNeblinaCh.handle+2, struct.pack('<bb', 0x00, 0x00))

    def readNeblina(self):
        return self.readNeblinaCh.read()

    def writeNeblina(self, string):
        self.writeNeblinaCh.write(string)

    def waitForNotification(self, timeout):
        return self.peripheral.waitForNotifications(timeout)

###################################################################################


class NeblinaCtrl(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.device = None
        self.isPause = False        # To ensure thread safety when accessing other characteristic then Neblina.
        self.stopRequested = False
        self.commandToSend = queue.Queue()

    def run(self):
        if not self.device:
            return

        while not self.stopRequested:
            if self.isPause:
                continue

            while not self.commandToSend.empty():
                command = self.commandToSend.get()
                self.device.writeNeblina(command)
            try:
                self.device.waitForNotification(0.01)
            except Exception:
                break

    def pause(self):
        self.isPause = True

    def unpause(self):
        self.isPause = False

    def stop(self):
        self.stopRequested = True
        self.join()
        self.device.disconnect()

    def setDevice(self, device):
        self.device = device

    def sendCommand(self, string):
        self.commandToSend.put(string)

###################################################################################


class NeblinaBLE(NeblinaAPIBase):
    """
        NeblinaBLE is the Neblina Bluetooth Low Energy (BLE) Application Program Interface (API)
    """

    def __init__(self):
        NeblinaAPIBase.__init__(self)
        self.ctrl = NeblinaCtrl()

    def close(self, deviceAddress=None):
        #self.stopEverything()
        self.ctrl.stop()
        logging.info("Disconnected from BLE device : " + deviceAddress)

    def open(self, deviceAddress):
        device = NeblinaDevice(deviceAddress)
        device.connect()
        self.ctrl.setDevice(device)
        self.ctrl.start()
        if device.connected:
            logging.info("Successfully connected to BLE device : " + deviceAddress)
            self.ctrl.setDevice(device)
        else:
            logging.warning("Unable to connect to BLE Device : " + deviceAddress)

    def isOpened(self, port=None):
        return self.ctrl.device and self.ctrl.device.connected

    def sendCommand(self, subSystem, command, enable=True, **kwargs):
        if self.ctrl.device and self.ctrl.device.connected:
            commandPacket = NebCommandPacket(subSystem, command, enable, **kwargs)
            self.ctrl.sendCommand(commandPacket.stringEncode())

    def sendCommandBytes(self, bytes):
        if self.ctrl.device and self.ctrl.device.connected:
            self.ctrl.sendCommand(bytes)

    def receivePacket(self):
        data = self.ctrl.device.delegate.packets.get()

        packet = None
        try:
            packet = NebResponsePacket(data)
            logging.debug(packet.data)
        except KeyError as e:
            logging.error("KeyError : {0}".format(str(e)))
        except NotImplementedError as e:
            logging.error("NotImplementedError : {0}".format(str(e)))
        except CRCError as e:
            logging.error("CRCError : " + str(e))
        except InvalidPacketFormatError as e:
            logging.error("InvalidPacketFormatError : {0]}".format(str(e)))
        except:
            logging.error("Unexpected error : ", exc_info=True)

        return packet

    def getBatteryLevel(self):
        if self.ctrl.device and self.ctrl.device.connected:
            self.ctrl.pause()
            bytes = self.ctrl.device.readBattery()
            self.ctrl.unpause()
            return bytes
        return None

    def flashRecord(self, numSamples, dataType):
        """
            This function can not be used for BLE communication due to inability to accurately count the number of
            samples recorded.

            Please use flashRecordStart and flashRecordStop.
        """
        assert False

    def flashPlayback(self, pbSessionID, destinationFileName=None):
        """
            This function can not be used for BLE communication due to the higher then normal throughput required to
            prevent same record-playback time span.

            Please use UART to use playback.
        """
        assert False
