__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import configparser
import logging

logfile = 'januswm-transmit'
logger = logging.getLogger(logfile)


class TransmitCfg(object):
    """
    Class attributes of configuration settings for transmission operations
    """
    def __init__(
        self,
        core_cfg: any
    ) -> None:
        """
        Sets object properties either directly or via ConfigParser from ini file

        :param core_cfg: any
        """
        cfg_url_dict = core_cfg.get('cfg_url_dict')
        self.ini_file = cfg_url_dict['xmit']
        self.config = configparser.ConfigParser()
        self.config.read_file(f=open(self.ini_file))

        # Update frequency in minutes, minimum = 60 min and maximum = 1440, 60 min intervals
        self.execution_int = self.config.getint(
            'Transmit_Settings',
            'execution_interval'
        )

        # Update frequency in minutes, minimum = 60 min and maximum = 1440, 60 min intervals
        self.update_freq = self.config.getint(
            'Update_Settings',
            'update_freq'
        )

        # Update frequency in minutes, minimum = 60 min and maximum = 1440, 60 min intervals
        self.update_freq = self.config.getint(
            'Update_Settings',
            'update_freq'
        )

        # GPRS settings dictionary
        self.gprs_cfg_dict = {
            'sock': 'fast.t-mobile.com',
            'addr': '198.13.81.243',
            'port': 4440,
            'attempts': self.config.getint(
                'Cellular_Configuration',
                'transmission_attempts'
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
        if attrib == 'exec_int':
            return self.execution_int
        elif attrib == 'update_freq':
            return self.update_freq
        elif attrib == 'gprs_cfg_dict':
            return self.gprs_cfg_dict

    def set(
        self,
        section: str,
        attrib: str,
        value: str
    ) -> (bool, str):
        """
        Sets configuration attributes by updating ini file

        :param section: str
        :param attrib: str
        :param value: str
        :return: set_err: bool
        """
        set_err = False
        valid_section = True
        valid_option = True
        valid_value = True
        log = ''

        if section == 'Transmit_Settings':
            if attrib == 'execution_interval':
                try:
                    if int(value) < 0:
                        log = 'Attribute value {0} is less than 1: {1}.'.format(attrib, value)
                        logger.error(msg=log)
                        log1 = 'Retaining previous value.'.format(attrib)
                        logger.warning(msg=log1)
                        valid_value = False

                    elif (int(value) > 1) and (int(value) < 60):
                        log = 'Attribute value {0} is greater than 1 and less than 60: {1}.'.format(attrib, value)
                        logger.error(msg=log)
                        log1 = 'Retaining previous value.'.format(attrib)
                        logger.warning(msg=log1)
                        valid_value = False

                    elif int(value) > 1440:
                        log = 'Attribute value {0} is greater than 1440: {1}.'.format(attrib, value)
                        logger.error(msg=log)
                        log1 = 'Retaining previous value.'.format(attrib)
                        logger.warning(msg=log1)
                        valid_value = False

                    else:
                        if not (int(value) == 60) and \
                                not (int(value) == 120) and \
                                not (int(value) == 180) and \
                                not (int(value) == 240) and \
                                not (int(value) == 360) and \
                                not (int(value) == 480) and \
                                not (int(value) == 720) and \
                                not (int(value) == 1440):
                            log = 'Attribute value {0} is not a valid value '.format(attrib) +\
                                  '(60, 120, 180, 240, 360, 480, 720, 1440): {0}.'.format(value)
                            logger.error(msg=log)
                            log1 = 'Retaining previous value.'.format(attrib)
                            logger.warning(msg=log1)
                            valid_value = False

                except ValueError:
                    log = 'Attribute value {0} is not an integer: {1}.'.format(attrib, value)
                    logger.error(msg=log)
                    log1 = 'Retaining previous value.'.format(attrib)
                    logger.warning(msg=log1)
                    valid_value = False

        elif section == 'Update_Settings':
            if attrib == 'update_freq':
                try:
                    if int(value) < 60:
                        log = 'Attribute value {0} is less than 60: {1}.'.format(attrib, value)
                        logger.error(msg=log)
                        log1 = 'Retaining previous value.'.format(attrib)
                        logger.warning(msg=log1)
                        valid_value = False

                    elif int(value) > 1440:
                        log = 'Attribute value {0} is greater than 1440: {1}.'.format(attrib, value)
                        logger.error(msg=log)
                        log1 = 'Retaining previous value.'.format(attrib)
                        logger.warning(msg=log1)
                        valid_value = False

                except ValueError:
                    log = 'Attribute value {0} is not an integer: {1}.'.format(attrib, value)
                    logger.error(msg=log)
                    log1 = 'Retaining previous value.'.format(attrib)
                    logger.warning(msg=log1)
                    valid_value = False

            else:
                valid_option = False

        elif section == 'Cellular_Settings':
            if attrib == 'transmission_attempts':
                try:
                    if int(value) < 1:
                        log = 'Attribute value {0} is less than 1: {1}.'.format(attrib, value)
                        logger.error(msg=log)
                        log1 = 'Retaining previous value.'.format(attrib)
                        logger.warning(msg=log1)
                        valid_value = False

                except ValueError:
                    log = 'Attribute value {0} is not an integer: {1}.'.format(attrib, value)
                    logger.error(msg=log)
                    log1 = 'Retaining previous value.'.format(attrib)
                    logger.warning(msg=log1)
                    valid_value = False

            else:
                valid_option = False

        else:
            valid_section = False
            valid_option = False

        if valid_section:
            if valid_option:
                if valid_value:
                    try:
                        self.config.set(
                            section=section,
                            option=attrib,
                            value=value
                        )
                        self.config.write(
                            fp=open(
                                file=self.ini_file,
                                mode='w',
                                encoding='utf-8'
                            ),
                            space_around_delimiters=True
                        )
                        log = 'ConfigParser successfully set and wrote options to file.'
                        logger.info(msg=log)
                    except Exception as exc:
                        log = 'ConfigParser failed to set and write options to file.'
                        logger.error(msg=log)
                        logger.error(msg=exc)
                        print(log)
                        print(exc)

            else:
                set_err = True
                log = 'ConfigParser failed to set and write options to file, invalid option.'
                logger.error(msg=log)

        else:
            set_err = True
            log = 'ConfigParser failed to set and write options to file, invalid section.'
            logger.error(msg=log)

        return set_err, log
