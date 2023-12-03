import SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CF32
from SoapySDR import *
import numpy

sampleRate = 4e6
freq = 1420e6
print("loading results")
results = SoapySDR.Device.enumerate()
for result in results: print(result)

args = dict(driver="hackrf")
sdr = SoapySDR.Device(args)

print(sdr.listAntennas(SOAPY_SDR_RX, 0))
listofGains=sdr.listGains(SOAPY_SDR_RX, 0)
print(sdr.listGains(SOAPY_SDR_RX, 0))
for i in listofGains:
    print(sdr.getGainRange(SOAPY_SDR_RX,0,i))

freqs = sdr.getFrequencyRange(SOAPY_SDR_RX, 0)
for freqRange in freqs: print(freqRange)

sdr.setSampleRate(SOAPY_SDR_RX, 0, sampleRate)           # Set sample rate
#sdr.setGain(SOAPY_SDR_RX, 0, '', 14)        # Set the gain mode
sdr.setFrequency(SOAPY_SDR_RX, 0, freq)          # Tune the LO