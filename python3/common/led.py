__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import inspect
import logging
import rpi_ws281x
from common import errors

logfile = 'januswm-capture'
logger = logging.getLogger(logfile)


class LED(object):
    def __init__(
        self,
        err_xmit_url: str,
        led_cfg_dict: dict
    ) -> None:
        """
        Instantiates object

        :param err_xmit_url: str
        :param led_cfg_dict: dict
        """
        self.err_xmit_url = err_xmit_url
        info = inspect.getframeinfo(frame=inspect.stack()[1][0])
        err_msg_base = 'FILE: ' + info.filename + ' ' + \
            'FUNCTION: ' + info.function

        # Create LED object for pixels attached to given pin
        try:
            self.led = rpi_ws281x.PixelStrip(
                num=led_cfg_dict['count'],
                pin=led_cfg_dict['pin'],
                freq_hz=led_cfg_dict['freq_hz'],
                dma=led_cfg_dict['dma'],
                invert=led_cfg_dict['invert'],
                brightness=led_cfg_dict['brightness'],
                channel=led_cfg_dict['channel'],
                strip_type=rpi_ws281x.SK6812_STRIP_GRBW
            )
            self.led.begin()

            log = 'LEDs initialized.'
            logger.info(msg=log)
            print(log)

            self.off()

        except Exception as exc:
            log = 'Failed to initialize LEDs.'
            logger.error(msg=log)
            logger.error(msg=exc)
            print(log)
            print(exc)

            err_msg = err_msg_base + ' ' + \
                'MESSAGE: ' + log + '\n'
            errors.errors(
                err_xmit_url=self.err_xmit_url,
                err_msg=err_msg
            )

    def on(
        self,
        led_set_dict: dict
    ) -> bool:
        """
        Turns on LED strip and passes to each identical settings

        :param led_set_dict: dict

        :return led_on_err: bool
        """
        info = inspect.getframeinfo(frame=inspect.stack()[1][0])
        err_msg_base = 'FILE: ' + info.filename + ' ' + \
            'FUNCTION: ' + info.function

        led_on_err = False

        try:
            for pixel in range(self.led.numPixels()):
                self.led.setPixelColor(
                    n=pixel,
                    color=self.color(
                        red=led_set_dict['r'],
                        green=led_set_dict['g'],
                        blue=led_set_dict['b'],
                        white=led_set_dict['w']
                    )
                )
                self.led.show()

            log = 'Successfully turned on LEDs.'
            logger.info(msg=log)
            print(log)

        except Exception as exc:
            led_on_err = True
            log = 'Failed to turn on LEDs.'
            logger.error(msg=log)
            logger.error(msg=exc)
            print(log)
            print(exc)

            err_msg = err_msg_base + ' ' + \
                'MESSAGE: ' + log + '\n'
            errors.errors(
                err_xmit_url=self.err_xmit_url,
                err_msg=err_msg
            )

        return led_on_err

    def off(
        self
    ) -> bool:
        """
        Turns off LED strip

        :return led_off_err: bool
        """
        info = inspect.getframeinfo(frame=inspect.stack()[1][0])
        err_msg_base = 'FILE: ' + info.filename + ' ' + \
            'FUNCTION: ' + info.function

        led_off_err = False

        try:
            for pixel in range(self.led.numPixels()):
                self.led.setPixelColor(
                    n=pixel,
                    color=self.color()
                )
                self.led.show()

            log = 'Successfully turned off LEDs.'
            logger.info(msg=log)
            print(log)

        except Exception as exc:
            led_off_err = True
            log = 'Failed to turn off LEDs.'
            logger.error(msg=log)
            logger.error(msg=exc)
            print(log)
            print(exc)

            err_msg = err_msg_base + ' ' + \
                'MESSAGE: ' + log + '\n'
            errors.errors(
                err_xmit_url=self.err_xmit_url,
                err_msg=err_msg
            )

        return led_off_err

    @staticmethod
    def color(
        red: int = 0,
        green: int = 0,
        blue: int = 0,
        white: int = 0
    ) -> int:
        """Convert the provided red, green, blue color to a 24-bit color value.
        Each color component should be a value 0-255 where 0 is the lowest intensity
        and 255 is the highest intensity.
        """
        return (white << 24) | (red << 16) | (green << 8) | blue
