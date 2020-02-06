__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import logging
import os.path
from common import file_ops
from config.core import CoreCfg

logfile = 'januswm'
logger = logging.getLogger(logfile)


def errors(
    err_xmit_url: str,
    err_msg: str
) -> bool:
    """
    Places log error entry into transmit folder for transmission

    :param err_xmit_url: str
    :param err_msg: str

    :return copy_err: bool
    """
    core_cfg = CoreCfg()
    cfg_url_dict = core_cfg.get(attrib='cfg_url_dict')

    copy_err = False

    err_dtg = str(os.path.basename(err_xmit_url)).split('_')[1] + '_' + \
        str(os.path.basename(err_xmit_url).split('_')[2])
    err_msg = 'DATE-TIME: ' + err_dtg + '_' + err_msg

    if not os.path.isfile(path=err_xmit_url):
        copy_err = file_ops.copy_file(
            data_orig_url=cfg_url_dict['err'],
            data_dest_url=err_xmit_url
        )

        if not copy_err:
            file_ops.f_request(
                file_cmd='file_line_write',
                file_name=err_xmit_url,
                data_file_in=[err_msg]
            )

        else:
            log = 'Failed to append error message to file for error transmission'
            logger.error(log)
            print(log)

    else:
        file_ops.f_request(
            file_cmd='file_line_append',
            file_name=err_xmit_url,
            data_file_in=[err_msg]
        )

    return copy_err
