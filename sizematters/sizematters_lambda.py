# Copyright (c) 2022 Brett Whitelaw
# All rights reserved.
# Unauthorized redistribution prohibited.

"""This script contains an AWS Lambda handler function to wrap SizeMatters.

This simple http-triggered AWS Lambda handler function will take in an image
file and some parameters, via a multipart POSTed form and return a JPEG from
the SizeMatters tool, using the provided parameters.

:Author: Brett Whitelaw (GitHub: bwhitela)
:Date: 2022/03/14
:Last Update: 2022/03/14
"""

import base64
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


def sizematters_lambda(event, context):
    """Simple AWS Lambda handler function for the SizeMatters tool/function.

    An http-triggered AWS Lambda handler function that only accepts POSTed
    multipart forms with `file`, `color`, and `quality`. The returned image
    will always be in JPEG format.

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
        if event['httpMethod'] != 'POST':
            resp = {
                'statusCode': 405,
                'headers': {'Content-type': 'text/plain'},
                'body': 'Only accepting POST requests!'
            }
            return resp

        if not event['headers']['content-type'].startswith('multipart/form-data'):
            resp = {
                'statusCode': 400,
                'headers': {'Content-type': 'text/plain'},
                'body': 'Only accepting multipart/form-data requests!'
            }
            return resp

        body = io.BytesIO(base64.b64decode(event['body']))
        fs = cgi.FieldStorage(
            fp=body,
            headers=event['headers'],
            environ={
                'REQUEST_METHOD':'POST',
                'CONTENT_TYPE':event['headers']['content-type']
            }
        )

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

        img_out_fh.seek(0)
        resp = {
            'isBase64Encoded': True,
            'statusCode': 201,
            'headers': {'content-type': 'image/jpeg'},
            'body': base64.b64encode(img_out_fh.read()).decode('utf-8'),
        }
        return resp

    except FormError as err:
        resp = {
            'statusCode': 400,
            'headers': {'Content-type': 'text/plain'},
            'body': 'Bad form!'
        }
        return resp
    except:
        resp = {
            'statusCode': 500,
            'headers': {'Content-type': 'text/plain'},
            'body': 'Something went wrong!'
        }
        return resp
