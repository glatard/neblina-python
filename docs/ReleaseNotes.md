# Neblina Firmware Release Notes
Last updated: June 2, 2016

New

- Simultaneous BLE (Bluetooth Low Energy) and UART communication
- Multiple interaction command for various subsystem
  - Debug: Set Interface, Motion Status, Recorder Status, Firmware Version, Port Status and Set Port State
  - EEPROM: Read and Write page
  - LED: Get and Set state
  - Motion
    - Settings: Disable All Streaming, Downsample, External Heading Correction, Lock Heading Reference, Accelerometer Range, Fusion Type
    - Streaming: Euler Angle, External Force, Finger Gesture, IMU, MAG, Motion State, Pedometer, Quaternion, Rotation Information, Sitting/Standing, Trajectory Information
    - Utilities: Reset Timestamp, Start/Stop Trajectory Recording
  - Flash: Erase, Start/Stop Record, Start/Stop Playback, Get Number of Sessions, Get Session Information
  - Power: Battery Level, Board Temperature
- Support multiple motion streaming
- Support BLE streaming at a maximum of 50 packets/second
- Support UART communication at 500 000 baud rate
- Record up to 900 000 packets on flash (only with ProMotion)
- Application-specific EEPROM space of 2 KB (only with ProMotion)
- Support battery power (only with ProMotion)

Known Issues

- Hardware
  - UART communication freeze when powering up. Requires power cycling.
  - Occasional power failure when powering up. Requires power cycling and battery reconnection (if present).
