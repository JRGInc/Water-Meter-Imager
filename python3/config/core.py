__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import logging
import os

logfile = 'januswm'
logger = logging.getLogger(logfile)


class CoreCfg(object):
    """
    Class attributes of configuration settings for capture operations
    """

    def __init__(
            self
    ) -> None:
        """
        Sets object properties directly
        """
        self.base_dir = os.path.dirname('/opt/Janus/WM/')

        self.train_version = '019'
        self.test_version = '001'
        self.test_set = '005'

        # Define core paths
        core_dirs_dict = {
            'cfg':  'config/',
            'img':  'images/',
            'py3':  'python3/',
            'xmit': 'transmit/'
        }

        # Define core paths
        self.core_path_dict = {
            'cfg':  os.path.join(
                self.base_dir,
                core_dirs_dict['cfg']
            ),
            'img':  os.path.join(
                self.base_dir,
                core_dirs_dict['img']
            ),
            'py3':  os.path.join(
                self.base_dir,
                core_dirs_dict['py3']
            ),
            'xmit': os.path.join(
                self.base_dir,
                core_dirs_dict['xmit']
            )
        }

        # Define file names in /config path
        cfg_name_dict = {
            'capt': 'capture.ini',
            'err':  'errors.txt',
            'seq':  'sequence.txt',
            'xmit': 'transmit.ini'
        }

        # Define full urls for files in /config path
        self.cfg_url_dict = {
            'capt': os.path.join(
                self.core_path_dict['cfg'],
                cfg_name_dict['capt']
            ),
            'err': os.path.join(
                self.core_path_dict['cfg'],
                cfg_name_dict['err']
            ),
            'seq': os.path.join(
                self.core_path_dict['cfg'],
                cfg_name_dict['seq']
            ),
            'xmit': os.path.join(
                self.core_path_dict['cfg'],
                cfg_name_dict['xmit']
            )
        }

    def get(
        self,
        attrib: str
    ) -> any:
        """
        Gets configuration attributes

        :param attrib: str

        :return: any
        """
        if attrib == 'cptr_base_dir':
            return self.base_dir
        elif attrib == 'train_version':
            return self.train_version
        elif attrib == 'test_version':
            return self.test_version
        elif attrib == 'test_set':
            return self.test_set
        elif attrib == 'core_path_dict':
            return self.core_path_dict
        elif attrib == 'cfg_url_dict':
            return self.cfg_url_dict
