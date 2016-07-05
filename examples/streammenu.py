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

from __future__ import print_function
import os
import cmd
import getopt
import signal
import sys
import time
import logging

from neblina import *
from neblinaAPI import NeblinaAPI

###################################################################################


class GracefulKiller:
    isKilled = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, signum, frame):
        #print("Signal received: {0}.".format(signum))
        self.isKilled = True

###################################################################################


class StreamMenu(cmd.Cmd):
    """docstring for StreamMenu"""

    def __init__(self, address):
        cmd.Cmd.__init__(self)
        self.signalKiller = GracefulKiller()

        self.bigLine = '-------------------------------------------------------------------\n'
        self.prompt = '>>'
        self.intro = "Welcome to the Neblina Streaming Menu!"

        self.api = NeblinaAPI(Interface.UART)
        print("Setting up the connection...")  # initial delay needed for the device to synchronize its processors
        time.sleep(1)
        print('.')
        time.sleep(1)
        print('.')
        time.sleep(1)
        print('.')
        self.api.open(address)
        global initialmotionstate  # the global variable that stores the initial motion engine state
        initialmotionstate = self.api.getMotionStatus()  # get the initial motion engine state
        self.api.streamDisableAll()  # disable all streaming options after storing the initial state
        self.api.setDataPortState(Interface.BLE, False)  # Close BLE streaming to prevent slowed streaming
        self.api.setDataPortState(Interface.UART, True)  # Open UART streaming


    # If the user exits with Ctrl-C, try switching the interface back to BLE
    def cmdloop(self, intro=None):
        try:
            cmd.Cmd.cmdloop(self)
        except KeyboardInterrupt as e:
            self.api.setDataPortState(Interface.BLE, True)

    ## Command definitions ##
    def do_hist(self, args):
        """Print a list of commands that have been entered"""
        print(self._hist)

    def do_exit(self, args):
        """Exits from the console"""

        # Set the motion engine state back to its initial state by enabling the appropriate streaming features
        print('Setting the motion engine back to its initial state...')
        if initialmotionstate.distance:
            self.api.streamTrajectoryInfo(True)
        if initialmotionstate.force:
            self.api.streamExternalForce(True)
        if initialmotionstate.euler:
            self.api.streamEulerAngle(True)
        if initialmotionstate.quaternion:
            self.api.streamQuaternion(True)
        if initialmotionstate.imuData:
            self.api.streamIMU(True)
        if initialmotionstate.motion:
            self.api.streamMotionState(True)
        if initialmotionstate.steps:
            self.api.streamPedometer(True)
        if initialmotionstate.magData:
            self.api.streamMAG(True)
        if initialmotionstate.sitStand:
            self.api.streamSittingStanding(True)

        # Make the module stream back towards its default interface (BLE)
        self.api.setDataPortState(Interface.BLE, True)
        return -1

    ## Command definitions to support Cmd object functionality ##
    def do_EOF(self, args):
        """Exit on system end of file character"""
        return self.do_exit(args)

    def do_shell(self, args):
        """Pass command to a system shell when line begins with '!'"""
        os.system(args)

    def do_help(self, args):
        """Get help on commands
           'help' or '?' with no arguments prints a list of commands for which help is available
           'help <command>' or '? <command>' gives help on <command>
        """
        ## The only reason to define this method is for the help text in the doc string
        cmd.Cmd.do_help(self, args)

    def do_EEPROMWrite(self, args):
        arguments = args.split(' ')

        if len(arguments) < 2:
            print('EEPROMWrite <pageNumber> <8-byte string>')
            return
        if len(arguments[1]) > 8:
            print('The data string must less than 8 bytes')
            return
        arguments[1] = arguments[1].rjust(8) # Pad the string to 8 bytes
        writeBytes = arguments[1].encode('utf-8')
        writePageNumber = int(arguments[0])
        if writePageNumber < 0 or writePageNumber > 255:
            print('Page number must be between 0 and 255 inclusively')
            return

        self.api.eepromWrite(writePageNumber, writeBytes)

        print('Write to page #{0} of dataBytes {1} was successful.'\
            .format(writePageNumber, writeBytes))

    def do_EEPROMRead(self, args):
        arguments = args.split(' ')
        print(arguments)
        print(len(arguments))
        if (arguments[0]) == '' or len(arguments) != 1:
            print('EEPROMRead <pageNumber>')
            return

        readPageNumber = int(arguments[0])
        if readPageNumber < 0 or readPageNumber > 255:
            print('Page number must be between 0 and 255 inclusively')
            return

        dataBytes = self.api.eepromRead(readPageNumber)

        try:
            print('Got \'{0}\' at page #{1}'.format(dataBytes.decode('utf-8'), readPageNumber))
        except UnicodeDecodeError as ude:
            print('Got {0} at page #{1}'.format(dataBytes, readPageNumber))

    def do_getMotionStatus(self, args):
        states = self.api.getMotionStatus()
        print("Distance: {0}\nForce:{1}\nEuler:{2}\nQuaternion:{3}\nIMUData:{4}\nMotion:{5}\nSteps:{6}\nMAGData:{7}\nSitStand:{8}"\
        .format(states.distance, states.force, states.euler, states.quaternion,\
                states.imuData, states.motion, states.steps, states.magData, states.sitStand))

    def do_getBatteryLevel(self, args):
        batteryLevel = self.api.getBatteryLevel()
        print('Battery Level: {0}%'.format(batteryLevel))

    def do_getTemperature(self, args):
        temp = self.api.getTemperature()
        print('Board Temperature: {0} degrees (Celsius)'.format(temp))

    def do_streamEuler(self, args):
        self.api.streamEulerAngle(True)
        while not self.signalKiller.isKilled:
            print(self.api.getEulerAngle())
        self.api.streamEulerAngle(False)

    def do_streamIMU(self, args):
        self.api.streamIMU(True)
        while not self.signalKiller.isKilled:
            print(self.api.getIMU())
        self.api.streamIMU(False)

    def do_streamQuat(self, args):
        self.api.streamQuaternion(True)
        while not self.signalKiller.isKilled:
            print(self.api.getQuaternion())
        self.api.streamQuaternion(False)

    def do_streamMAG(self, args):
        self.api.streamMAG(True)
        while not self.signalKiller.isKilled:
            print(self.api.getMAG())
        self.api.streamMAG(False)

    def do_streamForce(self, args):
        self.api.streamExternalForce(True)
        while not self.signalKiller.isKilled:
            print(self.api.getExternalForce())
        self.api.streamExternalForce(False)

    def do_streamRotation(self, args):
        self.api.streamRotationInfo(True)
        while not self.signalKiller.isKilled:
            print(self.api.getRotationInfo())
        self.api.streamRotationInfo(False)

    def do_streamPedometer(self, args):
        self.api.streamPedometer(True)
        while not self.signalKiller.isKilled:
            print(self.api.getPedometer())
        self.api.streamPedometer(False)

    def do_streamGesture(self, args):
        self.api.streamFingerGesture(True)
        while not self.signalKiller.isKilled:
            print(self.api.getFingerGesture())
        self.api.streamFingerGesture(False)

    def do_streamTrajectoryInfo(self, args):
        self.api.streamTrajectoryInfo(True)
        while not self.signalKiller.isKilled:
            print(self.api.getTrajectoryInfo())
        self.api.streamTrajectoryInfo(False)

    def do_streamDisableAll(self, args):
        self.api.stream()

    def do_resetTimestamp(self, args):
        self.api.motionResetTimestamp()

    def do_downsample(self, args):
        if(len(args) <= 0):
            print('The argument should be a multiplicand of 20, i.e., 20, 40, 60, etc!')
            return
        n = int(args)
        if ((n % 20)!=0):
            print('The argument should be a multiplicand of 20, i.e., 20, 40, 60, etc!')
            return
        self.api.motionSetDownsample(n)

    def do_setAccFullScale(self, args):
        possibleFactors = [2,4,8,16]
        if(len(args) <= 0):
            print('The argument should be 2, 4, 8, or 16, representing the accelerometer range in g')
            return
        factor = int(args)
        if(factor not in possibleFactors):
            print('The argument should be 2, 4, 8, or 16, representing the accelerometer range in g')
            return
        self.api.motionSetAccFullScale(factor)

    def do_setled(self, args):
        arguments = args.split(' ')
        if len(arguments) != 2:
            print('setled <ledNumber> <value>')
            return
        ledIndex = int(arguments[0])
        ledValue = int(arguments[1])
        if(ledIndex < 0 or ledIndex > 1):
            print('Only led indices 0 or 1 are valid')
            return
        self.api.setLED(ledIndex, ledValue)

    def do_flashState(self, args):
        state = self.api.flashGetState()
        print('State: {0}'.format(state))
        sessions = self.api.getSessionCount()
        print('Num of sessions: {0}'.format(sessions))

    def do_flashSessionInfo(self, args):
        if(len(args) <= 0):
            sessionID = 65535
        elif(len(args) > 0):
            sessionID = int(args)
        packet = self.api.getSessionInfo(sessionID)
        if(packet == None):
            print('Session {0} does not exist on the flash'\
                .format(sessionID))
        else:
            print( "Session %d: %d packets (%d bytes)"\
            %(packet.sessionID, packet.sessionLength, packet.sessionLengthBytes) )

    def do_flashErase(self, args):
        self.api.eraseStorage()
        print('Flash erase has completed successfully!')

    def do_flashRecordIMU(self, args):
        if(len(args) <= 0):
            numSamples = 1000
        else:
            numSamples = int(args)
        self.api.flashRecord(numSamples, Commands.Motion.IMU)

    def do_flashRecordEuler(self, args):
        if(len(args) <= 0):
            numSamples = 1000
        else:
            numSamples = int(args)
        self.api.flashRecord(numSamples, Commands.Motion.EulerAngle)

    def do_flashRecordQuaternion(self, args):
        if(len(args) <= 0):
            numSamples = 1000
        else:
            numSamples = int(args)
        self.api.flashRecord(numSamples, Commands.Motion.Quaternion)

    def do_flashPlayback(self, args):
        arguments = args.split(' ')
        if(len(args) <= 0):
            mySessionID = 65535
            dump = False
        elif(len(arguments) == 1):
            mySessionID = int(arguments[0])
            dump = False
        elif(len(arguments) >= 2 ):
            mySessionID = int(arguments[0])
            if arguments[1] == 'True' or arguments[1] == '1':
                dump = True
            else:
                dump = False
        self.api.sessionPlayback(mySessionID, dump)

    def do_versions(self, args):
        packet = self.api.getFirmwareVersions()
        apiRelease = packet.apiRelease
        mcuFWVersion = packet.mcuFWVersion
        bleFWVersion = packet.bleFWVersion
        deviceID = packet.deviceID
        print(packet)

    ## Override methods in Cmd object ##
    def preloop(self):
        """Initialization before prompting user for commands.
           Despite the claims in the Cmd documentaion, Cmd.preloop() is not a stub.
        """
        cmd.Cmd.preloop(self)   ## sets up command completion
        self._hist    = []      ## No history yet
        self._locals  = {}      ## Initialize execution namespace for user
        self._globals = {}

    def postloop(self):
        """Take care of any unfinished business.
           Despite the claims in the Cmd documentaion, Cmd.postloop() is not a stub.
        """
        self.api.close()
        cmd.Cmd.postloop(self)   ## Clean up command completion
        print ("Exiting...")

    def precmd(self, line):
        """ This method is called after the line has been input but before
            it has been interpreted. If you want to modify the input line
            before execution (for example, variable substitution) do it here.
        """
        # This is added to ensure that the pending bytes in the COM buffer are discarded for each new command.
        # This is crucial to avoid missing Acknowledge packets in the beginning, if Neblina is already streaming.
        self._hist += [ line.strip() ]
        return line

    def postcmd(self, stop, line):
        """If you want to stop the console, return something that evaluates to true.
           If you want to do some post command processing, do it here.
        """
        self.signalKiller.isKilled = False
        return stop

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def default(self, line):
        """Called on an input line when the command prefix is not recognized.
           In that case we execute the line as Python code.
        """
        try:
            exec(line) in self._locals, self._globals
        except Exception as e:
            print (e.__class__, ":", e)

###################################################################################


def printArguments():
    print("Neblina stream menu")
    print("Copyright Motsai 2010-2016")
    print("")
    print("Neblina commands:")
    print("    -h --help   : Display available commands.")
    print("    -a --address: Device address to use (COM port)")

###################################################################################


if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:")
    except getopt.GetoptError:
        printArguments()
        sys.exit()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printArguments()
            sys.exit()
        elif opt in ("-a", "--address"):
            console = StreamMenu(arg)
            console.cmdloop()
            sys.exit()

    print("No device address specified. Exiting.")
