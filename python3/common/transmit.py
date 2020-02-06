#!/usr/bin/env python3
__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import logging
import time
from sim800.gprs import Sim800 as SimGPRS

logfile = 'januswm-transmit'
logger = logging.getLogger(logfile)


def transmit_data(
    gprs_set_dict: dict,
    file_url_local: str,
    file_url_xmit: str
) -> bool:
    """
    Transmits selected data

    :param gprs_set_dict: dict
    :param file_url_local: str
    :param file_url_xmit: str

    :return: xmit_err: bool
    """
    timea = time.time()
    xmit_err = False
    ser_err = False
    attempt = 0

    sim = SimGPRS()
    for attempt in range(0, gprs_set_dict['attempts']):
        log = 'Attempting to transmit file {0} to server.'.format(file_url_local)
        logger.info(msg=log)
        print(log)

        sim.reset()

        xmit_err, ser_err = sim.http_upload(
            gprs_set_dict=gprs_set_dict,
            file_url_local=file_url_local,
            file_url_xmit=file_url_xmit
        )

        if xmit_err:
            log = 'Experienced error during transmission of file {0}.'. \
                format(file_url_local, (attempt + 1))
            logger.warning(msg=log)
            print(log)

        if not xmit_err and not ser_err:
            break

    if xmit_err or ser_err:
        log = 'Failed to send file {0} after {1} attempt(s).'.\
            format(file_url_local, (attempt + 1))
        logger.error(msg=log)
        print(log)

    print('File transmission time elapsed: {0} sec'.format(time.time() - timea))

    return xmit_err


def update_config(
    gprs_set_dict: dict,
) -> bool:
    """
    Requests remote update of local capture.ini file

    :param gprs_set_dict: dict

    :return: xmit_err: bool
    """
    timea = time.time()
    xmit_err = False
    ser_err = False
    attempt = 0

    log = 'Attempting to retrieve capture.ini from server.'
    logger.info(msg=log)
    print(log)

    sim = SimGPRS()
    for attempt in range(0, gprs_set_dict['attempts']):
        sim.reset()

        xmit_err, ser_err = sim.http_updateconfig(
            gprs_set_dict=gprs_set_dict,
        )

        if not xmit_err and not ser_err:
            break

    if xmit_err or ser_err:
        log = 'Failed to request capture.ini update after {0} attempt(s).'.\
            format(attempt + 1)
        logger.error(msg=log)
        print(log)

    print('Request transmission time elapsed: {0} sec'.format(time.time() - timea))

    return xmit_err
