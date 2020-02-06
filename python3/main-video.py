#!/usr/bin/env python3
__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'


if __name__ == '__main__':
    import logging
    import logging.config
    import os
    import sys
    import time as ttime
    from common import picamera
    from config.core import CoreCfg
    from config.capture import CaptureCfg
    from config.log import LogCfg
    from datetime import *
    from tendo import singleton

    # Configure logging
    log_config_obj = LogCfg()
    logging.config.dictConfig(log_config_obj.config)
    logfile = 'januswm-video'
    logger = logging.getLogger(name=logfile)
    logging.getLogger(name=logfile).setLevel(level=logging.INFO)

    # Single instance
    try:
        me = singleton.SingleInstance()

    except singleton.SingleInstanceException:
        log = 'Duplicate capture process, shutting down.'
        logger.warning(msg=log)
        print(log)
        sys.exit(-1)

    for i in range(1, 6):
        logger.info(msg='')

    log = 'JanusWM Model logging started'
    logger.info(msg=log)

    core_cfg = CoreCfg()

    capture_cfg = CaptureCfg(core_cfg=core_cfg)
    err_xmit_url = capture_cfg.get(attrib='err_xmit_url')
    img_url_dict = capture_cfg.get(attrib='img_url_dict')
    led_cfg_dict = capture_cfg.get(attrib='led_cfg_dict')
    led_set_dict = capture_cfg.get(attrib='led_set_dict')
    cam_cfg_dict = capture_cfg.get(attrib='cam_cfg_dict')

    img_path_dict = core_cfg.get(attrib='img_path_dict')
    def model_video():

        timea = ttime.time()

        mov_orig_dtg = datetime.today().strftime('%Y-%m-%d_%H%M')
        mov_orig_name = 'mov_' + mov_orig_dtg + '_3%06d.h264'
        mov_orig_url = os.path.join(
            img_path_dict['mov'],
            mov_orig_name
        )

        # Record time in minutes
        record_time = 5
        time_record = 1000 * 60 * record_time
        picamera.video(
            err_xmit_url=err_xmit_url,
            led_cfg_dict=led_cfg_dict,
            led_set_dict=led_set_dict,
            cam_cfg_dict=cam_cfg_dict,
            img_orig_url=mov_orig_url,
            time_record=time_record
        )

        print('Model execution time elapsed: {0} sec'.format(ttime.time() - timea))

    model_video()
