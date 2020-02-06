__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import logging
import os
import RPi.GPIO as GPIO
import serial
import socket
import time as ttime
from datetime import *

logfile = 'januswm-transmit'
logger = logging.getLogger(logfile)


class Sim5320(object):
    def __init__(
        self
    ) -> None:
        """
        Instantiates Sim5320 object
        """
        self.port = None

    @staticmethod
    def reset(
    ) -> None:
        """Resets Sim5320"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(
            22,
            GPIO.OUT
        )
        GPIO.output(
            22,
            False
        )
        ttime.sleep(1)
        GPIO.output(
            22,
            True
        )
        ttime.sleep(1)
        GPIO.output(
            22,
            False
        )
        GPIO.cleanup(22)
        log = 'Sim5320 reset executed.'
        logger.info(log)

    def port_open(
        self
    ) -> bool:
        """
        Opens serial port to Sim5320

        :return port_ser_err: bool
        """
        port_ser_err = False

        try:
            self.port = serial.Serial(
                "/dev/ttyAMA0",
                baudrate=115200,
                timeout=1
            )
            logger.info('Serial port opened for Sim5320, settings:')
            logger.info(self.port.get_settings())

        except serial.SerialException:
            port_ser_err = True
            log = 'Serial library failed to connect to Sim5320.'
            logger.error(log)
            print(log)

        return port_ser_err

    def port_close(
        self
    ) -> None:
        """
        Closes serial port to Sim5320
        """
        self.port.close()
        logger.info('Serial port closed for Sim5320.')

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
            port_msg = port_cmd + port_args + '\r'
            self.port.write(port_msg.encode())
            port_cmd_err = self.response(port_cmd)

        except serial.SerialException:
            port_cmd_err = True
            logger.error('Serial library failed to execute Sim5320 command.')

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
            port_msg = port_cmd + port_args + '\r'
            self.port.write(port_msg.encode())
            port_cmd_err = self.response(port_cmd)
            if not port_cmd_err:
                self.port.write(data_pkt)
                port_cmd_err = self.response('DATA')

        except serial.SerialException:
            port_cmd_err = True
            logger.error('Serial library failed to send Sim5320 data packet.')

        return port_cmd_err

    def response(
        self,
        port_cmd: str,
    ) -> bool:
        """
        Reads response from serial port

        :param port_cmd: str

        :return port_cmd_err: bool
        """
        port_cmd_err = False

        log = 'Sim5320 ' + port_cmd + ' response:'
        logger.info(log)

        blank_count = 0
        port_event = ''
        while True:
            port_line = self.port.readline()
            try:
                port_line = port_line.decode('utf-8').split('\r\n')[0]
                if (port_line != '') and (not port_line.isspace()):
                    logger.info(port_line)
                    print(port_line)
            except Exception as exc:
                logger.debug(exc)

            if port_cmd == 'AT+CGSOCKCONT':
                if port_line == '':
                    blank_count += 1

                if blank_count == 20:
                    break

                ttime.sleep(0.250)

            elif port_cmd == 'AT+CHTTPSSEND':
                if port_line == '+CHTTPSNOTIFY: PEER CLOSED':
                    port_cmd_err = True
                    break

                if port_line == '>':
                    break

            elif port_cmd == 'AT+CHTTPSRECV':
                if port_line == '+CHTTPSNOTIFY: PEER CLOSED':
                    port_cmd_err = True
                    break

                if port_line == '+CHTTPS: RECV EVENT':
                    port_event = port_line
                    port_msg = 'AT+CHTTPSRECV=1024\r'
                    self.port.write(port_msg.encode())

                if (port_event == '+CHTTPS: RECV EVENT') and \
                        (port_line == '+CHTTPSRECV: 0'):
                    break

                if port_line == '':
                    blank_count += 1

                if blank_count == 50:
                    port_msg = 'AT+CHTTPSRECV=1024\r'
                    self.port.write(port_msg.encode())

                ttime.sleep(0.10)

            else:
                if port_line == 'OK':
                    break
                ttime.sleep(0.05)

            if port_line == 'ERROR':
                port_cmd_err = True
                break

        return port_cmd_err

    def http_start(
        self,
        gprs_set_dict: dict
    ) -> bool:
        """
        Starts http post sequence

        :param gprs_set_dict: dict

        :return http_cmd_err: bool
        """
        http_cmd_err = self.port_cmd(
            port_cmd='AT+CGSOCKCONT',
            port_args='=1,"IP","{0}",,0,0'.format(gprs_set_dict['sock'])
        )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+CSOCKSETPN',
                port_args='=1'
            )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+CHTTPSSTART',
                port_args=''
            )

        if not http_cmd_err:
            port_args = '="{0}",{1},1'.\
                format(
                    gprs_set_dict['addr'],
                    gprs_set_dict['port']
                )
            http_cmd_err = self.port_cmd(
                port_cmd='AT+CHTTPSOPSE',
                port_args=port_args
            )

        return http_cmd_err

    def http_sendrecv(
        self,
        data_pkt: str
    ) -> bool:
        """
        Executes http send/receive commands

        :param data_pkt: str

        :return http_cmd_err: bool
        """
        http_cmd_err = self.port_data(
            port_cmd='AT+CHTTPSSEND',
            port_args='=' + str(len(data_pkt)),
            data_pkt=data_pkt.encode()
        )

        if not http_cmd_err:
            http_cmd_err = self.port_cmd(
                port_cmd='AT+CHTTPSRECV',
                port_args='=1024'
            )

        return http_cmd_err

    def http_stop(
        self
    ):
        """
        Stops http post sequence
        """
        http_cmd_err = self.port_cmd(
            port_cmd='AT+CHTTPSCLSE',
            port_args=''
        )

        if not http_cmd_err:
            self.port_cmd(
                port_cmd='AT+CHTTPSSTOP',
                port_args=''
            )

    def http_upload(
        self,
        gprs_set_dict: dict,
        file_url: str
    ) -> [bool, bool]:
        """
        Executes http file upload

        :param gprs_set_dict: dict
        :param file_url: str

        :return http_cmd_err: bool
        """
        ser_err = self.port_open()
        http_cmd_err = True

        if not ser_err:

            # Build connection and execute upload
            http_cmd_err = self.http_start(gprs_set_dict)
            file_name = str(os.path.basename(file_url))

            if not http_cmd_err:

                # Set upload parameters
                host_name = socket.gethostname()

                # Add dtg stamp to filename
                txt_file_dtg = datetime.today().strftime('%Y-%m-%d_%H%M')
                if file_name.split('.')[1] == 'txt':
                    file_name = file_name.split('.')[0] + '_' + txt_file_dtg + '.txt'

                # Build content and HTML header, then combine and send
                json_str = '{' +\
                    '"remote":"' + host_name + '",' +\
                    '"file":"' + file_name + '",' +\
                    '"size":"' + str(os.path.getsize(file_url)) + '"' +\
                    '}'
                html_hdr = """
POST /upload HTTP/1.1
Content-Type: application/json
Content-Length: {0}
Host: {1}

""".\
                    format(
                        len(json_str),
                        gprs_set_dict['addr']
                    )
                data_pkt = html_hdr + json_str
                http_cmd_err = self.http_sendrecv(data_pkt)

            if not http_cmd_err:

                # Determine content type for HTML header and build
                if file_name.split('.')[1] == 'txt':
                    con_type = 'text/plain'
                elif file_name.split('.')[1] == 'log':
                    con_type = 'text/plain'
                else:
                    con_type = 'application/octet-stream'

                html_hdr = """
POST /upload HTTP/1.1
Content-Type: {0}
Content-Length: {1}
Host: {2}

""".\
                    format(
                        con_type,
                        os.path.getsize(file_url),
                        gprs_set_dict['addr']
                    )

                # Build and send successive HTML data packets
                with open(file_url, 'rb') as text_file:
                    data = text_file.read(4096 - len(html_hdr))
                    port_args = '=' + str(len(html_hdr) + len(data))
                    data_pkt = html_hdr.encode() + data

                    while len(data_pkt) > 0:
                        if not http_cmd_err:

                            http_cmd_err = self.port_data(
                                port_cmd='AT+CHTTPSSEND',
                                port_args=port_args,
                                data_pkt=data_pkt
                            )

                            if http_cmd_err:
                                break

                        data_pkt = text_file.read(4096)
                        port_args = '=' + str(len(data_pkt))

            if not http_cmd_err:
                http_cmd_err = self.port_cmd(
                    port_cmd='AT+CHTTPSRECV',
                    port_args='=1024'
                )

            # Send HTTP stop and close messages
            if not http_cmd_err:
                self.http_stop()
            self.port_close()

        else:
            log = 'Failed to open serial port to SIM 5320.'
            logger.error(log)
            print(log)

        return http_cmd_err, ser_err

    def http_clearlist(
        self,
        gprs_set_dict: dict
    ) -> [bool, bool]:
        ser_err = self.port_open()
        cmd_err = True

        if not ser_err:

            # Build connection and execute upload
            cmd_err = self.http_start(gprs_set_dict)

            if not cmd_err:

                # Build content and HTML header, then combine and send
                json_str = '{"remote":"list","file":"clear","size":"0"}'
                html_hdr = """
POST /upload HTTP/1.1
Content-Type: application/json
Content-Length: {0}
Host: {1}

""".\
                    format(
                        str(len(json_str)),
                        gprs_set_dict['addr']
                    )

                data_pkt = html_hdr + json_str
                cmd_err = self.http_sendrecv(data_pkt)

            # Send HTTP stop and close messages
            if not cmd_err:
                self.http_stop()
            self.port.close()

        else:
            log = 'Failed to open serial port to SIM 5320.'
            logger.error(log)
            print(log)

        return cmd_err, ser_err
