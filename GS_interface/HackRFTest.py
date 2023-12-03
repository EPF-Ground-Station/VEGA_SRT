import SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CF32
from SoapySDR import *
import numpy

results = SoapySDR.Device.enumerate()
for result in results: print(result)