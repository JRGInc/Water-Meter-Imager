#!/usr/bin/env python3
__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'


if __name__ == '__main__':
    import logging
    import logging.config
    import os
    import shutil
    import sys
    import time as ttime
    from common import capture, file_ops
    from config.core import CoreCfg
    from config.capture import CaptureCfg
    from config.log import LogCfg
    from datetime import *
    from tendo import singleton

    # Configure logging
    log_config_obj = LogCfg()
    logging.config.dictConfig(log_config_obj.config)
    logfile = 'januswm-capture'
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

    log = 'JanusWM Capture logging started'
    logger.info(msg=log)

    core_cfg = CoreCfg()
    core_path_dict = core_cfg.get(attrib='core_path_dict')
    cfg_url_dict = core_cfg.get(attrib='cfg_url_dict')

    timea = ttime.time()

    minute = int(datetime.today().strftime('%M'))
    hour = int(datetime.today().strftime('%H'))
    execution_minute = (hour * 60) + minute

    capture_cfg = CaptureCfg(core_cfg=core_cfg)

    img_seq = capture_cfg.get(attrib='img_seq')
    img_orig_dtg = capture_cfg.get(attrib='img_orig_dtg')
    img_url = capture_cfg.get(attrib='img_url')
    img_capt_dict = capture_cfg.get(attrib='img_capt_dict')
    err_xmit_url = capture_cfg.get(attrib='err_xmit_url')

    print(execution_minute)
    log = 'Capture execution minute: {0}'.format(execution_minute)
    logger.info(msg=log)

    img_capt_err = False
    if img_capt_dict['img_capt_freq'] > 0:
        if not (execution_minute % img_capt_dict['img_capt_freq']):
            img_capt_err = capture.capture(
                capture_cfg=capture_cfg
            )

    if not img_capt_err:
        if img_capt_dict['img_xmit_freq'] > 0:
            if not (execution_minute % img_capt_dict['img_xmit_freq']):
                if os.path.isfile(path=img_url):
                    shutil.copy2(
                        src=img_url,
                        dst=core_path_dict['xmit']
                    )

        if img_capt_dict['img_xmit_freq'] == 1:
            set_err, msg = capture_cfg.set(
                section='Capture_Settings',
                attrib='image_xmit_freq',
                value='0'
            )

        if img_capt_dict['img_capt_freq'] == 1:
            set_err, msg = capture_cfg.set(
                section='Capture_Settings',
                attrib='image_capture_freq',
                value='0'
            )

        # increment image sequence only after image is captured,
        # even if there was an error
        img_seq = str(int(img_seq) + 1)
        file_ops.f_request(
            file_cmd='file_replace',
            file_name=cfg_url_dict['seq'],
            num_bytes=7,
            data_file_in=[img_seq]
        )

    print('Total capture execution time elapsed: {0} sec'.format(ttime.time() - timea))
