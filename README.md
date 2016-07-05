[![Build Status](https://travis-ci.org/Motsai/neblina-python.svg)](https://travis-ci.org/Motsai/neblina-python)
# Neblina&trade; ProMotion Development Kit Python Scripts
![Python](/docs/img/python_logo.png)
![ProMotion Board](/docs/img/promotion.jpg)

## Neblina&trade;
The Neblina&trade; module is a low-power self-contained [AHRS](https://en.wikipedia.org/wiki/Attitude_and_heading_reference_system), [VRU](https://en.wikipedia.org/wiki/Inertial_measurement_unit) and [IMU](https://en.wikipedia.org/wiki/Inertial_measurement_unit) with [Bluetooth&reg; SMART](https://en.wikipedia.org/wiki/Bluetooth_low_energy) connectivity developed by Motsai. The miniature board built with the latest [HDI PCB](https://en.wikipedia.org/wiki/Microvia) technology, features a high-performance patent-pending sensor fusion algorithm on-board, that makes it perfect for [wearable technology devices](https://en.wikipedia.org/wiki/Wearable_technology) in applications such as [biomechanical analysis](https://en.wikipedia.org/wiki/Biomechanics), [sports performance analytics](https://en.wikipedia.org/wiki/Sports_biomechanics), remote [physical therapy](https://en.wikipedia.org/wiki/Physical_therapy) monitoring, [quantified self](https://en.wikipedia.org/wiki/Quantified_Self) , [health and fitness tracking](https://en.wikipedia.org/wiki/Activity_tracker), among others.

## ProMotion Development Kit
The [ProMotion Development Kit](http://promotion.motsai.com/) serves as a reference design for Neblina integration; adding storage, micro-USB port, battery, and I/O expansion to the Neblina. A NOR flash recorder and an EEPROM module are also included on the ProMotion board. The development kit with the extensive software support allows system integrators and evaluators to start development within minutes.

This repository is part of the development kit that provides a Python interface to interact with and simulate the behaviour of Neblina.

## Requirements
* python3
* pyserial
* bluepy (Linux-only)
* Windows 10 64-bit or Ubuntu 14.04 LTS 64-bit
* ProMotion board
* Micro USB cable

## ProMotion board hardware setup
Refer to the [Quick Start guide](http://nebdox.motsai.com/ProMotion_DevKit/Getting_Started) to learn about the hardware.

### Retrieve COM port name
In order to connect neblina to the computer, the COM port name is required. Follow these steps to retrieve the COM port name associated with Neblina, depending on your platform.

#### Windows
* Disconnect `ProMotion` from the computer, if already connected, and then turn it off.
* Prior to connecting `ProMotion`, open `Device Manager` and navigate to `Ports (COM & LTP)`.
* Connect `ProMotion` to the computer using the micro-USB port. Note that `ProMotion` should be turned off when plugging it into the computer.
* Monitor the change to the list of COM ports. The COM ports names follow the `COMx` pattern (where `x` is the associated COM port number)

#### Ubuntu 14.04 LTS
* Disconnect `ProMotion` from the computer, if already connected, and then turn it off.
* Prior to connecting `ProMotion`, execute the following command at the terminal.
```
$ ls /dev/ttyACM*
```
* Connect `ProMotion` to the computer using the micro-USB port. Note that `ProMotion` should be turned off when plugging it into the computer.
* Run `ls /dev/ttyACM*` again and find the change to the list of ports. The COM ports names follow the `/dev/ttyACMx` pattern (where `x` is the associated COM port number)
* It is required to give permissions to use the COM port. Set with the following command by replace `x` with the associated COM port number, and `<username>` by the currently logged in user:
```
$ chown <username> /dev/ttyACMx
```

### Running the unit tests (Linux-only, optional)
The unit tests allow for the validation of the decoding and encoding process of the packets transferred between the computer and the board. Make sure the pyslip submodule has been cloned (see below) and then you can run the unit tests by executing the script:
```
$ ./runNeblinaDataTests.sh
```

## Python Installation
It is suggested to install these dependencies in a virtual environment. More information [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

### Install the source locally
```
$ git clone https://github.com/Motsai/neblina-python.git
```
To be able to run interaction scripts, you must also instantiate the pyslip submodule:
```
$ git submodule init
$ git submodule update
```

### Ubuntu 14.04 LTS

#### Install dependencies:
On Linux here are the minimum requirements:
```
$ apt-get install python-pip
$ pip3 install pyserial
```
To be able to use Bluetooth Low Energy (BLE) on Linux, you must also install these dependencies:
```
$ apt-get install libglib2.0-dev
$ pip3 install bluepy
```

#### Include directories to the Python Environment
In order to include the directories required to run `neblina-python`, add the following lines at the end of `~/.bashrc` by replacing `/path/to/the/repo/` with the path where `neblina-python` folder is located:
```
$ export PYTHONPATH="${PYTHONPATH}:/path/to/the/repo/neblina-python"
```

It is recommended to run `source ~/.bashrc` to execute the file you just modify to apply the changes. Otherwise, you need to open a new shell.

### Windows
#### Include directories to the Python Environment
![Path](/docs/img/env_variables.png)

#### Install dependencies:
On Windows, you can first install [pip](https://pip.pypa.io/en/latest/installing/) and then simply try:
```
$ pip3 install pyserial
```
Note that if you are using Python 3.4 or higher, the pip is already installed on your machine. Currently, the BLE package is not available on Windows.


## How-to
### Execute Euler Angle streaming example using Bluetooth Low Energy (Linux-only):
```
python3 <base dir>/examples/streamEulerAngle.py -a <BLE Device's MAC Address>
```

The BLE device's MAC address can be found by opening the Bluetooth icon in the top panel on your Linux machine, and doing a scan over the available BLE devices. You can stop the streaming at any time by hitting Ctrl+C, otherwise it will continue streaming. 

The list of all available features that can be streamed to both BLE and USB interfaces is available on the Neblina firmware's [Release Notes](/docs/datasheets/ReleaseNotes.pdf).

### Execute the interaction shell:
The interactive shell currently supports only USB (not BLE). However, both Windows and Linux machines are supported. 
```
cd <base dir>/examples
python3 streammenu.py -a <>
```

On the execution of the shell script, the program will ask you for the name of the COM port to connect to. Type the name of the COM port associated with the module and press 'Enter'.

![Path](/docs/img/startup.png)

### Stream menu commands:
To explore different streaming features of the ProMotion board, run the stream menu shell script, and type "help" to see the available commands:
```
help
```
![Path](/docs/img/help.png)

Through the rest of this guide, we will go through a number of examples to explore the streaming features of the ProMotion board.


#### Example 1: stream quaternion orientation data
```
streamQuaternion
```
The quaternion data will then be streamed to the console. The information includes a timestamp in microseconds, which is followed by the four elements of a unit-length quaternion vector.
![Path](/docs/img/stream_quat.png)

You can stop the streaming at any time by hitting Ctrl+C.

#### Example 2: stream Euler angles
```
streamEulerAngle
```
This will stream the Yaw, Pitch and Roll angles in degrees using the aerospace rotation sequence, where Yaw takes place first, and is then followed by Pitch and Roll. The timestamp value in microseconds is also provided. The streaming can be stopped by hitting ctrl+C.

#### Example 3: stream raw sensor data
To stream the 3-axis accelerometer and gyroscope data:
```
streamIMU
```
To stream the 3-axis accelerometer and magnetometer data:
```
streamMAG
```

#### Example 4: get the battery level and temperature of the board
```
getBatteryLevel
getTemperature
```
![Path](/docs/img/get_battery.png)

#### Example 5: record motion data on chip
To record, and playback a specific motion feature:
```
eraseStorage //erase the on-chip recorder (optional)
sessionRecordQuaternion <number of samples> //by default, the streaming frequency is 50 Hz.
sessionPlayback <session ID> <dump to file option> //use the same session ID as returned by the record command
```

![Path](/docs/img/record_data.png)

Note from the above snapshot that the session ID "0" has been returned after the recording is issued. Consequently, the playback command should define the session ID "0" to point to the right session on the NOR flash. Furthermore, the `<dump to file>` option is enabled above to store the data into a csv file. The dump file will be stored in the "record" folder:


You can also try recording the IMU raw sensor data, or Euler angles using the following commands:
```
sessionRecordEulerAngles <number of samples>
sessionRecordIMU <number of samples>
```

At any time, you can inquire about the number of sessions present in the recorder, as well as the length of each session:
```
getSessionCount //returns the total number of recorded sessions in the NOR flash recorder
getSessionInfo <Session ID>  //returns the length of a recorder session
```

#### Example 6: Read and Write to the EEPROM
```
EEPROMWrite <page_number> <string>
EEPROMRead <page_number>
```
![Path](/docs/img/eeprom.png)

For more information on streammenu commands or to see all available commands, please refer to the [reference guide](http://documentation.motsai.com)
