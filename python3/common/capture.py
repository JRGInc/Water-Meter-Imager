#!/usr/bin/env python3
__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import logging
from common import img_ops, picamera

logfile = 'januswm-capture'
logger = logging.getLogger(logfile)


def capture(
    capture_cfg: any
) -> bool:
    """
    Captures image, processes captured image, makes TensorFlow
    prediction, then transmits image

    :param capture_cfg: any

    :return: err_vals_dict['img_redx']: bool
    """
    # Error values dictionary
    err_vals_dict = {
        'img_orig': True,
        'img_redx': True
    }

    # Load configuration settings
    img_url = capture_cfg.get(attrib='img_url')
    led_cfg_dict = capture_cfg.get(attrib='led_cfg_dict')
    led_set_dict = capture_cfg.get(attrib='led_set_dict')
    cam_cfg_dict = capture_cfg.get(attrib='cam_cfg_dict')
    err_xmit_url = capture_cfg.get(attrib='err_xmit_url')

    print(img_url)
    img_orig, err_vals_dict['img_orig'] = picamera.snap_shot(
        err_xmit_url=err_xmit_url,
        led_cfg_dict=led_cfg_dict,
        led_set_dict=led_set_dict,
        cam_cfg_dict=cam_cfg_dict
    )
    print('Capture error: {0}'.format(err_vals_dict['img_orig']))

    if not err_vals_dict['img_orig']:
        err_vals_dict['img_redx'] = img_ops.reduce(
            img_orig_stream=img_orig,
            err_xmit_url=err_xmit_url,
            img_orig_url=img_url,
            img_dest_url=img_url,
            img_dest_qual=cam_cfg_dict['quality'],
        )
        print('Reduction error: {0}'.format(err_vals_dict['img_redx']))

    return err_vals_dict['img_redx']
