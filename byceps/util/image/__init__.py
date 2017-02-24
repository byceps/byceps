"""
byceps.util.image
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from io import BytesIO

from PIL import Image

from .models import Dimensions


def read_dimensions(filename_or_stream):
    """Return the dimensions of the image."""
    image = Image.open(filename_or_stream)
    return Dimensions(*image.size)


def create_thumbnail(filename_or_stream, image_type, maximum_dimensions):
    """Create a thumbnail from the given image and return the result stream."""
    output_stream = BytesIO()

    image = Image.open(filename_or_stream)

    dimensions = Dimensions(*image.size)

    if not dimensions.is_square:
        edge_length = min(*dimensions)
        crop_box = (0, 0, edge_length, edge_length)
        image = image.crop(crop_box)

    image.thumbnail(maximum_dimensions, resample=Image.ANTIALIAS)

    image.save(output_stream, format=image_type)

    output_stream.seek(0)
    return output_stream
