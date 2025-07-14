# Mag_Response

Mag_Response is a Python-based GUI program for magnetic device characterization. It applies a constant voltage or current bias to a device under test (DUT) while generating magnetic fields using a coil and a power amplifier controlled by a DAQ. It records real-time voltage responses from two GPIB-connected multimeters and visualizes them as XY plots.

## 1. Overview

- Apply voltage or current to a DUT while varying magnetic fields
- Real-time voltage monitoring using two multimeters
- Coil control through DAQ analog output (AO)
- GUI implemented using `tkinter`
- Data logging in CSV format

## 2. System Requirements

- Operating System: Windows 10 or higher  
- Python Version: 3.9 to most recent stable version recommended 
- Drivers: NI-VISA, NI-DAQmx  
- Hardware: GPIB-compatible sourcemeter and multimeters, NI DAQ device 

## 3. Installation

### 3.1 Install Python
Download from https://www.python.org and check “Add Python to PATH” during installation.

### 3.2 Install Required Packages
```bash
pip install pyvisa pyvisa-py nidaqmx numpy matplotlib
```

### 3.3 Install NI Drivers
- NI-VISA: for GPIB communication  
- NI-DAQmx: for analog output  
- Verify hardware detection in NI MAX

## 4. Device Connections

- Sourcemeter: GPIB0::01::INSTR  
- Multimeter 1: GPIB0::02::INSTR  (x-axis)
- Multimeter 2: GPIB0::03::INSTR  (y-axis)
- DAQ AO: Dev1/ao0 (Check in NI MAX)

> You can edit the addresses directly in the code or via the GUI.

## 5. How to Run

### From Command Line
```bash
python Mag_Response.py
```

## 6. User Guide

1. Select bias mode: voltage [V] or current [A]  
2. Enter GPIB addresses and sweep parameters  
3. Click 'Start Measurement' to begin sweeping and data logging  
4. Real-time XY plot appears; CSV file is created  
5. Click 'Stop Measurement' to safely end the session

> If used in conjunction with a Gaussmeter, the voltage output can be converted to magnetic field strength as per the Gaussmeter manual.

## 7. Data Output

- Format: CSV  
- Location: Current directory  
- Filename Example: `voltage_xy_log_YYYYMMDD_HHMMSS.csv`  
- Columns: Time(s), DMM1_X(V), DMM2_Y(V)

## 8. Technical Summary

- Language: Python  
- Libraries: pyvisa, nidaqmx, numpy, matplotlib, tkinter  
- Core Functions: magnetic sweep, DAQ control, real-time plotting, data export  
- Target Use: Magnetic field response characterization of devices
