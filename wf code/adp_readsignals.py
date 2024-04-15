from ctypes import *
import sys
from dwfconstants import *


# Loads the correct linker library for the platform
if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

# Allocates space for a string and gets the version type
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

# Opens  device
hdwf = c_int()
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()



#& Sending out sine wave stuff

# Disables preset configuration, allowing us to configure manually
dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) 

print("Configure and start first analog out channel")
# Sets it to channel 1 with default carrier node as source. 
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), AnalogOutNodeCarrier, c_int(1))
# Sets channel 0 to create a sine wave
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), AnalogOutNodeCarrier, funcSine)
# Sets frequency of the given function wave
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), AnalogOutNodeCarrier, c_double(500000))
# Sets amplitude
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), AnalogOutNodeCarrier, c_double(3.5))
# Starts the instrument
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(1))


