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
repo = "Tests"
obs = "TestCalib"
cal = "calibData"

if not os.path.isdir(DATA_PATH+repo):
    os.mkdir(DATA_PATH+repo)

if not os.path.isdir(DATA_PATH+repo+'/'+obs):
    os.mkdir(DATA_PATH+repo+'/'+obs)

pathObs = DATA_PATH + repo + '/' + obs

pathCalib = DATA_PATH + repo + "/calibData"

if not os.path.isdir(pathCalib):
    print(f"making Dir at {pathCalib}")
    os.mkdir(pathCalib)
pathCalib += '/'

fc = 1420

rate = 2.048
intTime = 1
gain = 480
durCalib = 60  # 1min of calib
durObs = 300


def obsPSD(fc, rate, intTime, gain, dur, path):

    # Save parameters of observation for later analysis
    with open(path+"params.json", "w") as jsFile:
        d = {"fc": fc,
             "rate": rate, "channels": 1024, "gain": gain, "intTime": intTime}
        json.dump(d, jsFile)

    nbSamples = rate * intTime
    m = np.floor(nbSamples/1024)    # Prefer a multiple of 1024 (channels)
    nbObs = int(np.ceil(dur/intTime))
    print(f"nbObs : {nbObs}")

    for i in range(nbObs):
        # Collect data
        print("open")
        SRT.sdr.open()
        print("freq")
        SRT.sdr.center_freq = fc
        print("rate")
        SRT.sdr.sample_rate = rate
        print("gain")
        SRT.gain = gain

        print("here it begins")
        samples = SRT.sdr.read_samples(1024 * m)
        print("here it stops")

        # Save data
        real = fits.Column(name='real', array=samples.real, format='1E')
        im = fits.Column(name='im', array=samples.imag, format='1E')
        table = fits.BinTableHDU.from_columns([real, im])
        table.writeto(path + "sample#" +
                      str(i) + '.fits', overwrite=True)
        SRT.sdr.close()


SRT.trackGal(100.7075, 65.32)  # Moves to calibration target
SRT.obsPower(durCalib, repo=repo, obs=cal)
SRT.trackGal(84.29, 2)  # Moves to Deneb
SRT.obsPower(durObs, repo=repo, obs=obs)
SRT.disconnect()


def getFreqP(path):
    with open(path+"params.json", "r") as jsFile:
        params = json.load(jsFile)

    # Extract data
    fc = params["fc"]
    rate = params["rate"]
    channels = params["channels"]

    # I did not find any other way...
    for root, repo, files in os.walk(path):
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

    # average = np.delete(average, round(np.floor(len(average)/2))
    #                     )
    # average = np.delete(average, round(np.ceil(len(average)/2)))

    freq, psd = welch(average, rate, detrend=False)
    return freq, psd


fCal, psdCal = getFreqP(pathCalib)
fObs, psdObs = getFreqP(pathObs)

psdCal = psdCal / np.mean(psdCal)
psdObs = psdObs / np.mean(psdObs)

psdNew = psdObs - psdCal + 1000

plt.semilogy(freq+fc, psd)
plt.xlabel('frequency [Hz]')
plt.ylabel('Relative Power')
plt.savefig(pathObs+"PSDCalibrated.png", format="png")
plt.show()
