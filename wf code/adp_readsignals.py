from ctypes import *
import sys


from dwfconstants import *
import math, time


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

dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called




#& Sending out sine wave stuff
dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called


print("Generating sine wave...")
# Disables preset configuration, allowing us to configure manually
dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) 

print("Configure and start first analog out channel")
# Sets it to channel 1 with default carrier node as source. 
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), AnalogOutNodeCarrier, c_int(1))
# Sets channel 0 to create a sine wave
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), AnalogOutNodeCarrier, funcSine)
# Sets frequency of the given function wave
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), AnalogOutNodeCarrier, c_double(1e6))
# Sets amplitude
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), AnalogOutNodeCarrier, c_double(0.9))
# Starts the instrument
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(1))

# Weirdly, if you have the following code, it works. But without 
# Something to do after the configure command, it fails out!
sts = c_ubyte(0)
print("Entering try catch 1")
try:
    while True:
        time.sleep(1)
        dwf.FDwfAnalogOutStatus(hdwf, c_int(0), byref(sts))
        print(sts)
        continue

except KeyboardInterrupt:
    pass

    

# capture up to 32Ki if samples
nBufMax = c_int()
dwf.FDwfAnalogInBufferSizeInfo(hdwf, 0, byref(nBufMax))
nSamples = min(32768, nBufMax.value)
nSamples = int(2**round(math.log2(nSamples)))

#set up acquisition
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(100e6))
dwf.FDwfAnalogInBufferSizeSet(hdwf, nSamples)
dwf.FDwfAnalogInChannelEnableSet(hdwf, 0, 1) # enable channel 0 (C1)
dwf.FDwfAnalogInChannelRangeSet(hdwf, 0, c_double(2)) # 2V pk2pk

if dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1)) != 1 :
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(szerr.value)
    quit()

hzRate = c_double()
dwf.FDwfAnalogInFrequencyGet(hdwf, byref(hzRate))
print("Samples: "+str(nSamples)+"  Rate: "+str(hzRate.value/1e6)+"MHz") 


rgdSamples = (c_double*nSamples)()
rgdWindow = (c_double*nSamples)()
nBins = int(nSamples/2+1)
rgdBins = (c_double*nBins)()
hzTop = hzRate.value/2
dwf.FDwfSpectrumWindow(byref(rgdWindow), c_int(nSamples), DwfWindowFlatTop, c_double(1.0), None)
print("Range: DC to "+str(hzTop/1e6)+" MHz  Resolution: "+str(hzTop/(nBins-1)/1e3)+" kHz") 

print("Press Ctrl+C to stop")
try:
    while True:
        time.sleep(0.5)
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
        for ich in range(2):
            dwf.FDwfAnalogInStatusData(hdwf, c_int(ich), rgdSamples, nSamples) # get channel 1 data
            for i in range(nSamples):
                rgdSamples[i] = rgdSamples[i]*rgdWindow[i]
            dwf.FDwfSpectrumFFT(byref(rgdSamples), nSamples, byref(rgdBins), None, nBins)

            iPeak = 0
            vPeak = float('-inf')
            for i in range(5, nBins): # skip DC lobe
                if rgdBins[i] < vPeak: continue
                vPeak = rgdBins[i]
                iPeak = i

            print("C"+str(ich+1)+" peak: "+str(hzTop*iPeak/(nBins-1)/1e6)+" MHz  "+str(vPeak)+" V")
            
            if iPeak < nBins-5: # weighted average
                s = 0
                m = 0
                for i in range(-4,5):
                    t = rgdBins[iPeak+i]
                    s += (iPeak+i)*t
                    m += t
                iPeak = s/m

            print("C"+str(ich+1)+" weighted: "+str(hzTop*iPeak/(nBins-1)/1e6)+" MHz")

except KeyboardInterrupt:
    pass

dwf.FDwfDeviceCloseAll()







