import SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CF32
from SoapySDR import *
import numpy

print("loading results")
results = SoapySDR.Device.enumerate()
for result in results: print(result)