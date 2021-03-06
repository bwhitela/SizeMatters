# Copyright (c) 2018 Brett Whitelaw
# All rights reserved.
# Unauthorized redistribution prohibited.

"""This script contains a basic WSGI compliant application to wrap SizeMatters.

This simple WSGI application will take in an image file and some parameters,
via a multipart POSTed form and return a JPEG from the SizeMatters tool, using
the provided parameters.

:Author: Brett Whitelaw (GitHub: bwhitela)
:Date: 2018/05/14
:Last Update: 2020/08/01
"""

import cgi
import io

import sizematters


FILE_PARAM = 'file'
COLOR_PARAM = 'color'
QUALITY_PARAM = 'quality'
DEFAULT_COLOR = 'white'
DEFUALT_QUALITY = '75'
AVAILABLE_COLOR_MAP = sizematters.AVAILABLE_COLOR_MAP


class FormError(Exception):
    pass


def sizematters_app(environ, start_response):
    """Simple WSGI application for the SizeMatters tool/function.

    A WSGI compliant application that only accepts POSTed multipart forms
    with `file`, `color`, and `quality`. The returned image will always be in
    JPEG format.

    :Form Parameters:
        - `file`: Should be a JPEG file (although others may work).
        - `color`: Should be any of the standard HTML color names (string).
            Default is 'white'.
        - `quality`: Should be an integer from 1 to 100 to indicate the quality
            setting for JPEG compression. Default is 75.

    :Errors:
        - 400: If the form parameters are bad or the Content-type is not
            multipart/form-data.
        - 405: If the request method is anything other than POST.
        - 500: If anything else raises an exception.
    """
    try:
        if environ['REQUEST_METHOD'] != 'POST':
            status = '405 Method Not Allowed'
            headers = [('Content-type', 'text/plain')]
            start_response(status, headers)
            return ['Only accepting POST requests!']

        if not environ['CONTENT_TYPE'].startswith('multipart/form-data'):
            status = '400 Bad Request'
            headers = [('Content-type', 'text/plain')]
            start_response(status, headers)
            return ['Only accepting multipart/form-data requests!']

        fs = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        color = fs.getfirst(COLOR_PARAM, DEFAULT_COLOR)
        if color not in AVAILABLE_COLOR_MAP:
            raise FormError

        quality = fs.getfirst(QUALITY_PARAM, DEFUALT_QUALITY)
        if quality and int(quality) >= 1 and int(quality) <= 100:
            quality = int(quality)
        else:
            raise FormError

        img_as_str = fs.getfirst(FILE_PARAM, None)
        if not img_as_str:
            raise FormError
        img_in_fh = io.BytesIO(img_as_str)

        img_out_fh = io.BytesIO()

        sizematters.maximize_image(img_in_fh, img_out_fh, color=color,
            quality=quality)
        img_in_fh.close()

        status = '201 Created'
        headers = [('Content-type', 'image/jpeg')]
        start_response(status, headers)
        img_out_fh.seek(0)
        return [img_out_fh.read()]

    except FormError as err:
        status = '400 Bad Request'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return ['Bad form!']
    except:
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return ['Something went wrong!']
