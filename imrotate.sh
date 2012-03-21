#!/bin/bash

# An utility that rotates image 90 degrees anti-clockwise.
#
# If you have such an image::
#
#     +-----+
#     | >+o |
#     +-----+
#
# ... it will generate another image like this::
#
#     +---+
#     | o |
#     | + |
#     | ^ |
#     +---+
#
# Naturally, width/height ratio will be conserved (though inversed, of
# course). EXIF metadata is also kept.
#
# The same operation could be done by other scripts/programs or by
# using the "Image Orientation" EXIF tag. However, our current camera
# (Sony DSC-H5) does not have any orientation sensor (and therefore
# always set this tag to "Horizontal") so I could not use tag.

mkdir -p rotated
echo 'Created "rotated/"'
for src in $*
do
    out="rotated/`basename $src`"
    jpegtran -rotate 270 -copy all "$src" > "$out"
    echo 'Created' $out
done