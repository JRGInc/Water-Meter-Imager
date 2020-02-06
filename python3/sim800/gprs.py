__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import logging
import RPi.GPIO as GPIO
import serial
import socket
import time as ttime

logfile = 'januswm-transmit'
logger = logging.getLogger(logfile)


class Sim800(object):
    def __init__(
        self
    ) -> None:
        """
        Instantiates Sim800 object
        """
        self.port = None

    @staticmethod
    def reset(
    ) -> None:
        """Resets Sim800"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(
            22,
            GPIO.OUT
        )
        GPIO.output(
            22,
            False
        )
        ttime.sleep(3)
        GPIO.output(
            22,
            True
        )
        ttime.sleep(3)
        GPIO.output(
            22,
            False
        )
        GPIO.cleanup(22)
        ttime.sleep(5)
        log = 'Sim800 reset executed.'
        logger.info(msg=log)
        print(log)

    def port_open(
        self
    ) -> bool:
        """
        Opens serial port to Sim800

        :return port_ser_err: bool
        """
        port_ser_err = False

        try:
            self.port = serial.Serial(
                port="/dev/ttyAMA0",
                baudrate=115200,
                timeout=1
            )
            log = 'Serial port opened for Sim800, settings:'
            logger.info(msg=log)
            print(log)
            log = self.port.get_settings()
            logger.info(msg=log)
            print(log)

        except serial.SerialException:
            port_ser_err = True
            log = 'Serial library failed to connect to Sim800.'
            logger.error(msg=log)
            print(log)

        return port_ser_err

    def port_close(
        self
    ) -> None:
        """
        Closes serial port to Sim800
        """

        self.port.close()
        log = 'Serial port closed for Sim800.'
        logger.info(msg=log)

    def port_cmd(
        self,
        port_cmd: str,
        port_args: str = ''
    ) -> bool:
        """
        Writes AT command to serial port

        :param port_cmd: str
        :param port_args: str

        :return port_cmd_err: bool
        """
        try:
            port_msg_raw = port_cmd + port_args
            port_msg = port_msg_raw + '\r'
            self.port.write(data=port_msg.encode())
            port_cmd_err = self.response(port_msg=port_msg_raw)

        except serial.SerialException:
            port_cmd_err = True
            log = 'Serial library failed to execute Sim800 command.'
            logger.error(msg=log)
            print(log)

        return port_cmd_err

    def port_data(
        self,
        port_cmd: str,
        port_args: str,
        data_pkt: bytes
    ) -> bool:
        """
        Writes raw data to serial port

        :param port_cmd: str
        :param port_args: str
        :param data_pkt: bytes

        :return port_cmd_err: bool
        """
        try:
            port_msg_raw = port_cmd + port_args
            port_msg = port_msg_raw + '\r'
            self.port.write(data=port_msg.encode())
            port_cmd_err = self.response(port_msg=port_msg_raw)
            if not port_cmd_err:
                self.port.write(data=data_pkt)
                port_cmd_err = self.response(port_msg='DATA')

        except serial.SerialException:
            port_cmd_err = True
            log = 'Serial library failed to send Sim800 data packet.'
            logger.error(msg=log)
            print(log)

        return port_cmd_err

    def response(
        self,
        port_msg: str,
    ) -> bool:
        """
        Reads response from serial port

        :param port_msg: str

        :return port_msg_err: bool
        """
        port_msg_err = False

        log = 'Sim800 ' + port_msg + ' response'
        logger.info(msg=log)
        print(log)

        blank_count = 0
        while True:
            port_line = self.port.readline()
            try:
                port_line = port_line.decode('utf-8').split(sep='\r\n')[0]
                if (port_line != '') and (not port_line.isspace()):
                    logger.info(msg=port_line)
                    print(port_line)
            except Exception as exc:
                logger.debug(msg=exc)
                print(exc)

            if port_msg == 'AT+SAPBR=3,1,"Contype","GPRS"':
                if port_line == 'SMS Ready':
                    break

                if port_line == '':
                    blank_count += 1
                if blank_count == 240:
                    port_msg_err = True
                    break

                ttime.sleep(0.25)

            elif port_msg == 'AT+SAPBR=3,1,"APN","fast.t-mobile.com"':
                if port_line == 'OK':
                    break

                if port_line == '':
                    blank_count += 1
                if blank_count == 240:
                    port_msg_err = True
                    break

                ttime.sleep(0.25)

            elif port_msg == 'AT+SAPBR=1,1':
                if port_line == 'OK':
                    break

                if port_line == '':
                    blank_count += 1
                if blank_count == 240:
                    port_msg_err = True
                    break

                ttime.sleep(0.25)

            elif port_msg == 'AT+SAPBR=2,1':
                if port_line == 'OK':
                    break

                if port_line == '':
                    blank_count += 1
                if blank_count == 240:
                    port_msg_err = True
                    break

                ttime.sleep(0.25)

            elif port_msg[:11] == 'AT+HTTPDATA':
                if port_line == 'DOWNLOAD':
                    break

            elif port_msg[:13] == 'AT+HTTPACTION':
                if port_line[:18] == '+HTTPACTION: 1,200':
                    logger.info('Sim800 experienced a successful upload.')
                elif port_line[:18] == '+HTTPACTION: 1,415':
                    logger.warning('Sim800 attempted to upload unsupported media type.')
                elif port_line[:18] == '+HTTPACTION: 1,502':
                    port_msg_err = True
                    logger.error('Sim800 experienced a server error.')
                elif port_line[:18] == '+HTTPACTION: 1,601':
                    port_msg_err = True
                    logger.error('Sim800 experienced a network error.')

                if port_line[:12] == '+HTTPACTION:':
                    break

            else:
                if port_line == 'OK':
                    break
                elif port_line == 'NORMAL POWER DOWN':
                    break
                ttime.sleep(0.05)

            if port_line == 'ERROR':
                port_msg_err = True
                break

        return port_msg_err

    def http_start(
        self,
        gprs_set_dict: dict
    ) -> bool:
        """
        Starts http post sequence

        :param gprs_set_dict: dict

        :return http_cmd_err: bool
        """
        http_cmd_err = True
        ser_err = False
        count = 0

        while http_cmd_err and (count < 3):
            if count > 0:
                log = 'Sim800 experienced error in configuring GPRS service, closing serial, ' +\
                      'resetting Sim800, reattempting.'
                logger.warning(msg=log)
                print(log)
                self.port_close()
                self.reset()
                ser_err = self.port_open()

            if not ser_err:
                http_cmd_err = self.port_cmd(
                    port_cmd='AT+SAPBR',
                    port_args='=3,1,"Contype","GPRS"'
                )
            count += 1

        if not http_cmd_err:
            self.port_cmd(
                port_cmd='AT+CSQ',
                port_args=''
            )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+SAPBR',
                port_args='=3,1,"APN","{0}"'.format(gprs_set_dict['sock'])
            )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+SAPBR',
                port_args='=1,1'
            )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+SAPBR',
                port_args='=2,1'
            )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+HTTPINIT',
                port_args=''
            )

        return http_cmd_err

    def http_sendrecv(
        self,
        gprs_set_dict: dict,
        host_name: str,
        content_type: str,
        data_pkt: bytes
    ) -> bool:
        """
        Executes http send/receive commands

        :param gprs_set_dict: dict
        :param host_name: str
        :param content_type: str
        :param data_pkt: bytes

        :return http_cmd_err: bool
        """
        http_cmd_err = self.port_cmd(
            port_cmd='AT+HTTPPARA',
            port_args='="CID",1'
        )

        if not http_cmd_err:
            port_args = '="URL","{0}:{1}/upload"'.\
                format(
                    gprs_set_dict['addr'],
                    gprs_set_dict['port']
                )
            http_cmd_err = self.port_cmd(
                port_cmd='AT+HTTPPARA',
                port_args=port_args
            )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+HTTPPARA',
                port_args='="UA","{0}"'.format(host_name)
            )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+HTTPPARA',
                port_args='="CONTENT","{0}"'.format(content_type)
            )

        if not http_cmd_err:
            http_cmd_err = self.port_data(
                port_cmd='AT+HTTPDATA',
                port_args='={0},120000'.format(len(data_pkt)),
                data_pkt=data_pkt
            )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+HTTPACTION',
                port_args='=1'
            )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+HTTPREAD',
                port_args=''
            )

        return http_cmd_err

    def http_stop(
        self
    ) -> bool:
        """
        Stops http post sequence

        :return http_cmd_err: bool
        """
        http_cmd_err = self.port_cmd(
            port_cmd='AT+SAPBR',
            port_args='=0,1'
        )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+CPOWD',
                port_args='=1'
            )

        return http_cmd_err

    def nettime_en(
        self,
    ) -> bool:
        """
        Enables receipt of cellular network time

        :return net_time_err: bool
        """
        net_time_err = self.port_cmd(
            port_cmd='AT+CLTS',
            port_args='=1'
        )

        return net_time_err

    def nettime_get(
        self,
    ) -> bool:
        """
        Gets cellular network time

        :return net_time_err: bool
        :return net_time: str
        """
        net_time_err = self.port_cmd(
            port_cmd='AT+CCLK?',
            port_args=''
        )

        return net_time_err

    def http_upload(
        self,
        gprs_set_dict: dict,
        file_url_local: str,
        file_url_xmit: str
    ) -> [bool, bool]:
        """
        Executes http file upload

        :param gprs_set_dict: dict
        :param file_url_local: str
        :param file_url_xmit: str

        :return http_cmd_err: bool
        """
        ser_err = self.port_open()
        http_cmd_err = True

        if not ser_err:

            # Build connection and execute upload
            http_cmd_err = self.http_start(
                gprs_set_dict=gprs_set_dict
            )

            if not http_cmd_err:
                # Determine content type for HTML header and build
                if file_url_xmit.split('.')[1] == 'txt':
                    content_type = 'text/plain'
                elif file_url_xmit.split('.')[1] == 'log':
                    content_type = 'text/plain'
                else:
                    content_type = 'application/octet-stream'

                with open(file=file_url_local, mode='rb') as text_file:
                    data_pkt = text_file.read()

                http_cmd_err = self.http_sendrecv(
                    gprs_set_dict=gprs_set_dict,
                    host_name=file_url_xmit,
                    content_type=content_type,
                    data_pkt=data_pkt
                )

            # Send HTTP stop and close messages
            if not http_cmd_err:
                http_cmd_err = self.http_stop()
            self.port_close()

        else:
            log = 'Failed to open serial port to SIM 800.'
            logger.error(msg=log)
            print(log)

        return http_cmd_err, ser_err

    def http_updateconfig(
        self,
        gprs_set_dict: dict
    ) -> [bool, bool]:
        """
        Requests remote update of local capture.ini file

        :param gprs_set_dict: dict

        :return http_cmd_err: bool
        """
        host_name = socket.gethostname()
        ser_err = self.port_open()
        http_cmd_err = True

        if not ser_err:

            # Build connection and execute upload
            http_cmd_err = self.http_start(
                gprs_set_dict=gprs_set_dict
            )

            # Build constant and HTML header, then combine and send
            if not http_cmd_err:
                content_type = 'application/json'
                json_str = '{"remote":"update","file":"config","size":"0"}'
                data_pkt = json_str.encode()

                http_cmd_err = self.http_sendrecv(
                    gprs_set_dict=gprs_set_dict,
                    host_name=host_name,
                    content_type=content_type,
                    data_pkt=data_pkt
                )

            # Send HTTP stop and close messages
            if not http_cmd_err:
                http_cmd_err = self.http_stop()
            self.port.close()

        else:
            log = 'Failed to open serial port to SIM 800.'
            logger.error(msg=log)
            print(log)

        return http_cmd_err, ser_err
