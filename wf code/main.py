"""
    Main Driver for ADP Signal Acquisition and Data Transformation
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

# Check library loading errors
szerr = create_string_buffer(512)
dwf.FDwfGetLastErrorMsg(szerr)
if szerr[0] != b'\0':
    print(str(szerr.value))

# Allocates space for a string and gets the version type
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

# # Enumerate connected devices
# cDevice = c_int()
# success = dwf.FDwfEnum(c_int(), byref(cDevice))
# print("Number of Devices: "+str(cDevice.value))





# Prints error messages, if they exist
value = dwf.FDwfGetLastErrorMsg(szerr)
print(value)
print("printing last error: ")
if szerr[0] != b'\0':
    print(str(szerr.value))
