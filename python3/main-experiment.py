#!/usr/bin/env python3
__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

if __name__ == '__main__':
    import logging
    import logging.config
    import os
    import sys
    import time as ttime
    from auxiliary import picamera
    from common import file_ops
    from config.core import CoreCfg
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

    qualities = [
        100,
        90,
        80,
        70,
        60,
        50,
        40,
        30,
        20,
        10
    ]

    core_cfg = CoreCfg()
    cfg_url_dict = core_cfg.get(attrib='cfg_url_dict')
    img_path_dict = core_cfg.get(attrib='img_path_dict')
    data_path_dict = core_cfg.get(attrib='data_path_dict')
    img_orig_dtg = datetime.today().strftime('%Y-%m-%d_%H%M')

    err_xmit_name = 'errors_' + img_orig_dtg + '.txt'
    err_xmit_url = os.path.join(
        data_path_dict['xmit'],
        err_xmit_name
    )
    led_cfg_dict = {
        'count': 2,            # Number of LED pixels.
        'pin': 18,            # GPIO pin connected to the pixels (18 uses PWM!).
        'freq_hz': 800000,    # LED signal frequency in hertz (usually 800khz)
        'dma': 10,            # DMA channel to use for generating signal (try 10)
        'brightness': 255,    # Set to 0 for darkest and 255 for brightest
        'invert': False,    # True to invert the signal (when using NPN transistor level shift)
        'channel': 0        # set to '1' for GPIOs 13, 19, 41, 45 or 53
    }
    led_set_dict = {
        'r': 100,
        'g': 100,
        'b': 100,
        'w': 255
    }
    cam_cfg_dict = {
        'mode': 2,
        'width': 3280,
        'height': 2464,
        'shutter': 100000,              # Microseconds, 0 = auto
        'sharpness': 100,               # -100 to 100, 0 = default
        'saturation': 0,                # -100 to 100, 0 = default
        'rotation': 180,                # 0 to 359 degrees
        'exposure': 'antishake'         # exposure setting
    }
    resolution_list = [
        None,
        None,
        # [
        #     {
        #         'resolution': '03',
        #         'width': 1080,
        #         'height': 1080
        #     },
        #     {
        #         'resolution': '05',
        #         'width': 960,
        #         'height': 960
        #     },
        #     # {
        #     #     'resolution': '03',
        #     #     'width': 1440,
        #     #     'height': 1080
        #     # },
        #     # {
        #     #     'resolution': '04',
        #     #     'width': 1400,
        #     #     'height': 1050
        #     # },
        #     # {
        #     #     'resolution': '05',
        #     #     'width': 1280,
        #     #     'height': 960
        #     # },
        #     # {
        #     #     'resolution': '06',
        #     #     'width': 1224,
        #     #     'height': 918
        #     # },
        #     # {
        #     #     'resolution': '07',
        #     #     'width': 1152,
        #     #     'height': 864
        #     # },
        #     # {
        #     #     'resolution': '08',
        #     #     'width': 1024,
        #     #     'height': 768
        #     # },
        #     # {
        #     #     'resolution': '09',
        #     #     'width': 960,
        #     #     'height': 720
        #     # },
        #     # {
        #     #     'resolution': '10',
        #     #     'width': 800,
        #     #     'height': 600
        #     # },
        #     # {
        #     #     'resolution': '11',
        #     #     'width': 768,
        #     #     'height': 576
        #     # },
        #     # {
        #     #     'resolution': '12',
        #     #     'width': 640,
        #     #     'height': 480
        #     # }
        # ],
        [
            {
                'resolution': '00',
                'width': 1200,
                'height': 1200
            },
            # {
            #     'resolution': '01',
            #     'width': 1536,
            #     'height': 1536
            # },
            # {
            #     'resolution': '02',
            #     'width': 1200,
            #     'height': 1200
            # },
            # {
            #     'resolution': '01',
            #     'width': 2048,
            #     'height': 1536
            # },
            # {
            #     'resolution': '02',
            #     'width': 1600,
            #     'height': 1200
            # },
            # {
            #     'resolution': '03',
            #     'width': 1440,
            #     'height': 1080
            # },
            # {
            #     'resolution': '04',
            #     'width': 1400,
            #     'height': 1050
            # },
            # {
            #     'resolution': '05',
            #     'width': 1280,
            #     'height': 960
            # },
            # {
            #     'resolution': '06',
            #     'width': 1224,
            #     'height': 918
            # },
            # {
            #     'resolution': '07',
            #     'width': 1152,
            #     'height': 864
            # },
            # {
            #     'resolution': '08',
            #     'width': 1024,
            #     'height': 768
            # },
            # {
            #     'resolution': '09',
            #     'width': 960,
            #     'height': 720
            # },
            # {
            #     'resolution': '10',
            #     'width': 800,
            #     'height': 600
            # },
            # {
            #     'resolution': '11',
            #     'width': 768,
            #     'height': 576
            # },
            # {
            #     'resolution': '12',
            #     'width': 640,
            #     'height': 480
            # }
        ],
        None,
        None,
        # [
        #     {
        #         'resolution': '02',
        #         'width': 1200,
        #         'height': 1200
        #     },
        #     {
        #         'resolution': '03',
        #         'width': 1080,
        #         'height': 1080
        #     },
        #     # {
        #     #     'resolution': '02',
        #     #     'width': 1600,
        #     #     'height': 1200
        #     # },
        #     # {
        #     #     'resolution': '03',
        #     #     'width': 1440,
        #     #     'height': 1080
        #     # },
        #     # {
        #     #     'resolution': '04',
        #     #     'width': 1400,
        #     #     'height': 1050
        #     # },
        #     # {
        #     #     'resolution': '05',
        #     #     'width': 1280,
        #     #     'height': 960
        #     # },
        #     # {
        #     #     'resolution': '06',
        #     #     'width': 1224,
        #     #     'height': 918
        #     # },
        #     # {
        #     #     'resolution': '07',
        #     #     'width': 1152,
        #     #     'height': 864
        #     # },
        #     # {
        #     #     'resolution': '08',
        #     #     'width': 1024,
        #     #     'height': 768
        #     # },
        #     # {
        #     #     'resolution': '09',
        #     #     'width': 960,
        #     #     'height': 720
        #     # },
        #     # {
        #     #     'resolution': '10',
        #     #     'width': 800,
        #     #     'height': 600
        #     # },
        #     # {
        #     #     'resolution': '11',
        #     #     'width': 768,
        #     #     'height': 576
        #     # },
        #     # {
        #     #     'resolution': '12',
        #     #     'width': 640,
        #     #     'height': 480
        #     # }
        # ],
        # [
        #     {
        #         'resolution': '06',
        #         'width': 918,
        #         'height': 918
        #     },
        #     {
        #         'resolution': '07',
        #         'width': 864,
        #         'height': 864
        #     },
        #     # {
        #     #     'resolution': '06',
        #     #     'width': 1224,
        #     #     'height': 918
        #     # },
        #     # {
        #     #     'resolution': '07',
        #     #     'width': 1152,
        #     #     'height': 864
        #     # },
        #     # {
        #     #     'resolution': '08',
        #     #     'width': 1024,
        #     #     'height': 768
        #     # },
        #     # {
        #     #     'resolution': '09',
        #     #     'width': 960,
        #     #     'height': 720
        #     # },
        #     # {
        #     #     'resolution': '10',
        #     #     'width': 800,
        #     #     'height': 600
        #     # },
        #     # {
        #     #     'resolution': '11',
        #     #     'width': 768,
        #     #     'height': 576
        #     # },
        #     # {
        #     #     'resolution': '12',
        #     #     'width': 640,
        #     #     'height': 480
        #     # }
        # ],
        None,
        None,
        None,
        # [
        #     {
        #         'resolution': '09',
        #         'width': 960,
        #         'height': 720
        #     },
        #     {
        #         'resolution': '10',
        #         'width': 800,
        #         'height': 600
        #     },
        #     {
        #         'resolution': '11',
        #         'width': 768,
        #         'height': 576
        #     },
        #     {
        #         'resolution': '12',
        #         'width': 640,
        #         'height': 480
        #     }
        # ],
        # [
        #     {
        #         'resolution': '12',
        #         'width': 640,
        #         'height': 480
        #     }
        # ]
    ]

    test_url_str = os.path.join(
        img_path_dict['orig'],
        img_orig_dtg + '_pc_image_elapse_times.csv'
    )
    if not os.path.isfile(path=test_url_str):
        copy_err = file_ops.copy_file(
            data_orig_url=cfg_url_dict['hist'],
            data_dest_url=test_url_str
        )
        if not copy_err:
            open(test_url_str, 'w').close()

    for sensor_mode in range(0, len(resolution_list)):
        if resolution_list[sensor_mode] is not None:
            cam_cfg_dict['mode'] = sensor_mode
            print('SENSOR MODE: {0}'.format(sensor_mode))
            print(resolution_list[sensor_mode])
            for resolution in range(0, len(resolution_list[sensor_mode])):
                cam_cfg_dict['width'] = resolution_list[sensor_mode][resolution]['width']
                cam_cfg_dict['height'] = resolution_list[sensor_mode][resolution]['height']
                cam_cfg_dict['encoding'] = 'jpg'
                print(cam_cfg_dict)

                for qual in range(0, len(qualities)):
                    print('IMAGE QUALITY: {0}'.format(qualities[qual]))

                    img_orig_name = img_orig_dtg + '_pc_' + 'md' + str(cam_cfg_dict['mode']) + '_' + \
                        str(cam_cfg_dict['width']) + 'x' + str(cam_cfg_dict['height'])
                    if qualities[qual] < 100:
                        img_orig_name += '_q0' + str(qualities[qual]) + '.jpg'
                    else:
                        img_orig_name += '_q' + str(qualities[qual]) + '.jpg'

                    img_orig_url = os.path.join(
                        img_path_dict['orig'],
                        img_orig_name
                    )
                    print(img_orig_url)

                    timea = ttime.time()
                    img_orig, err_img_orig = picamera.snap_shot(
                        sw_mode='pc',
                        err_xmit_url=err_xmit_url,
                        led_cfg_dict=led_cfg_dict,
                        led_set_dict=led_set_dict,
                        cam_cfg_dict=cam_cfg_dict,
                        img_orig_url=img_orig_url,
                        img_orig_qual=qualities[qual]
                    )

                    img_xmit_err = picamera.reduce_image(
                        img_orig_stream=img_orig,
                        err_xmit_url=err_xmit_url,
                        img_orig_url=img_orig_url,
                        img_dest_url=img_orig_url,
                        img_dest_qual=qualities[qual],
                    )

                    time_elapse = ttime.time() - timea
                    print('JPG Capture error: {0}'.format(err_img_orig))
                    print('JPG Image capture time elapsed: {0} sec'.format(time_elapse))
                    print('\n\n')

                    data_in = [img_orig_url, time_elapse]
                    file_ops.f_request(
                        file_cmd='file_csv_appendlist',
                        file_name=test_url_str,
                        data_file_in=data_in
                    )

                    ttime.sleep(1.0)
