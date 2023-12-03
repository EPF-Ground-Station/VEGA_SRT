import SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CF32
from SoapySDR import *
import numpy

print("loading results")
results = SoapySDR.Device.enumerate()
for result in results: print(result)

args = dict(driver="hackrf")
sdr = SoapySDR.Device(args)

print(sdr.listAntennas(SOAPY_SDR_RX, 0))
print(sdr.listGains(SOAPY_SDR_RX, 0))
freqs = sdr.getFrequencyRange(SOAPY_SDR_RX, 0)
for freqRange in freqs: print(freqRange)