__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import inspect
import logging
import os
import signal
from common import errors, led, os_cmd
from io import BytesIO
from picamera import PiCamera


def snap_shot(
    err_xmit_url: str,
    led_cfg_dict: dict,
    led_set_dict: dict,
    cam_cfg_dict: dict,
) -> (any, bool):
    """
    Captures and saves original image

    :param err_xmit_url: dict
    :param led_cfg_dict: dict
    :param led_set_dict: dict
    :param cam_cfg_dict: dict

    :return img_orig: stream
    :return img_orig_err: bool
    """
    logfile = 'januswm-capture'
    logger = logging.getLogger(logfile)

    info = inspect.getframeinfo(frame=inspect.stack()[1][0])
    err_msg_base = 'FILE: ' + info.filename + ' ' + \
        'FUNCTION: ' + info.function

    img_orig = None
    img_orig_err = False
    cmd_err_count = 0
    timeout = 30

    # Turn flash on
    flash = led.LED(
        err_xmit_url=err_xmit_url,
        led_cfg_dict=led_cfg_dict
    )
    led_on_err = flash.on(led_set_dict=led_set_dict)

    if not led_on_err:
        while cmd_err_count < 2:

            # signal.alarm(timeout)
            try:
                camera = PiCamera()
                camera.sensor_mode = cam_cfg_dict['mode']
                camera.resolution = (cam_cfg_dict['width'], cam_cfg_dict['height'])
                camera.shutter_speed = cam_cfg_dict['shutter']
                camera.sharpness = cam_cfg_dict['sharpness']
                camera.saturation = cam_cfg_dict['saturation']
                camera.rotation = cam_cfg_dict['rotation']
                camera.exposure_mode = cam_cfg_dict['exposure']
                img_orig = BytesIO()

                # Quality is handled by PIL next step downstream
                camera.capture(
                    output=img_orig,
                    format='jpeg',
                    quality=100
                )
                img_orig.seek(0)

                camera.close()
                break

            except Exception as exc:
                img_orig_err = True
                cmd_err_count += 1
                log = 'Timeout took place at {0} seconds'. \
                    format(timeout)
                logger.error(msg=exc)
                logger.error(msg=log)
                print(exc)
                print(log)

                err_msg = err_msg_base + ' ' + \
                    'MESSAGE: ' + log + '\n'
                errors.errors(
                    err_xmit_url=err_xmit_url,
                    err_msg=err_msg
                )

    else:
        img_orig_err = True

        log = 'LED flash failed to fire, no image captured.'
        logger.error(msg=log)

        err_msg = err_msg_base + ' ' + \
            'MESSAGE: ' + log + '\n'
        errors.errors(
            err_xmit_url=err_xmit_url,
            err_msg=err_msg
        )

    # Turn flash off
    flash.off()

    return img_orig, img_orig_err


def video(
    err_xmit_url: str,
    led_cfg_dict: dict,
    led_set_dict: dict,
    cam_cfg_dict: dict,
    img_orig_url: str,
    time_record: int,
) -> bool:
    """
    Captures and saves video

    :param err_xmit_url: dict
    :param led_cfg_dict: dict
    :param led_set_dict: dict
    :param cam_cfg_dict: dict
    :param img_orig_url: str
    :param time_record: int

    :return img_orig_err: bool
    """
    logfile = 'januswm-video'
    logger = logging.getLogger(logfile)

    info = inspect.getframeinfo(frame=inspect.stack()[1][0])
    err_msg_base = 'FILE: ' + info.filename + ' ' + \
        'FUNCTION: ' + info.function

    img_orig_err = False
    cmd_err_count = 0
    rstill_check = False
    timeout = time_record + 10

    def timeout_handler(
        signum,
        frame
    ):
        raise Exception('Timeout occurred for raspistill capture')

    signal.signal(
        signal.SIGALRM,
        timeout_handler
    )

    # Turn flash on
    flash = led.LED(
        err_xmit_url=err_xmit_url,
        led_cfg_dict=led_cfg_dict
    )
    led_on_err = flash.on(led_set_dict=led_set_dict)

    if not led_on_err:
        while cmd_err_count < 2:

            signal.alarm(timeout)
            try:

                cmd_str0 = 'raspivid ' +\
                    '-ss ' + str(cam_cfg_dict['shutter']) + ' ' +\
                    '-sh ' + str(cam_cfg_dict['sharpness']) + ' ' +\
                    '-sa ' + str(cam_cfg_dict['saturation']) + ' ' +\
                    '-rot ' + str(cam_cfg_dict['rotation']) + ' ' + \
                    '-fps 5 ' +\
                    '-sg 60000 ' + \
                    '-t ' + str(time_record) + ' ' +\
                    '-n ' +\
                    '-o ' + img_orig_url

                cmd_err0, rtn_code0, std_out0 = os_cmd.os_cmd(
                    err_xmit_url=err_xmit_url,
                    cmd_str=cmd_str0
                )

                if (not cmd_err0) and (rtn_code0 == 0):
                    break

                else:
                    img_orig_err = True
                    cmd_err_count += 1

                    if rtn_code0 == 64:
                        log = 'Bad command line parameter for raspistill'. \
                            format(img_orig_url, rtn_code0)
                        logger.error(msg=log)

                        err_msg = err_msg_base + ' ' +\
                            'MESSAGE: ' + log + '\n'
                        errors.errors(
                            err_xmit_url=err_xmit_url,
                            err_msg=err_msg
                        )
                        break

                    elif rtn_code0 == 70:
                        rstill_check = True

                        log = 'Software or camera error for raspistill'. \
                            format(img_orig_url, rtn_code0)
                        logger.error(msg=log)

                        err_msg = err_msg_base + ' ' + \
                            'MESSAGE: ' + log + '\n'
                        errors.errors(
                            err_xmit_url=err_xmit_url,
                            err_msg=err_msg
                        )

                    else:
                        signal.alarm(0)
                        break

            except Exception as exc:
                img_orig_err = True
                cmd_err_count += 1
                rstill_check = True
                log = 'Timeout took place at {0} seconds'. \
                    format(timeout)
                logger.error(msg=exc)
                logger.error(msg=log)
                print(exc)
                print(log)

                err_msg = err_msg_base + ' ' + \
                    'MESSAGE: ' + log + '\n'
                errors.errors(
                    err_xmit_url=err_xmit_url,
                    err_msg=err_msg
                )

            finally:
                signal.alarm(0)

            if not rstill_check:
                log = 'Checking if raspistill improperly shutdown.'
                logger.info(msg=log)
                print(log)

                cmd_str1 = 'ps ' + \
                           '-aux'
                cmd_err1, rtn_code1, std_out1 = os_cmd.os_cmd(
                    err_xmit_url=err_xmit_url,
                    cmd_str=cmd_str1
                )

                if not cmd_err1:
                    processes = std_out1.split('\n')
                    logger.info(msg=processes[0])
                    print(processes[0])

                    nbr_fields = len(processes[0].split()) - 1
                    found_pid = False
                    for line in processes:
                        fields = line.split(None, nbr_fields)
                        if fields and (fields[0] == 'root') and ('raspistill' in fields[nbr_fields]):
                            found_pid = True
                            logger.info(msg=line)
                            print(line)
                            os.kill(
                                int(fields[1]),
                                signal.SIGTERM
                            )

                            err_msg = err_msg_base + ' ' + \
                                'MESSAGE: ' + 'Killed raspistill process.' + '\n'
                            errors.errors(
                                err_xmit_url=err_xmit_url,
                                err_msg=err_msg
                            )

                    if not found_pid:
                        log = 'No raspistill processes found.'
                        logger.info(msg=log)
                        print(log)

                        err_msg = err_msg_base + ' ' + \
                            'MESSAGE: ' + log + '\n'
                        errors.errors(
                            err_xmit_url=err_xmit_url,
                            err_msg=err_msg
                        )

    else:
        img_orig_err = True

        log = 'LED flash failed to fire, no image captured.'
        logger.error(msg=log)

        err_msg = err_msg_base + ' ' + \
            'MESSAGE: ' + log + '\n'
        errors.errors(
            err_xmit_url=err_xmit_url,
            err_msg=err_msg
        )

    # Turn flash off
    flash.off()

    return img_orig_err
