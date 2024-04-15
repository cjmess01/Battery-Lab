"""
    Main Driver for ADP Signal Acquisition and Data Transformation
    Author: Caleb Messerly and Shane Vanderhagen

    Make sure this is in the wf code folder on the ADP3450

"""

from ctypes import *
import sys
import time


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



# UART stuff
print("Configuring UART...")

cRX = c_int(0)
fParity = c_int(0)

# configure the I2C/TWI, default settings
dwf.FDwfDigitalUartRateSet(hdwf, c_double(9600)) # 9.6kHz
dwf.FDwfDigitalUartTxSet(hdwf, c_int(15)) # TX = DIO-15
dwf.FDwfDigitalUartRxSet(hdwf, c_int(14)) # RX = DIO-14
dwf.FDwfDigitalUartBitsSet(hdwf, c_int(8)) # 8 bits
dwf.FDwfDigitalUartParitySet(hdwf, c_int(0)) # 0 no parity, 1 even, 2 odd, 3 mark (high), 4 space (low)
dwf.FDwfDigitalUartStopSet(hdwf, c_double(1)) # 1 bit stop length

dwf.FDwfDigitalUartTx(hdwf, None, c_int(0))# initialize TX, drive with idle level
dwf.FDwfDigitalUartRx(hdwf, None, c_int(0), byref(cRX), byref(fParity))# initialize RX reception
time.sleep(1)

rgTX = create_string_buffer(b'Hello\r\n')
rgRX = create_string_buffer(8193)

print("Sending on TX for 10 seconds...")
dwf.FDwfDigitalUartTx(hdwf, rgTX, c_int(sizeof(rgTX)-1)) # send text, trim zero ending

tsec = time.perf_counter()  + 10 # receive for 10 seconds
print("Receiving on RX...")
while time.perf_counter() < tsec:
    time.sleep(0.01)
    dwf.FDwfDigitalUartRx(hdwf, rgRX, c_int(sizeof(rgRX)-1), byref(cRX), byref(fParity)) # read up to 8k chars at once
    if cRX.value > 0:
        rgRX[cRX.value] = 0 # add zero ending
        print(rgRX.value.decode(), end = '', flush=True)
        print("B")
    if fParity.value != 0:
        print("Parity error {}".format(fParity.value))

dwf.FDwfDeviceCloseAll()



