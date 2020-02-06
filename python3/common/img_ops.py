__author__ = 'Larry A. Hartman'
__company__ = 'Janus Research'

import cv2
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


def find_screws(
    img_scale,
    err_xmit_url: str,
    img_orig_url: str,
    img_screw_url: str,
    img_screw_ret: bool
) -> tuple:
    """
    Finds locations and sizes of screw heads and center needle pivot for given image

    :param img_scale
    :param err_xmit_url: dict
    :param img_orig_url: str
    :param img_screw_url: str
    :param img_screw_ret: bool

    :return img_screws: list
    :return img_screw_err: bool
    """
    img_screw_err = False
    img_screw_ang = 0.0
    img_screw_list = [None, None, None, None, None]
    left = 0
    right = 0
    upper = 0
    lower = 0
    radius = 0

    if os.path.isfile(path=img_orig_url):

        try:
            img_orig = cv2.imread(filename=img_orig_url)
            img_orig_h = img_orig.shape[0]
            img_scale_h = img_scale.shape[0]
            img_crop_dict = {}
            if img_orig_h <= 1080:
                img_crop_dict = {
                    'ulx': 350,
                    'uly': int(img_scale_h / 2) - 200,
                    'brx': 1350,
                    'bry': int(img_scale_h / 2) + 200
                }
            elif img_orig_h == 1536:
                img_crop_dict = {
                    'ulx': 675,
                    'uly': int(img_scale_h / 2) - 150,
                    'brx': 1265,
                    'bry': int(img_scale_h / 2) + 100
                }
            elif img_orig_h == 2464:
                img_crop_dict = {
                    'ulx': 1075,
                    'uly': int(img_scale_h / 2) - 200,
                    'brx': 2025,
                    'bry': int(img_scale_h / 2) + 200
                }

            img_screw = img_scale[
                img_crop_dict['uly']:img_crop_dict['bry'],
                img_crop_dict['ulx']:img_crop_dict['brx']
            ]

            img_gray = cv2.cvtColor(
                src=img_screw,
                code=cv2.COLOR_BGR2GRAY
            )
            img_blur = cv2.medianBlur(
                src=img_gray,
                ksize=5
            )

            circles = None

            if img_orig_h == 1536:
                circles = cv2.HoughCircles(
                    image=img_blur,
                    method=cv2.HOUGH_GRADIENT,
                    dp=2.5,
                    minDist=200,
                    param1=100,
                    param2=20,
                    minRadius=20,
                    maxRadius=60
                )
            elif img_orig_h == 2464:
                circles = cv2.HoughCircles(
                    image=img_blur,
                    method=cv2.HOUGH_GRADIENT,
                    dp=1.0,
                    minDist=300,
                    param1=100,
                    param2=30,
                    minRadius=30,
                    maxRadius=90
                )

            if circles is not None:
                for circle in range(0, len(circles[0])):
                    if left == 0:
                        left = circles[0][circle][0]
                        img_screw_list[0] = [int(i) for i in circles[0][circle].tolist()]
                    else:
                        if circles[0][circle][0] < left:
                            left = circles[0][circle][0]
                            img_screw_list[0] = [int(i) for i in circles[0][circle].tolist()]
                    if right == 0:
                        right = circles[0][circle][0]
                        img_screw_list[1] = [int(i) for i in circles[0][circle].tolist()]
                    else:
                        if circles[0][circle][0] > right:
                            right = circles[0][circle][0]
                            img_screw_list[1] = [int(i) for i in circles[0][circle].tolist()]

                    if upper == 0:
                        upper = circles[0][circle][1]
                        img_screw_list[2] = [int(i) for i in circles[0][circle].tolist()]
                    else:
                        if circles[0][circle][1] < upper:
                            upper = circles[0][circle][1]
                            img_screw_list[2] = [int(i) for i in circles[0][circle].tolist()]
                    if lower == 0:
                        lower = circles[0][circle][1]
                        img_screw_list[3] = [int(i) for i in circles[0][circle].tolist()]
                    else:
                        if circles[0][circle][1] > lower:
                            lower = circles[0][circle][1]
                            img_screw_list[3] = [int(i) for i in circles[0][circle].tolist()]

                    # Central pivot radius is always largest radius, place this circle in last list index
                    # This will work even if # of returned circles is 2, which sometimes occurs
                    if radius == 0:
                        radius = circles[0][circle][2]
                        img_screw_list[4] = [int(i) for i in circles[0][circle].tolist()]
                    else:
                        if circles[0][circle][2] > radius:
                            radius = circles[0][circle][2]
                            img_screw_list[4] = [int(i) for i in circles[0][circle].tolist()]

                    # copy grayed image to edges folder than perform this step to save image with overlaid lines,
                    # otherwise unnecessary
                    cv2.circle(
                        img=img_screw,
                        center=(
                            circles[0][circle][0],
                            circles[0][circle][1]
                        ),
                        radius=circles[0][circle][2],
                        color=(0, 0, 255),
                        thickness=3
                    )

                # Find and place central pivot circle at end of list
                # if circles[0][0][0] < circles[0][1][0] < circles[0][2][0] or \
                #         circles[0][2][0] < circles[0][1][0] < circles[0][0][0]:
                #     img_screw_list[4] = [int(i) for i in circles[0][1].tolist()]
                # elif circles[0][1][0] < circles[0][0][0] < circles[0][2][0] or \
                #         circles[0][2][0] < circles[0][0][0] < circles[0][1][0]:
                #     img_screw_list[4] = [int(i) for i in circles[0][0].tolist()]
                # else:
                #     img_screw_list[4] = [int(i) for i in circles[0][2].tolist()]

                # Reorient circle coordinates to original picture size
                for circle in range(0, len(img_screw_list)):
                    img_screw_list[circle][0] += img_crop_dict['ulx']
                    img_screw_list[circle][1] += img_crop_dict['uly']

                if img_screw_ret:
                    cv2.imwrite(
                        filename=img_screw_url,
                        img=img_screw,
                        params=[
                            int(cv2.IMWRITE_JPEG_QUALITY),
                            100
                        ]
                    )

                log = 'OpenCV located screws at {0} (left, right, upper, lower, pivot) with angle {1} degs.'. \
                    format(img_screw_list, img_screw_ang)
                logger.error(msg=log)
                print(log)

            else:
                img_screw_err = True
                log = 'OpenCV failed to determine screw locations for image {0}.'. \
                    format(img_screw_url)
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

        except Exception as exc:
            img_screw_err = True
            log = 'OpenCV failed to determine screw locations for image {0}.'. \
                format(img_screw_url)
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

    else:
        img_screw_err = True
        log = 'OS failed to locate image {0} to locate screws.'. \
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

    return img_screw_list, img_screw_err
