"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2022-08-01

   Requires:                       
       Python 2.7, 3
"""

"""# (0) dependencies ##################################################"""

from ctypes import *
from dwfconstants import *
import math
import time
import matplotlib.pyplot as plt
import sys
import numpy


"""# (1) device setup ##################################################"""

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")


version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

# prevent temperature drift
dwf.FDwfParamSet(DwfParamOnClose, c_int(0)) # 0 = run, 1 = stop, 2 = shutdown

hdwf = c_int()
print("Opening first device")
if dwf.FDwfDeviceOpen(-1, byref(hdwf)) != 1 or hdwf.value == hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(szerr.value)
    print("failed to open device")
    quit()



# 0 = the device will be configured only when calling FDwf?Configure
dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0))



""" (2) signal generation ##################################################"""

print("Generating sine wave...")
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), AnalogOutNodeCarrier, c_int(1))
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), AnalogOutNodeCarrier, funcRampDown)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), AnalogOutNodeCarrier, c_double(500000))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), AnalogOutNodeCarrier, c_double(0.705))
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(1))


# capture up to 32Ki if samples
nBufMax = c_int()
dwf.FDwfAnalogInBufferSizeInfo(hdwf, 0, byref(nBufMax))
nSamples = min(32768, nBufMax.value)
nSamples = int(2**round(math.log2(nSamples)))
print("Samples: "+str(nSamples)) 


"""# (3) signal aquisition ##################################################"""



#set up acquisition
channel1 = 0 # enable channel 0 (C1)
channel2 = 1 # enable channel 1 (C2)

#set constants for the aquisition
"""might need to make this a ctype?"""

#sample rate in Hz [nyquist rate (minimum to not have aliasing) is 2*freq of signal]
samplerate = 20000000
#peak to peak channel voltage range
pkpkchannelrange = 2
#coupling: 1 = AC; 0 = DC
coupling = 0
#attenuation constant
attenuation = 1
#record length in seconds
recordlength = 1
#oversampling: A signal is said to be oversampled by a factor of N if it is sampled at N times the Nyquist rate.
oversampling = "not necessary"
#set analog in channel bandwidth in Hz. In order to get maximum bandwidth, comment out the corresponding API command.
bandwidthHz = 20000000



#use constants to actually change the settings


dwf.FDwfAnalogInFrequencySet(hdwf, c_double(samplerate))
dwf.FDwfAnalogInBufferSizeSet(hdwf, nSamples)
dwf.FDwfAnalogInChannelEnableSet(hdwf, channel1, 1)
dwf.FDwfAnalogInChannelEnableSet(hdwf, channel2, 1)
dwf.FDwfAnalogInChannelRangeSet(hdwf, channel1, c_double(pkpkchannelrange)) # pk2pk
dwf.FDwfAnalogInChannelRangeSet(hdwf, channel2, c_double(pkpkchannelrange)) # pk2pk

#dwf.FDwfAnalogInChannelCouplingSet(hdwf, channel1, ctypes.c_double(0))
dwf.FDwfAnalogInChannelCouplingSet(hdwf, channel1, coupling)
dwf.FDwfAnalogInChannelCouplingSet(hdwf, channel2, coupling)
#dwf.FDwfAnalogInChannelAttenuationSet(hdwf, channel2, ctypes.c_double(attenuation))
dwf.FDwfAnalogInChannelAttenuationSet(hdwf, channel1, attenuation)
dwf.FDwfAnalogInChannelAttenuationSet(hdwf, channel2, attenuation)
# FDwfAnalogInRecordLengthSet(HDWF hdwf, double sLegth)
dwf.FDwfAnalogInRecordLengthSet(hdwf, recordlength)
# FDwfAnalogInChannelBandwidthSet(HDWF hdwf, int idxChannel, double hz)
dwf.FDwfAnalogInChannelBandwidthSet(hdwf, channel1, bandwidthHz)
dwf.FDwfAnalogInChannelBandwidthSet(hdwf, channel2, bandwidthHz)


# ORIGINAL COMMENT: wait at least 2 seconds for the offset to stabilize after the first connection
# start the acquisition
# FDwfAnalogInConfigure(HDWF hdwf, int fReconfigure, int fStart)
dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(0))
dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(0))
time.sleep(0.1)


"""Issue: how to start both channels as the exact same time"""
"""Fix: analog in configure and setting the scope to start the aquisition reads form any enabled channels."""
print("Starting oscilloscope")
if dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1)) != 1 :
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(szerr.value)
    quit()


hzRate = c_double()
dwf.FDwfAnalogInFrequencyGet(hdwf, byref(hzRate))

while True:
    sts = c_byte()
    # fetch status and data from device
    if dwf.FDwfAnalogInStatus(hdwf, 1, byref(sts)) != 1 :
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(szerr.value)
        quit()
    if sts.value == DwfStateDone.value :
        break
print("Acquisition done")


"""Need to rename this variable to something that makes more sense"""
rgdSamples1 = (c_double*nSamples)()

#FDwfAnalogInStatusData( HDWF hdwf, int idxChannel, double *rgdVoltData, int cdData)
#Description: Retrieves the acquired data samples from the specified idxChannel on the AnalogIn instrument. It
#copies the data samples to the provided buffer.
dwf.FDwfAnalogInStatusData(hdwf, channel1, rgdSamples1, nSamples) # get channel 1 data
dwf.FDwfAnalogInStatusData(hdwf, channel2, rgdSamples1, nSamples) # get channel 1 data

dwf.FDwfDeviceCloseAll()



"""# (4) FFT ##################################################"""


plt.title("raw data")
plt.plot(numpy.fromiter(rgdSamples1, dtype = numpy.float64), color='orange', label='C1')
plt.show()


hzTop = hzRate.value/2
rgdWindow = (c_double*nSamples)()
vBeta = c_double(1.0) # used only for Kaiser window
vNEBW = c_double() # noise equivalent bandwidth
dwf.FDwfSpectrumWindow(byref(rgdWindow), c_int(nSamples), DwfWindowFlatTop, vBeta, byref(vNEBW))

for i in range(nSamples):
    rgdSamples1[i] = rgdSamples1[i]*rgdWindow[i]



"""# (5) data processing and other ##################################################"""



plt.title("window and windowed data")
plt.plot(numpy.fromiter(rgdSamples1, dtype = numpy.float64), color='orange', label='C1')
plt.plot(numpy.fromiter(rgdWindow, dtype = numpy.float64), color='blue', label='W')
plt.show()


# requires power of two number of samples and BINs of samples/2+1
nBins = int(nSamples/2+1)
rgdBins1 = (c_double*nBins)()
rgdPhase1 = (c_double*nBins)()
dwf.FDwfSpectrumFFT(byref(rgdSamples1), nSamples, byref(rgdBins1), byref(rgdPhase1), nBins)

sqrt2 = math.sqrt(2)
for i in range(nBins): 
    rgdBins1[i] = 20.0*math.log10(rgdBins1[i]/sqrt2) # to dBV

for i in range(nBins): 
    if rgdBins1[i]<-60 : rgdPhase1[i] = 0  # mask phase at low magnitude
    else: rgdPhase1[i] = rgdPhase1[i]*180.0/math.pi # radian to degree
    if rgdPhase1[i] < 0 : rgdPhase1[i] = 180.0+rgdPhase1[i] 

rgMHz = []
for i in range(nBins): 
    rgMHz.append(hzTop*i/(nBins-1)/1e6)

rgBins1 = numpy.fromiter(rgdBins1, dtype = numpy.float64)
rgPhase1 = numpy.fromiter(rgdPhase1, dtype = numpy.float64)

plt.title("FFT dBV-deg / MHz")
plt.xlim([0, hzTop/1e6])
plt.ylim([-180.0, 180.0])
#plt.xticks(numpy.arange(0, hzTop/1e6, hzTop/2e7))
plt.plot(rgMHz, rgBins1, color='orange', label='dBV')
plt.plot(rgMHz, rgPhase1, color='blue', label='deg')
plt.show()


iPeak1 = 0
vMax = float('-inf')
for i in range(5, nBins): # skip DC
    if rgBins1[i] < vMax: continue
    vMax = rgBins1[i]
    iPeak1 = i

print("C1 peak: ", hzTop*iPeak1/(nBins-1)/1000,"kHz")


