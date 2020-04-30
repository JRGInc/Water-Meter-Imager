__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import inspect
import logging
import os.path
from common import errors
from PIL import Image


logfile = 'januswm-capture'
logger = logging.getLogger(logfile)


def reduce(
    img_orig_stream,
    err_xmit_url: str,
    img_orig_url: str,
    img_dest_url: str,
    img_dest_qual: int = 100,
) -> (bool, str):
    """
    Crops and saves given image

    :param img_orig_stream
    :param err_xmit_url: dict
    :param img_orig_url: str
    :param img_dest_url: str
    :param img_dest_qual: int

    :return img_redx_err: bool
    """
    img_redx_err = False
    img_orig = None

    try:
        if img_orig_stream is not None:
            img_orig = Image.open(fp=img_orig_stream)
        elif os.path.isfile(path=img_orig_url):
            img_orig = Image.open(fp=img_orig_url)
        else:
            img_redx_err = True
            log = 'OS failed to locate image {0} to save.'. \
                format(img_orig_url)
            logger.error(msg=log)
            print(log)

            if not err_xmit_url == '':
                info = inspect.getframeinfo(frame=inspect.stack()[1][0])
                err_msg_base = 'FILE: ' + info.filename + ' ' + \
                    'FUNCTION: ' + info.function

                err_msg = err_msg_base + ' ' + \
                    'MESSAGE: ' + log + '\n'
                errors.errors(
                    err_xmit_url=err_xmit_url,
                    err_msg=err_msg
                )

        if not img_redx_err:
            img_orig.save(
                fp=img_dest_url,
                format='jpeg',
                optimize=True,
                quality=img_dest_qual
            )
            img_orig.close()

            log = 'PIL successfully reduced image {0}.'.\
                format(img_dest_url)
            logger.info(msg=log)

    except Exception as exc:
        img_redx_err = True
        log = 'PIL failed to reduce image {0}.'.format(img_dest_url)
        logger.error(msg=log)
        logger.error(msg=exc)
        print(log)
        print(exc)

        if not err_xmit_url == '':
            info = inspect.getframeinfo(frame=inspect.stack()[1][0])
            err_msg_base = 'FILE: ' + info.filename + ' ' + \
                'FUNCTION: ' + info.function

            err_msg = err_msg_base + ' ' + \
                'MESSAGE: ' + log + '\n'
            errors.errors(
                err_xmit_url=err_xmit_url,
                err_msg=err_msg
            )

    return img_redx_err
