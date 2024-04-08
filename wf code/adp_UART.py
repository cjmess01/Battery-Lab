

"""
    UART Communication Script with Mohammad's Controller
    Author: Caleb Messerly and Shane Vanderhagen

    Make sure this is in the wf code folder on the ADP3450

"""

from ctypes import *
import sys

# Loads the correct linker library for the platform
if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

# Check for library loading errors
szerr = create_string_buffer(512)
dwf.FDwfGetLastErrorMsg(szerr)
if szerr[0] != b'\0':
    print(str(szerr.value))



print("Opening first device")
hdwf = c_int()
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
# device configuration of index 3 (4th) for Analog Discovery has 16kS digital-in/out buffer
#dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(3), byref(hdwf)) 

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()




# configure the I2C/TWI, default settings
dwf.FDwfDigitalUartRateSet(hdwf, c_double(9600)) # 9.6kHz
dwf.FDwfDigitalUartTxSet(hdwf, c_int(15)) # TX = DIO-15
dwf.FDwfDigitalUartRxSet(hdwf, c_int(14)) # RX = DIO-14
dwf.FDwfDigitalUartBitsSet(hdwf, c_int(8)) # 8 bits
dwf.FDwfDigitalUartParitySet(hdwf, c_int(0)) # 0 no parity, 1 even, 2 odd, 3 mark (high), 4 space (low)
dwf.FDwfDigitalUartStopSet(hdwf, c_double(1)) # 1 bit stop length
















# Prints error messages, if they exist
value = dwf.FDwfGetLastErrorMsg(szerr)
if szerr[0] != b'\0':
    print("printing last error: ")
    print(str(szerr.value))


