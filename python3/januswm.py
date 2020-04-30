#!/usr/bin/env python3
__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

# Initialize Application processes
if __name__ == '__main__':
    import logging
    import logging.config
    from config.core import CoreCfg
    from config.capture import CaptureCfg
    from config.log import LogCfg
    from config.transmit import TransmitCfg
    from crontab import CronTab

    # Configure logging
    log_config_obj = LogCfg()
    logging.config.dictConfig(config=log_config_obj.config)

    # Inject initial empty log entries for easy-to-spot visual markers
    logfile = 'januswm'
    logger = logging.getLogger(name=logfile)
    for i in range(1, 6):
        logger.info(msg='')

    log = 'JanusWM logging started'
    logger.info(msg=log)
    logging.getLogger(name=logfile).setLevel(level=logging.INFO)

    cron_sched = CronTab(user='pi')
    cron_sched.remove_all()
    cron_sched.write()

    log = 'Jobs listed in CRON at program start (possibly no entries):'
    logger.info(msg=log)
    print(log)
    for job in cron_sched:
        logger.info(msg=job)
        print(job)

    core_cfg = CoreCfg()
    capture_cfg = CaptureCfg(core_cfg=core_cfg)
    img_capt_dict = capture_cfg.get(attrib='img_capt_dict')

    transmit_cfg = TransmitCfg(core_cfg=core_cfg)
    xmit_exec_int = transmit_cfg.get(attrib='exec_int')

    job_capt = cron_sched.new(command='sudo python3 /opt/Janus/WM/python3/main-capture.py')
    job_capt.minute.every(img_capt_dict['exec_interval'])
    log = 'Setting capture execution to every {0} minutes.'.format(img_capt_dict['exec_interval'])
    logger.info(msg=log)

    job_xmit = cron_sched.new(command='sudo python3 /opt/Janus/WM/python3/main-transmit.py')
    # job_xmit.minute.every(3)
    job_xmit.hour.every(xmit_exec_int / 60)
    job_xmit.minute.on(25)
    log = 'Setting transmit execution to every {0} hour(s).'.format(xmit_exec_int / 60)
    logger.info(msg=log)

    cron_sched.write()

    log = 'Jobs listed in CRON after program start (no entries = cron error):'
    logger.info(msg=log)
    print(log)
    for job in cron_sched:
        logger.info(msg=job)
        print(job)
