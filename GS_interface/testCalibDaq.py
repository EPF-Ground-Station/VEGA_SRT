# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 19:29:56 2023

@author: lgtle
"""

from SRT_inline import *
from scipy.signal import welch

SRT.connect(False)

# 100.7075 , 65.32

# calibration
repo = "Tests/"
obs = "TestCalib/"

if not os.path.isdir(DATA_PATH+repo):
    os.mkdir(DATA_PATH+repo)

if not os.path.isdir(DATA_PATH+repo+obs):
    os.mkdir(DATA_PATH+repo+obs)

pathObs = DATA_PATH + repo + obs

pathCalib = DATA_PATH + repo+obs + "calibData"

if not os.path.isdir(pathCalib):
    os.mkdir(pathCalib)
pathCalib += '/'

fc = 1420e6  # MHz to Hz

rate = 2.048e6
intTime = 1
gain = 480
durCalib = 60  # 1min of calib


def obsPSD(fc, rate, intTime, gain, dur, path):

    # Save parameters of observation for later analysis
    with open(path+"params.json", "w") as jsFile:
        d = {"fc": fc,
             "rate": rate, "channels": 1024, "gain": gain, "intTime": intTime}
        json.dump(d, jsFile)

    nbSamples = rate * intTime
    m = np.floor(nbSamples/1024)    # Prefer a multiple of 1024 (channels)
    nbObs = int(np.ceil(duration/intTime))

    for i in range(nbObs):
        # Collect data
        self.sdr.open()
        self.sdr.center_freq = fc
        self.sdr.sample_rate = rate
        self.gain = gain

        samples = self.sdr.read_samples(1024 * m)

        # Save data
        real = fits.Column(name='real', array=samples.real, format='1E')
        im = fits.Column(name='im', array=samples.imag, format='1E')
        table = fits.BinTableHDU.from_columns([real, im])
        table.writeto(path + "sample#" +
                      str(i) + '.fits', overwrite=True)
        self.sdr.close()


SRT.trackGal(100.7075, 65.32)  # Moves to calibration target
obsPSD(fc, rate, intTime, gain, durCalib, pathCalib)
SRT.trackGal(84.29, 2)  # Moves to Deneb
obsPSD(fc, rate, intTime, gain, 180, pathObs)
SRT.disconnect()


def getFreqP(path):
    with open(path+"params.json", "r") as jsFile:
        params = json.load(jsFile)

    # Extract data
    fc = params["fc"]
    rate = params["rate"]
    channels = params["channels"]

    # I did not find any other way...
    for root, repo, files in os.walk(os.getcwd()):
        fitsFiles = [file for file in files if ".fits" in file]

    obsNb = len(fitsFiles)  # Number of files in observation

    firstFile = fitsFiles.pop(0)  # Pops the first element of the list
    real = fits.open(firstFile)[1].data.field('real').flatten()
    image = fits.open(firstFile)[1].data.field('im').flatten()

    for file in fitsFiles:
        data = fits.open(file)[1].data
        real += data.field('real').flatten()
        image += data.field('im').flatten()

    average = np.array((real + 1.0j*image)/obsNb)
    intTime = 1
    nperseg = int(intTime*rate)

    # average = np.delete(average, round(np.floor(len(average)/2))
    #                     )
    # average = np.delete(average, round(np.ceil(len(average)/2)))

    spectrum = np.fft.fft(average)
    freq, psd = welch(average, rate, detrend=False)
    return freq, psd


fCal, psdCal = getFreqP(pathCalib)
fObs, psdObs = getFreqObs(pathObs)

psdNew = psdObs - psdCal

plt.semilogy(freq+fc, psd)
plt.xlabel('frequency [Hz]')
plt.ylabel('Relative Power')
plt.savefig(pathObs+"PSDCalibrated.png", format="png")
plt.show()
