[![Build Status](https://travis-ci.org/Motsai/neblina-python.svg)](https://travis-ci.org/Motsai/neblina-python)
# Neblina Python Scripts
![Python](https://www.python.org/static/community_logos/python-logo-master-v3-TM.png)
![ProMotion Board](http://i.imgur.com/FvKbWka.jpg)

neblina-python is a Python interface that interact with and simulate the behaviour of Neblina, a Motion Capture module developed by Motsai.
# Requirements
* python3
* pyserial
* bluepy
* Windows or Linux

# Installation

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
export PYTHONPATH="${PYTHONPATH}:/path/to/the/repo/neblina-python/pyslip"
```

# How-to
## Retrieve COM port name
In order to connect neblina to the computer, the COM port name is required. Follow these steps to retrieve the COM port name associated with neblina, depending on your platform.
* Disconnect `Neblina` from computer, if already connected.
* Follow these steps prior to connecting `Neblina`
** On Windows, open `Device Manager` and navigate to `Ports (COM & LTP)`.
** On Linux, execute the following command.
```
ls /dev/ttyACM*
```
* Now connect `Neblina` and monitor the changes from the previous step. On the [ProMotion](http://promotion.motsai.com/) board, there is a serial USB-COM already provided.
** On Windows, the COM port name follow the `COMx` pattern (where `x` is the associated COM port number)
** On Linux, the COM port name follow the `/dev/ttyACMx` pattern (where `x` is the associated COM port number)

## Execute the interaction shell (Linux):
```
cd examples
python3 streammenu.py
```

On the execution of the shell script, the program will ask you for the name of the COM port to connect to. Type the name of the COM port associated with the module and press 'Enter'.


## Running the unit tests
The unit tests allow for the validation of the decoding and encoding process of the packets.
Make sure the pyslip submodule has been cloned and then you can now run the unit tests by executing the designated bash script:
```
./runNeblinaDataTests.sh
```

