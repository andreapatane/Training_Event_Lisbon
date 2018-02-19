from matplotlib import pyplot as plt
import numpy as np
from scipy import signal

def lowpass(s, f, order=2, fs=100.0):
    b, a = signal.butter(order, f / (fs/2))
    return signal.filtfilt(b, a, s)


emg_thereshold = 20. 
acc_thereshold = 5.   
fc_emg = 1.
fc_acc = 5.               
window_size = 100     
fs = 100.
           
dataDir = 'data/'
dataFile = 'figure_c_data'
data = np.loadtxt(dataDir + dataFile +  '.txt')

emg_data = data[:,-2]
emg_data = emg_data - np.mean(emg_data)
acc_data = data[:,-1]
acc_data = acc_data - np.mean(acc_data)


newLen = emg_data.shape[0] - emg_data.shape[0] % window_size
emg_data = emg_data[:newLen]
acc_data = acc_data[:newLen]
     


emg_data = np.reshape(emg_data,(emg_data.shape[0]/window_size,window_size))
acc_data = np.reshape(acc_data,(acc_data.shape[0]/window_size,window_size))

buzzerFlag = []
accFlag = []

for i,win in enumerate(emg_data):
    filtWin = (lowpass(abs(win), fc_emg))
    
    if np.mean(filtWin) > emg_thereshold:
        buzzerFlag = buzzerFlag + [1]*window_size
    else:
        buzzerFlag = buzzerFlag + [0]*window_size
                                  
    acc_filt = abs(np.diff((lowpass(acc_data[i], fc_acc))))
    print np.mean(acc_filt)
    if np.mean(acc_filt) < 5:
        accFlag = accFlag + [1]*window_size
    else:
        accFlag = accFlag + [0]*window_size

emg_data =  np.reshape(emg_data,(emg_data.shape[0]*window_size))
acc_data =  np.reshape(acc_data,(acc_data.shape[0]*window_size))

plt.figure(1)
plt.clf()
timeVec = np.cumsum( (1./fs) * np.ones(len(emg_data)))
plt.plot(timeVec,emg_data/max(emg_data),'-')
plt.plot(timeVec, acc_data/max(acc_data),'-')
plt.plot(timeVec,np.array(buzzerFlag)*np.array(accFlag))
plt.ylim((-1,1))
plt.xlim((timeVec[0],timeVec[-1]))
plt.xlabel('Time [s]')
plt.legend(['EMG','Acc','Buzzer'])


