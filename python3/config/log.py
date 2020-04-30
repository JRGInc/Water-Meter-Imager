__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import os

# Log paths and files
LOGPATHWM = os.path.normpath('/var/log/JanusWM/')
LOGPATHWMCAPT = os.path.normpath('/var/log/JanusWM-capture/')
LOGPATHWMXMIT = os.path.normpath('/var/log/JanusWM-transmit/')
januswm = os.path.join(LOGPATHWM, 'januswm')                      # Log file
januswm_capture = os.path.join(LOGPATHWMCAPT, 'januswm-capture')      # Log file
januswm_transmit = os.path.join(LOGPATHWMXMIT, 'januswm-transmit')    # Log file


class LogCfg(object):
    def __init__(
        self
    ) -> None:
        """
        Instantiates logging object and sets log configuration
        """
        self.config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'simple': {
                    'format': '%(levelname)s %(message)s',
                },
                'verbose': {
                    'format': " * %(asctime)s * %(levelname)s: " +
                              "<function '%(funcName)s' from '%(filename)s'>: %(message)s",
                },
            },
            'loggers': {
                'januswm': {
                    'handlers': ['januswm'],
                    'propagate': False,
                    'level': 'INFO',
                },
                'januswm-capture': {
                    'handlers': ['januswm-capture'],
                    'propagate': False,
                    'level': 'INFO',
                },
                'januswm-transmit': {
                    'handlers': ['januswm-transmit'],
                    'propagate': False,
                    'level': 'INFO',
                }
            },
            'handlers': {
                'januswm': {
                    'level': 'DEBUG',
                    'formatter': 'verbose',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': januswm,
                    'maxBytes': 25000,
                    'backupCount': 100,
                },
                'januswm-capture': {
                    'level': 'DEBUG',
                    'formatter': 'verbose',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': januswm_capture,
                    'maxBytes': 25000,
                    'backupCount': 100,
                },
                'januswm-transmit': {
                    'level': 'DEBUG',
                    'formatter': 'verbose',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': januswm_transmit,
                    'maxBytes': 25000,
                    'backupCount': 100,
                }
            }
        }
