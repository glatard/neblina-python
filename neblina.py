#!/usr/bin/env python
###################################################################################
# @package neblina

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


class BitMask:
    """
        BitMask pattern for packet header decoding
    """
    SubSystem = 0x1F
    PacketType = 0xE0

###################################################################################


class BitPosition:
    """
        Bit position for packet header decoding
    """
    PacketType = 5

###################################################################################


class Interface:
    """
        Neblina communication interface
    """
    BLE = 0x00      # Bluetooth Smart (Low Energy)
    UART = 0x01     # Serial

###################################################################################


class PacketType:
    """
        Neblina packet type
    """
    RegularResponse = 0x00
    Ack = 0x01
    Command = 0x02
    ErrorLogResp = 0x04
    ErrorLogCmd = 0x06

    class String:
        RegularResponse = "RegularResponse"
        Ack = "Acknowledge"
        Command = "Command"
        ErrorLogResp = "Error Response"
        ErrorLogCmd = "Error Command"

###################################################################################


class SubSystem:
    """
        Neblina subsystem
    """
    Debug = 0x00
    Motion = 0x01
    Power = 0x02
    DigitalIO = 0x03
    LED = 0x04
    ADC = 0x05
    DAC = 0x06
    I2C = 0x07
    SPI = 0x08
    Firmware = 0x09
    Crypto = 0x0A
    Storage = 0x0B
    EEPROM = 0x0C
    Sensor = 0x0D

###################################################################################


class Erase:
    """
        Neblina storage erase type
    """
    Quick = 0x00
    Mass = 0x01

###################################################################################


class Commands:
    """
        Neblina commands for various subsystem
    """

    class Debug:
        """
            Neblina debug commands
        """
        SetInterface = 0x01
        MotAndFlashRecState = 0x02
        StartUnitTestMotion = 0x03
        UnitTestMotionData = 0x04
        FWVersions = 0x05
        InterfaceState = 0x09
        RSSI = 0x07
        disableAllStream = 0x0C

    class Power:
        """
            Neblina power management commands
        """
        GetBatteryLevel = 0x00
        GetTemperature = 0x01

    class Motion:
        """
            Neblina motion engin commands
        """
        Downsample = 0x01  # Downsampling factor definition
        MotionState = 0x02  # streaming Motion State
        IMU = 0x03  # streaming the 6-axis IMU data
        Quaternion = 0x04  # streaming the quaternion data
        EulerAngle = 0x05  # streaming the Euler angles
        ExtForce = 0x06  # streaming the external force
        SetFusionType = 0x07  # setting the Fusion type to either 6-axis or 9-axis
        TrajectoryRecStartStop = 0x08  # start recording orientation trajectory
        TrajectoryInfo = 0x09  # calculating the distance from a pre-recorded orientation trajectory
        Pedometer = 0x0A  # streaming pedometer data
        MAG = 0x0B  # streaming magnetometer data
        SittingStanding = 0x0C  # streaming sitting standing
        AccRange = 0x0E  # set accelerometer range
        DisableStreaming = 0x0F  # disable everything that is currently being streamed
        ResetTimeStamp = 0x10  # Reset timestamp
        FingerGesture = 0x11  # Finger Gesture command
        RotationInfo = 0x12  # Rotation info in roll: number of rotations and speed in rpm
        MotionCount = 0x13  # Keep last with next value

    class Storage:
        """
            Neblina storage commands
        """
        EraseAll = 0x01  # Full-erase for the on-chip NOR flash memory
        Record = 0x02  # Either start a new recording session, or close the currently open one
        Playback = 0x03  # Open a previously recorded session for playback or close currently opened and being played
        NumSessions = 0x04  # Get Number of sessions currently on the flash storage
        SessionInfo = 0x05  # Get information associated with a particular session

    class EEPROM:
        """
            Neblina EEPROM commands
        """
        Read = 0x01  # Read a page
        Write = 0x02  # Write to a page

    class DigitalIO:
        """
            Neblina Digital IO (DEPRECATED)
        """
        SetConfig = 0x01
        GetConfig = 0x02
        SetValue = 0x03
        GetValue = 0x04
        NotifySet = 0x05
        NotifyEvent = 0x06

    class Firmware:
        """
            Neblina firmware commands (DEPRECATED)
        """
        Main = 0x01
        BLE = 0x02

    class LED:
        """
            Neblina LED commands
        """
        SetVal = 0x01
        GetVal = 0x02
        Config = 0x03

    class BLE:
        """
            Neblina BLE commands (DEPRECATED)
        """
        Receive = 0x01

    class Sensor:
        """
            Neblina Sensor commands
        """
        AccGyr = 0x10
        AccMag = 0x11
        Mag    = 0x0D
        SensorRange = 0x01
        SensorTypeAccel = 0x00
        SensorTypeGyro  = 0x01
        SensorTypeMAG   = 0x02

###################################################################################


CommandStrings = {
    (SubSystem.Debug, Commands.Debug.SetInterface): 'Set Interface',
    (SubSystem.Debug, Commands.Debug.MotAndFlashRecState): 'Check Motion and Flash Recorder States',
    (SubSystem.Debug, Commands.Debug.StartUnitTestMotion): 'Enable/Disable Unit Test Motion',
    (SubSystem.Debug, Commands.Debug.UnitTestMotionData): 'Unit Test Data',
    (SubSystem.Debug, Commands.Debug.FWVersions): 'Firmware Versions',
    (SubSystem.Debug, Commands.Debug.RSSI): 'Firmware Versions',
    (SubSystem.Debug, Commands.Debug.disableAllStream): 'Disable All Streaming',
    (SubSystem.Motion, Commands.Motion.Downsample): 'Downsample',
    (SubSystem.Motion, Commands.Motion.MotionState): 'MotionState',
    (SubSystem.Motion, Commands.Motion.IMU): 'IMU Data',
    (SubSystem.Motion, Commands.Motion.Quaternion): 'Quaternion',
    (SubSystem.Motion, Commands.Motion.EulerAngle): 'Euler Angle',
    (SubSystem.Motion, Commands.Motion.ExtForce): 'ExtForce',
    (SubSystem.Motion, Commands.Motion.SetFusionType): 'SetFusionType',
    (SubSystem.Motion, Commands.Motion.TrajectoryRecStartStop): 'Trajectory Record Start',
    (SubSystem.Motion, Commands.Motion.TrajectoryInfo): 'Trajectory Distance',
    (SubSystem.Motion, Commands.Motion.Pedometer): 'Pedometer',
    (SubSystem.Motion, Commands.Motion.MAG): 'MAG Data',
    (SubSystem.Motion, Commands.Motion.SittingStanding): 'Sitting-Standing',
    (SubSystem.Motion, Commands.Motion.AccRange): 'AccRange',
    (SubSystem.Motion, Commands.Motion.DisableStreaming): 'Disable Streaming',
    (SubSystem.Motion, Commands.Motion.ResetTimeStamp): 'Reset Timestamp',
    (SubSystem.Motion, Commands.Motion.FingerGesture): 'Finger Gesture',
    (SubSystem.Motion, Commands.Motion.RotationInfo): 'Rotation Info',
    (SubSystem.Power, Commands.Power.GetBatteryLevel): 'Battery Level',
    (SubSystem.Power, Commands.Power.GetTemperature): 'Board Temperature',
    (SubSystem.DigitalIO, Commands.DigitalIO.SetConfig): 'Set Config',
    (SubSystem.DigitalIO, Commands.DigitalIO.GetConfig): 'Get Config',
    (SubSystem.DigitalIO, Commands.DigitalIO.SetValue): 'Set Value',
    (SubSystem.DigitalIO, Commands.DigitalIO.GetValue): 'Get Value',
    (SubSystem.DigitalIO, Commands.DigitalIO.NotifySet): 'Notify Set',
    (SubSystem.DigitalIO, Commands.DigitalIO.NotifyEvent): 'Notify Event',
    (SubSystem.LED, Commands.LED.SetVal): 'LED Set Value',
    (SubSystem.LED, Commands.LED.GetVal): 'LED Read Value',
    (SubSystem.LED, Commands.LED.Config): 'LED Config',
    (SubSystem.ADC, 0): 'ADC Command',
    (SubSystem.DAC, 0): 'DAC Command',
    (SubSystem.I2C, 0): 'I2C Command',
    (SubSystem.SPI, 0): 'SPI Command',
    (SubSystem.Firmware, Commands.Firmware.Main): 'Main Firmware',
    (SubSystem.Firmware, Commands.Firmware.BLE): 'Nordic Firmware',
    (SubSystem.Crypto, 0): 'Crypto Command',
    (SubSystem.Storage, Commands.Storage.EraseAll): 'Erase All',
    (SubSystem.Storage, Commands.Storage.Record): 'Record',
    (SubSystem.Storage, Commands.Storage.Playback): 'Playback',
    (SubSystem.Storage, Commands.Storage.NumSessions): 'Num Sessions',
    (SubSystem.Storage, Commands.Storage.SessionInfo): 'Session ID',
    (SubSystem.EEPROM, Commands.EEPROM.Read): 'Read',
    (SubSystem.EEPROM, Commands.EEPROM.Write): 'Write',
    (SubSystem.Sensor, Commands.Sensor.AccGyr): 'Accelerometer Gyroscope Data',
    (SubSystem.Sensor, Commands.Sensor.AccMag): 'Accelerometer Magnetometer Data',
    (SubSystem.Sensor, Commands.Sensor.Mag): 'Magnetometer Data',
}

###################################################################################

# Dictionary containing the string descriptors of each command

###################################################################################


class Formatting:

    class Data:
        Blank = "<17s"  # Blank 17 bytes
        MotionAndFlash = "<4s B"  # downsample factor
        EEPROMRead = "<H 8s"  # Page number, 8 bytes Read Data
        LEDGetVal = "<B B B B B B B B"  # 8 LEDs values
        BatteryLevel = "<H"  # Battery Level (%)
        Temperature = "<h"  # Temperature x100 in Celsius
        FlashNumSessions = "<H"  # number of sessions
        FWVersions = "<B 3B 3B 8s"  # API Release, MCU Major/Minor/Build, BLE Major/Minor/Build, Device ID
        RSSI = "<I b>" #Timestamp, RSSI
        UnitTestMotion = "<B 3h 3h 3h 4h 3h 3h 3h H B I I h B I I"
        MotionState = "<I B"  # Timestamp, start/stop
        ExternalForce = "<I 3h"  # Timestamp, External force xyz
        TrajectoryDistance = "<I 3h H B"  # Timestamp, Euler angle errors, repeat count, completion percentage
        Pedometer = "<I H B h I 2H"  # Timestamp, stepCount, stepsPerMinute, walking direction, toe-off timestamp, stairs up count, stairs down count
        FingerGesture = "<I B"  # Timestamp, swipe pattern
        RotationInfo = "<I I H"  # Timestamp, rotationCount, rpm speed
        Quaternion = "<I 4h"  # Timestamp, quaternion
        IMU = "<I 3h 3h"  # Timestamp, accelerometer(xyz), gyroscope(xyz)
        ACCMAG = "<I 3h 3h"  # Timestamp, magnetometer(xyz), accelerometer(xyz)
        MAG = "<I 3h"  # Timestamp, magnetometer(xyz)
        Euler = "<I 3h"  # Timestamp, Euler angle (yaw,pitch,roll)
        FlashSessionInfoResponse = "<I H" # session length, session ID

    class CommandData:
        Header = "<4B"
        Command = "<B"  # enable/disable
        SensorRange = "<H H" # sensor type, sensor range
        FlashSession = "<B H"  # open/close, session ID
        FlashSessionInfo = "<H"  # session length, session ID
        UnitTestMotion = "<3h 3h 3h"  # accel, gyro, mag
        AccRange = "<H"  # downsample factor
        Downsample = "<H"  # downsample factor
        GetLED = "<B {0}s {1}s"  # Number of LEDs, LED Index x LEDs, LED Value x LEDs
        SetLED = "<B B"  # LED Index x LEDs, LED Value x LEDs
        EEPROM = "<H 8s"  # Page number, 8 bytes R/W Data
        SetDataPortState = "<B B"  # Port ID, Open/Close
