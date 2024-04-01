"""
    Caleb's samplescript
    Author: Caleb Messerly

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


