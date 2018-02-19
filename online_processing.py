import bitalino
import time
import numpy as np
from scipy import signal

#Function of lowpass filtering
def lowpass(s, f, order=2, fs=100.0):
    b, a = signal.butter(order, f / (fs/2))
    return signal.filtfilt(b, a, s)

#bitalino dev parameter
macAddress = "/dev/tty.BITalino-DevB"
#starting connection
device = bitalino.BITalino(macAddress)
time.sleep(1)
#sampling frequency and number of samples per processing windows
srate = 100
nframes = 100
#asking for emg and accelerometer signal
device.start(srate, [0,4])
#decision theresholds for emg and accelerometer signals
emg_thereshold = 20.      
acc_thereshold = 5.                  
#cutoff frequencies for emg and acc filtering      
fc_emg = 1.
fc_acc = 5. 
#number of repetitions to do
maxReps = 10
#loop variables
repCount = 0
prevWinFlag = False


#main processing loop
print "START"
try:
    while repCount < maxReps:

        #retrieving data, and stop loop if button is pressed
        data = device.read(nframes)
        if numpy.mean(data[:, 1]) < 1: break
        
        #getting emg and acc columns from data matrix
        emg_data = data[:,-2]
        acc_data = data[:,-1]
        #normalising signal to zero mean
        emg_data = emg_data - np.mean(emg_data)
        acc_data = acc_data - np.mean(acc_data)
        
        
        #Filtering absolute value of emg signal
        emg_data = lowpass(abs(emg_data), fc_emg, fs = srate)
        
        #Filtering and taking numerical derivative of accelerometer signal
        acc_data = abs(np.diff((lowpass(acc_data, fc_acc,fs = srate))))
        
        #if musclar activity detected and acceleration is in correct bounds...
        if (np.mean(emg_data) > emg_thereshold) and  (np.mean(acc_data) < 5):
            #...then the buzzer is turned on...
            device.trigger([0, 1])
            #...and set previous window flag to True, for the next step
            prevWinFlag = True
        else:
            #...otherwise buzzer is turned off...
            device.trigger([0, 0])
            #...and if the buzzer was on in the previous step, another repetion of the exercise is completed
            if prevWinFlag:
                repCount = repCount + 1
            #previous windows flag is then set to False
            prevWinFlag = False
finally:
    #turning on light to give feedback on end of exercise
    device.trigger([1, 0])
    time.sleep(3)
    #turning off light and closing device connection
    device.trigger([0, 0])
    print "STOP"
    device.stop()
    device.close()
