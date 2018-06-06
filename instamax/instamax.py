#!/usr/bin/env python

# Copyright (c) 2018 Brett Whitelaw
# All rights reserved.
# Unauthorized redistribution prohibited.

"""InstaMax: Maximize an image to the resolution limits imposed by Instagram.

This script contains a single function to maximize an image based on
Instagram's maximum resolution limitations (although this script can be called
from the command line, too). It may be noteworthy that Instagram uses the same
image processing library (i.e. Pillow) in their backend to process the images
you post.

:Author: Brett Whitelaw (GitHub: bwhitela)
:Date: 2018/05/14
:Last Update: 2018/06/04
"""

import argparse

import PIL.ExifTags
import PIL.Image
import PIL.ImageColor


INSTA_MAX_WIDTH = 1080
INSTA_MAX_HEIGHT = 1350

AVAILABLE_COLOR_MAP = PIL.ImageColor.colormap


def maximize_image(input_file, output_file, color='white', quality=75):
    """Maximize an image to the resolution limits imposed by Instagram.

    Note that your image will not be cropped in any way. The new space created
    around your image will be whatever color you specify.

    Also note that every attempt has been made to keep metadata, etc. intact.
    Bicubic interpolation is being used to resize your image. JPEG image
    quality is set to a default of 75%. It is not recommended to go above 95%.
    Instagram probably uses around 50%.

    :Parameters:
        - `input_file`: File name (as a string) or a file object of the input
            image.
        - `output_file`: File name (as a string) or a file object for the output
            image (JPEG).
        - `color`: A standard HTML color to use as the background (as a string).
            Default is 'white'.
        - `quality`: The quality setting for JPEG compression as an integer
            percentage. Default is 75.

    :Returns:
        None. A file is written to `output_file`, however. It will be a JPEG
        format image.

    :Exceptions:
        None. The PIL library may throw some, depending on what you pass in.
    """
    img = PIL.Image.open(input_file)

    # Because orientation information is in the metadata, which will effect
    # how the image is processed, we'll check this, and change our working
    # reference point to match the orientation (i.e. if the image orientation
    # is +/- 90 degrees, we'll flip length and width information for our
    # working space).
    exif_data = img._getexif()
    # Determine numeric key in EXIF for 'Orientation'.
    orientation_key = None
    for exif_code, exif_string in PIL.ExifTags.TAGS.iteritems():
        if exif_string == 'Orientation':
            orientation_key = exif_code
            break
    # Look at the metadata to determine orientation.
    output_width = INSTA_MAX_WIDTH
    output_height = INSTA_MAX_HEIGHT
    if exif_data.get(orientation_key):
        if exif_data[orientation_key] in [5, 6, 7, 8]:
            # Rotated +/- 90 degrees. Might be mirrored but doesn't matter.
            output_width = INSTA_MAX_HEIGHT
            output_height = INSTA_MAX_WIDTH

    width, height = img.size
    # If the height is greater than the Instagram max ratio, sides will be
    # filled.
    if ((float(output_height) / float(output_width)) <
        (float(height) / float(width))):
        new_height = output_height
        scale_factor = float(new_height) / float(height)
        new_width = int(round(width * scale_factor))
    # If the width is greater than the Instagram max ratio, top and bottom will
    # be filled.
    else:
        new_width = output_width
        scale_factor = float(new_width) / float(width)
        new_height = int(round(height * scale_factor))
    # Now we know exactly how to scale it.
    scaled_img = img.resize((new_width, new_height), PIL.Image.BICUBIC)

    # Create the background.
    if color not in AVAILABLE_COLOR_MAP:
        color = 'white'
    background_img = PIL.Image.new(img.mode,
                                   (output_width, output_height),
                                   color)

    # Figure out how to center the image on the background.
    left = (output_width / 2) - (new_width / 2)
    right = left + new_width
    upper = (output_height / 2) - (new_height / 2)
    lower = upper + new_height
    background_img.paste(scaled_img, (left, upper, right, lower))
    final_img = background_img

    # Check the quality setting.
    if quality and int(quality) < 1:
        quality = 1
    elif quality and int(quality) > 100:
        quality = 100
    else:
        quality = int(quality)

    # Handle possible issues with alpha channels.
    temp_img = final_img.convert('RGBA')
    alpha_replace_img = PIL.Image.new('RGBA', temp_img.size, 'white')
    composite_img = PIL.Image.alpha_composite(alpha_replace_img, temp_img)
    final_img = composite_img.convert('RGB')

    # Finish.
    final_img.save(output_file, 'jpeg',
                   quality=quality,
                   icc_profile=img.info.get('icc_profile'),
                   exif=img.info.get('exif', ''))


def parse_cmd_line():
    """Parse the arguments from the command line.

    :Returns:
        All arguments as an parsed argument object.
    """
    description = 'InstaMax:\n' + \
                  'This script will take the input image and maximize it ' + \
                  'to fit the maximum dimensions that Instagram allows. ' + \
                  'Your picture will not be cropped, but the background ' + \
                  'will be filled with your choice of color.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('input_file',
                        help='Image file to process.')
    parser.add_argument('output_file',
                        help='File name (with any necessary path information) '
                             'where the output JPEG will be written.')
    parser.add_argument('-c', '--color', dest='color',
                        help='Common HTML color for background. (Default: '
                             'white)',
                        default='white')
    parser.add_argument('-q', '--quality', dest='quality', type=int,
                        help='Output JPEG image quality. (Default: 75)',
                        default=75)
    return parser.parse_args()


def main():
    args = parse_cmd_line()
    with open(args.output_file, 'wb') as out_fh:
        with open(args.input_file, 'rb') as in_fh:
            maximize_image(in_fh, out_fh, args.color, args.quality)


if __name__ == "__main__":
    main()
