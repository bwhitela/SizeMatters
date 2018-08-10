SizeMatters (formerly InstaMax)
===============================

Maximize Image Size for Instagram
---------------------------------

Have you ever wanted to post a portrait-orientation picture to Instagram, but
when you go to do so, Instagram forces you to crop it because it is "too tall"
for Instagram? For those of us that don't want to crop our image, we usually
go and grab an "app" that fits the whole picture into a square and fills in the
new space with a background color. This is really silly because we could be
getting more pixels for our pictures! Instagram allows a maximum image size of
1080 pixels wide by 1350 pixels tall. This tool gives you the maximum number of
pixels allowed by Instagram for your picture.

Requirements
------------

The only requirement of this tool is the Pillow image processing library,
which can be found in PyPI. I have included a ``requirements.txt`` file
if you use ``pip`` and a ``setup.py`` file, as well. This tool has only been
run with Python 2.7, but I have no reason to believe it won't work with most
versions.

``instamax.py``
---------------

This script contains a single function to maximize an image based on Instagram's
maximum size limitations (although this script can be called from the command
line, too). It may be noteworthy that Instagram uses the same image processing
library (i.e. Pillow) in their backend to process the images you post.

If you want to import the tool for use with your Python code, here is the
docstring for the primary ``maximize_image`` function::

    Maximize an image to the resolution limits imposed by Instagram.

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

If you just want to run this as a script from the command line, here's the
usage::

    usage: instamax.py [-h] [-c COLOR] [-q QUALITY] input_file output_file

    InstaMax: This script will take the input image and maximize it to fit the
    maximum dimensions that Instagram allows. Your picture will not be cropped,
    but the background will be filled with your choice of color.

    positional arguments:
      input_file            Image file to process.
      output_file           File name (with any necessary path information) where
                            the output JPEG will be written.

    optional arguments:
      -h, --help            show this help message and exit
      -c COLOR, --color COLOR
                            Common HTML color for background. (Default: white)
      -q QUALITY, --quality QUALITY
                            Output JPEG image quality. (Default: 75)

``instamax_wsgi.py``
--------------------

This script contains a very simple WSGI-compliant web app to wrap the InstaMax
tool. It contains a single function, ``instamax_app``, which serves as the
WSGI-compliant app. Here is the docstring that defines how it is used::

    Simple WSGI application for the InstaMax tool/function.

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

Because this is a WSGI-compliant web app, you can use it with your favorite
wrapper, whether that is the reference one provided by Python, or something like
uWSGI (which is what I use).

``instamax.html``
-----------------

I have also provided a very basic/stripped-down HTML file that contains a proper
form to send requests to the InstaMax web app. If you make use of this, you'll
likely need to tweak it to meet your needs.
