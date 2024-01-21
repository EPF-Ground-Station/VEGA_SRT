import SoapySDR
from SoapySDR import SOAPY_SDR_RX, SOAPY_SDR_CF32
from SoapySDR import *
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

sampleRate = 4e6
freq = 1420e6
NSamples = 16384


timeout_us = int(5e6)

print("loading results")
results = SoapySDR.Device.enumerate()
for result in results: print(result)

args = dict(driver="hackrf")
sdr = SoapySDR.Device(args)

print(sdr.listAntennas(SOAPY_SDR_RX, 0))
listofGains=sdr.listGains(SOAPY_SDR_RX, 0)
print(sdr.listGains(SOAPY_SDR_RX, 0))
for i in listofGains:
    print(i,sdr.getGainRange(SOAPY_SDR_RX,0,i))

freqs = sdr.getFrequencyRange(SOAPY_SDR_RX, 0)
for freqRange in freqs: print(freqRange)

sdr.setSampleRate(SOAPY_SDR_RX, 0, sampleRate)           # Set sample rate
sdr.setGain(SOAPY_SDR_RX, 0, 'LNA', 32)        # Set the gain mode
sdr.setGain(SOAPY_SDR_RX, 0, 'AMP', 14)
sdr.setGain(SOAPY_SDR_RX, 0, 'VGA', 20)
sdr.setFrequency(SOAPY_SDR_RX, 0, freq)          # Tune the LO

rx_buff = np.empty(2 * NSamples, np.int16)  # Create memory buffer for data stream
rx_stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CS16, [0]) # Setup data stream
sdr.activateStream(rx_stream)  # this turns the radio on

sr = sdr.readStream(rx_stream, [rx_buff], NSamples, timeoutUs=timeout_us)

rc = sr.ret
assert rc == NSamples, 'Error Reading Samples from Device (error code = %d)!' % rc

rx_buff.tofile("file1.bin")