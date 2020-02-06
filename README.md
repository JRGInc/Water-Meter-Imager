# 2019 Water Meter Code Base

This code library executes several functions:

1. Train Inception v4 image classification model with TensorFlow on Ubuntu desktop computer with nVidia GPU
2. Test Inception v4 image classification with TensorFlow on Ubuntu desktop computer with nVidia GPU
3. Image capture, classification, and transmission on Raspberry PI with PiCamera v2
4. Control stepper motor controller via Raspberry PI with TB6600 to rotate water meter shaft
5. Image capture experimentation on Raspberry PI

Create and download code to the following directory:

```
/opt/Janus/WM/
```

After downloading the code, create the following additional directory structure prior to running any function:

```
/images
/transmit
```

## Limited Operational Testing

Operational testing can be performed on a properly setup Raspberry Pi to verify functionality of the image capture and transmission toolchains.  

### Test Image Capture and Processing Only

To test the image and capture toolchains, open ```/opt/Janus/WM/config/capture.ini``` file and make the following changes:

```
## The numerical settings in this file represent minutes

[Capture_Settings]
execution_interval = 5
image_capture_freq = 1			# Set this to 1 to enable a single, immediate capture
image_xmit_freq    = 0          # Set this to 0 to disable copies placed in transmission queue
```

The ```image_capture_freq``` setting, when set to ```1``` enables a single capture process which will run immediately during program execution.  At the end of execution it will be reset to ```0```.

### Test Prediction Toolchain

To test the prediction toolchain set the ```prediction_enable``` setting to ```True``` in the ```/opt/Janus/WM/config/capture.ini```.  The results of this prediction will be placed in three locations: 

1.  A captured image in ```/opt/Janus/WM/images/YYYY-MM-DD_HHMM_nnnnnnn.jpg```.
2.  A coped image in ```/opt/Janus/WM/transmit/YYYY-MM-DD_HHMM_nnnnnnn.jpg```

### Test Execution

Open terminal and execute BASH code: 

```
pi@raspberrypi:~$ sudo python3 /opt/Janus/WM/python3/main-capture.py
```

### Test Transmission Toolchain

Transmission takes place when items are placed in the transmission queue ```/opt/Janus/WM/data/transmit```.  Each item is removed after successful transmission.  The test involves two parts:

1.  Successfully place selected items in the transmission queue
2.  Successfully transmit and delete items in the transmission queue


First, open ```/opt/Janus/WM/config/capture.ini``` file and make the following changes:

```
## The numerical settings in this file represent minutes

[Capture_Settings]
execution_interval = 5
image_capture_freq = 1			# Set this to 1 to enable a single, immediate capture
image_xmit_freq    = 1          # Set this to 1 to enable copies placed in transmission queue
```

The various settings, when set to ```1``` enables a process to run immediately during program execution.  At the end of execution each will be reset to ```0```.  

Next, open terminal and execute BASH code: 

```
pi@raspberrypi:~$ sudo python3 /opt/Janus/WM/python3/main-capture.py
```

After this runs, the transmit queue should be examined to determine the presence of all the image files and two text files, as marked in the settings file above, totaling several MB in disk space.  The actual transmission test does not require the presence of all these files; therefore, the operator can delete the larger files to conserve transmission data use.

Once unwanted files have been deleted, open ```/opt/Janus/WM/python3/config/transmit.py``` file and verify the settings in the ```self.gprs_cfg_dict``` python dictionary are correct:

```
self.gprs_cfg_dict = {
    'sock': 'fast.t-mobile.com',
    'addr': '198.13.81.243',
    'port': 4440,
    'attempts': self.config.getint(
	'Cellular_Configuration',
	'transmission_attempts'
    )
}
```

The number of transmission attempts (in the event of transmission error) is set in ```/opt/Janus/WM/config/transmit.ini``` with the ```transmission_attempts``` setting.


After verification, open terminal and execute BASH code: 

```
pi@raspberrypi:~$ sudo python3 /opt/Janus/WM/python3/main-transmit.py
```

Transmission progress will be piped to stdout and each file will be removed from the transmit queue after successful transmission.



## Operational Execution

For testing the various settings in the ```/opt/Janus/WM/config/capture.ini``` were set to ```1``` with the expectation that each setting thus set will be reverted to a ```0``` after execution.  For operational execution the ```execution_interval``` must be set to ```5``` or greater--**highly recommended to use multiples of 5**.  All other settings must be a multiple of the ```execution_interval```, as suggested below.  Only settings of ```1``` are reset to ```0```, so these settings will be preserved during execution.

```
[Capture_Settings]
execution_interval = 5			# Runs the script every 5 minutes as CRON job
image_capture_freq = 15			# Captures image every 15 minutes
image_xmit_freq    = 30         # Images captured on 30 minute intervals are placed in transmission queue
```

There are only a couple of settings for transmission in the ```/opt/Janus/WM/config/capture.ini```:

```
[Transmit_Settings]
# All frequencies specified in this file must be a
# multiple of this number
# Choices are must be 60, 120, 180, 240, 360, 480, 720, 1440
execution_interval = 60

[Update_Settings]
# Image capture frequency in minutes, 
# 60-1440 = minute intervals to update in 60 min increments
update_freq = 1440

# Cellular modem settings
[Cellular_Configuration]
transmission_attempts = 3
```

The ```execution_interval``` is set at 60-minute intervals.  During operataional execution, the CRON job will execute this program 5 minutes after the hour to prevent using processor resources when the image capture and prediction program executes on the hour.  

The ```update_freq``` is not used in this version of the program.  In the event of transmission failure, the ```transmission_attempts``` can be set to any number 1 or above.  

When the above settings are made, open terminal and execute BASH code to begin operation: 

```
pi@raspberrypi:~$ sudo python3 /opt/Janus/WM/python3/januswm.py
```

This sets two tasks in a CRON table: ```main-capture.py``` and ```main-transmit.py```.  They can be viewed at any time by opening a terminal and executing BASH code:

```
pi@raspberrypi:~$ crontab -l
```

To stop execution, open terminal and execute BASH code:

```
pi@raspberrypi:~$ crontab -r
```
