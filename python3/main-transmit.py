#!/usr/bin/env python3
__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'


if __name__ == '__main__':
    import glob
    import logging
    import logging.config
    import os
    import shutil
    import socket
    import sys
    import time as ttime
    from common import transmit
    from config.log import LogCfg, LOGPATHWMCAPT, LOGPATHWMXMIT
    from config.core import CoreCfg
    from config.transmit import TransmitCfg
    from datetime import *
    from pathlib import Path
    from tendo import singleton

    # Configure logging
    log_config_obj = LogCfg()
    logging.config.dictConfig(log_config_obj.config)
    logfile = 'januswm-transmit'
    logger = logging.getLogger(name=logfile)
    logging.getLogger(name=logfile).setLevel(level=logging.INFO)

    # Single instance
    try:
        me = singleton.SingleInstance()

    except singleton.SingleInstanceException:
        log = 'Duplicate transmit process, shutting down.'
        logger.warning(msg=log)
        print(log)
        sys.exit(-1)

    for i in range(1, 6):
        logger.info(msg='')

    log = 'JanusWM Transmit logging started'
    logger.info(msg=log)

    core_cfg = CoreCfg()

    timea = ttime.time()

    minute = int(datetime.today().strftime('%M'))
    hour = int(datetime.today().strftime('%H'))
    execution_minute = (hour * 60) + minute

    transmit_cfg = TransmitCfg(core_cfg=core_cfg)
    gprs_cfg_dict = transmit_cfg.get(attrib='gprs_cfg_dict')

    print(execution_minute)
    log = 'Transmission execution minute: {0}'.format(execution_minute)
    logger.info(msg=log)
    # Update not implemented yet
    # if not (execution_minute % update_freq):
    #     transmit.update_config(
    #         gprs_set_dict=gprs_cfg_dict
    #     )

    core_path_dict = core_cfg.get(attrib='core_path_dict')

    # Put last several logs into transmission directory if they exist
    max_history = 3
    directories = [LOGPATHWMCAPT, LOGPATHWMXMIT]
    try:
        for directory in directories:
            count = 0
            paths = sorted(
                Path(directory).iterdir(),
                key=os.path.getmtime,
                reverse=True
            )
            for logfile in paths:
                file_name, file_ext = os.path.splitext(str(logfile))
                file_name = os.path.basename(file_name)
                logfile_url = os.path.join(
                    directory,
                    str(logfile)
                )
                xmit_dtg = datetime.today().strftime('%Y-%m-%d_%H%M')
                if file_ext != '':
                    logfile = file_name + '_' + file_ext[1:]
                else:
                    logfile = file_name + '_0'
                log_name = 'logs_' + xmit_dtg + '_' + logfile + '.txt'
                transmit_url = os.path.join(
                    core_path_dict['xmit'],
                    log_name
                )
                shutil.copyfile(
                    src=logfile_url,
                    dst=transmit_url
                )
                count += 1
                if count >= max_history:
                    break

    except Exception as exc:
        log = 'Failed to copy logs to transmission directory.'
        logger.error(msg=log)
        logger.error(msg=exc)
        print(log)
        print(exc)

    host_name = socket.gethostname()
    while os.listdir(core_path_dict['xmit']):
        most_recent_url_str = max(
            glob.iglob(os.path.join(core_path_dict['xmit'] + '*')),
            key=os.path.getctime
        )
        print(most_recent_url_str)

        file_url_xmit = host_name + '_' + os.path.basename(most_recent_url_str)
        xmit_err = transmit.transmit_data(
            gprs_set_dict=gprs_cfg_dict,
            file_url_local=most_recent_url_str,
            file_url_xmit=file_url_xmit
        )

        if not xmit_err:
            os.remove(most_recent_url_str)

        else:
            log = 'Encountered problems transmitting files, will attempt again later.'
            logger.warning(msg=log)
            print(log)
            break

    print('Total transmission execution time elapsed: {0} sec'.format(ttime.time() - timea))
