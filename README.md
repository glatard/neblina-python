[![Build Status](https://travis-ci.org/Motsai/neblina-python.svg)](https://travis-ci.org/Motsai/neblina-python)
# Neblina<sup>TM</sup> ProMotion Development Kit Python Scripts
![Python](https://www.python.org/static/community_logos/python-logo-master-v3-TM.png)
![ProMotion Board](http://i.imgur.com/FvKbWka.jpg)

This repository provides a Python interface that interacts with and simulates the behaviour of Neblina, a Motion Capture module developed by Motsai. Here, we present a quick guide to use Python to communicate with the ProMotion board (http://promotion.motsai.com/), which adds storage, USB and battery connectivity, as well as I/O expansion to Neblina.  
# Requirements
* python3
* pyserial
* bluepy
* Windows or Linux
* ProMotion board
* 3ft Micro USB cable

# ProMotion board hardware setup
Download the [Quick Start guide](https://drive.google.com/file/d/0B92ySxNucL7jYi1ESHFjcDI5NFU/view?usp=sharing).

# Python Installation

## Install the source locally:
```
$ git clone https://github.com/Motsai/neblina-python.git
```

## Install dependencies:
```
$ pip3 install pyserial
$ pip3 install bluepy
```

To be able to run interaction scripts, you must first instantiate the pyslip submodule:
```
$ git submodule init
$ git submodule update
```

## Windows
### Include directories to the Python Environment
![Path](http://i.imgur.com/ftOUSVX.png?1)

## Linux
### Include directories to the Python Environment
In order to include the directories required to run `neblina-python`, add the following lines at the end of `~/.bashrc` by replacing `/path/to/the/repo/` with the path where `neblina-python` folder is located:
```
export PYTHONPATH="${PYTHONPATH}:/path/to/the/repo/neblina-python"
```

It is recommended to run `source ~/.bashrc` to execute the file you just modify to apply the changes. Otherwise, you need to open a new shell.

# How-to
## Retrieve COM port name
In order to connect neblina to the computer, the COM port name is required. Follow these steps to retrieve the COM port name associated with neblina, depending on your platform.
* Disconnect `ProMotion` from the computer, if already connected, and then turn it off.
* Follow these steps prior to connecting `ProMotion`
    * On Windows, open `Device Manager` and navigate to `Ports (COM & LTP)`.
    * On Linux, execute the following command.
    ```
    ls /dev/ttyACM*
    ```
* Now connect `ProMotion` and monitor the changes from the previous step. Note that `ProMotion` should be turned off, when you plug it in the computer.
    * On Windows, the COM port name follow the `COMx` pattern (where `x` is the associated COM port number)
    * On Linux, the COM port name follow the `/dev/ttyACMx` pattern (where `x` is the associated COM port number)
* On Linux, it is required to give permissions to use the COM port. Set with the following command by replace `x` with the associated COM port number:
```
chown user /dev/ttyACMx
```

## Running the unit tests (optional)
The unit tests allow for the validation of the decoding and encoding process of the packets transferred between the computer and the board. Make sure the pyslip submodule has been cloned and then you can now run the unit tests by executing the designated bash script:
```
./runNeblinaDataTests.sh
```

## Execute the interaction shell (Linux):
```
cd examples
python3 streammenu.py
```

On the execution of the shell script, the program will ask you for the name of the COM port to connect to. Type the name of the COM port associated with the module and press 'Enter'.


## Stream menu commands:
To explore different streaming features of the ProMotion board, run the stream menu shell script, and type "help" to see the available commands:
```
help
```
![Path](http://i.imgur.com/x9mP3ws.png)

Through the rest of this guide, we will go through a number of examples to explore the streaming features of the ProMotion board.


### Example 1: stream quaternion orientation data
```
streamQuaternion
```
The quaternion data will then be streamed to the console. The information includes a timestamp in microseconds, which is followed by the four elements of a unit-length quaternion vector. 
![Path](http://i.imgur.com/E8wbtgX.png)

The quaternion entries are represented as 16-bit signed integer values covering the range of [-1,1]. For more information regarding the quaternion data format please refer to the reference guide:
```
API_link.pdf //to be added later
```

You can stop the streaming at any time by hitting ctrl+C.

### Example 2: stream Euler angles
```
streamEulerAngle
```
This will stream the Yaw, Pitch and Roll angles in degrees using the aerospace rotation sequence, where Yaw takes place first, and is then followed by Pitch and Roll. The timestamp value in microseconds is also provided. The streaming can be stopped by hitting ctrl+C.

### Example 3: stream raw sensor data
To stream the 3-axis accelerometer and gyroscope data:
```
streamIMU
```
To stream the 3-axis accelerometer and magnetometer data:
```
streamMAG
```
The streaming can be stopped by hitting ctrl+C. The sensor ranges are also discussed in the reference guide:
```
API_link.pdf //to be added later
```

### Example 4: get the battery level and temperature of the board
```
getBatteryLevel
getTemperature
```
![Path](http://i.imgur.com/SplE2nk.png)

### Example 5: record motion data on chip
To record, and playback a specific motion feature:
```
storageErase //erase the on-chip recorder (optional)
storageRecordQuaternion <number of samples> //by default, the streaming frequency is 50 Hz.
storagePlayback <session ID> <dump to file option> //use the same session ID as returned by the record command
```

![Path](http://i.imgur.com/OByaYRg.png)

Note from the above snapshot that the session ID "0" has been returned after the recording is issued. Consequently, the playback command should define the session ID "0" to point to the right session on the NOR flash. Furthermore, the `<dump to file>` option is enabled above to store the data into a csv file. The dump file will be stored in the "record" folder:

![Path](http://i.imgur.com/QwJ4hQD.png)

You can also try recording the IMU raw sensor data, or Euler angles using the following commands:
```
storageRecordEulerAngles <number of samples>
storageRecordIMU <number of samples>
```

At any time, you can inquire about the number of sessions present in the recorder, as well as the length of each session:
```
getSessionCount //returns the total number of recorded sessions in the NOR flash recorder
getSessionInfo <Session ID>  //returns the length of a recorder session
```

### Example 6: Read and Write to the EEPROM
```
EEPROMWrite <page_number> <string>
EEPROMRead <page_number>
```
![Path](http://i.imgur.com/CrijxdY.png)

There are more commands in the streammenu, for which you can find more information in the reference guide:
```
API_link.pdf //to be added later
```
