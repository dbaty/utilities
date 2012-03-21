#!/usr/bin/env python
"""``imresize`` is an utility which resizes and/or converts a set of
images.

Run with "--help" for the syntax.

No PEP8, no argparse, etc. This is an old script. ;)

Published under the 3-clause BSD license, a copy of which is included
below.

--- 8< ---
Copyright (c) Damien Baty
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.
    * Neither the name of Poulda nor the names of its contributors may
      be used to endorse or promote products derived from this
      software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DAMIEN BATY BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--- 8< ---
"""

import os
import os.path
import sys
import time
import getopt
import logging

from PIL import Image, ImageFile


## See http://mail.python.org/pipermail/image-sig/1999-August/000816.html
ImageFile.MAXBLOCK = 1000000

## Load drivers so that we can list available image formats
Image.init()

IMAGE_EXTENSIONS = ('jpg', 'gif', 'png')
DEFAULT_OUTPUT_DIRECTORY = 'resized'
DEFAULT_QUALITY = 95

USAGE = """Standard usage: %s [-h,--help]
                            [-s <width>,<height>] 
                            [-o <output-dir>]
                            [-a <suffix>]
                            [-f <image-format>]
                            [-q <quality>]
                            <file1> [<file2>...<fileN>]

This program resizes and/or converts all images found amongst the
given files. Generated files are created in a specific directory, but
you may arrange so that the original files are overwritten. Original
and generated images have the same basename, unless you have specified
a different file format.

-h, --help

  print this message.

-s <width>,<height>

  size of generated images. If <width> or <height> is omitted, the
  program proportionnaly computes the missing value from the given
  one. However, you must provide at least one of these values.

  Default: [image is not resized]

-o <output-dir>

  the directory where images are created.

  Default: %s

-a <suffix>

  suffix to append to the filename (just before the extension). Be
  sure to quote the suffix so that it is not parsed as an option.

  Example: '-a "-small"' would generate files named '1-small.jpg',
  '2.new-small.jpg', etc.

  Default: [no suffix]

-f <image-format>

  format of the generatd images. The following formats are available: %s

  Default: [same as the original image]

-q <quality>

  quality of generated JPEG files, on a scale from 1 (worst) to 95
  (best). Values above 95 should be avoided; 100 completely disables
  the JPEG quantization stage (from PIL documentation).

  Default: %s""" % \
    (sys.argv[0], DEFAULT_OUTPUT_DIRECTORY,
     ', '.join(sorted(Image.SAVE.keys())), DEFAULT_QUALITY)

LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
LOGGING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def usage():
    print USAGE


def processFile(infile, outfile, suffix,
                width, height,
                image_format,
                quality):
    """Resize and/or convert ``infile``.

    If ``suffix`` is given, is is appended to ``outfile``, just before
    the extension.

    If ``width`` or ``height`` is omitted, the missing value is
    computed from the given one so that proportions are kept.

    ``image_format`` is the format of the generated thumbnail
    (``JPEG``, ``PNG``, see PIL documentation). If ``None``, we use
    the format of the original image.
    """
    try:
        image = Image.open(infile)
    except IOError, exc:
        logging.error('Could not open "%s": Got: %s', infile, exc)
        return 0

    if image_format is None:
        image_format = image.format

    ## Change ``outfile`` basename if asked
    if suffix:
        base, ext = outfile.rsplit('.', 1)
        outfile = ''.join((base, suffix, '.', ext))
    if image_format != image.format:
        outfile = ''.join((outfile.rsplit('.', 1)[0],
                           '.',
                           image_format.lower()))

    ## Resize if asked
    if width or height:
        if not width:
            width = image.size[0] * height / float(image.size[1])
            width = int(round(width))
        elif not height:
            height = image.size[1] * width / float(image.size[0])
            height = int(round(height))
        size = (width, height)
        new = image.resize(size, Image.ANTIALIAS)
        del image ## This let us overwrite the image if wanted.
        image = new
    else:
        size = image.size

    ## Finally, save file
    try:
        image.save(outfile, image_format, quality=quality, optimize=True)
    except IOError, exc:
        logging.error('Could not save "%s": Got: %s', outfile, exc)
        return 0

    logging.info('Created "%s" (size: %d,%d).', outfile, size[0], size[1])
    return 1


def main():
    """Main function."""
    try:
        options, args = getopt.getopt(sys.argv[1:],
                                      'ho:s:f:a:q:',
                                      ['help'])
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    if not args:
        usage()
        sys.exit(1)

    output_dir = DEFAULT_OUTPUT_DIRECTORY
    suffix = None
    width, height = None, None
    image_format = None
    quality = DEFAULT_QUALITY
    for option, value in options:
        if option == '-o':
            output_dir = value
        elif option == '-a':
            suffix = value
        elif option == '-s':
            width, height = value.split(',')
            if width: width = int(width)
            if height: height = int(height)
        elif option == '-f':
            image_format = value
        elif option == '-q':
            quality = int(value)
        elif option in ('-h', '--help'):
            usage()
            sys.exit(0)

    logging.basicConfig(level=LOGGING_LEVEL,
                        format=LOGGING_FORMAT,
                        datefmt=LOGGING_DATE_FORMAT)

    if os.path.exists(output_dir):
        if not os.path.isdir(output_dir):
            logging.error('Error: "%s" is not a directory.',
                          output_dir)
            sys.exit(1)
    else:
        os.mkdir(output_dir)

    generated = 0
    errors = 0
    start_time = time.time()
    for filename in args:
        outfile = filename.split(os.sep)[-1]
        outfile = os.path.join(output_dir, outfile)
        if processFile(filename, outfile, suffix,
                       width, height, image_format, quality):
            generated += 1
        else:
            errors += 1

    elapsed = time.time() - start_time
    logging.info('Generated %d images in %.2fs.', generated, elapsed)
    if errors:
        logging.info('WARNING: there were %d errors.', errors)


if __name__ == "__main__":
    main()
