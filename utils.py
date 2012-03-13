import Image as pil
import StringIO

from django.core.files.uploadedfile import InMemoryUploadedFile


def cropped_django_image(image, area):
    """
    Crops image to area using pil. Returns image object that can be directly
    assigned to ImageField

    :param: image ImageField to crop
    :area: tuple (x, y, w, h)
    """

    area = (area[0], area[1], area[0] + area[2], area[1] + area[3])
    img = pil.open(image).crop(area)
    img_io = StringIO.StringIO()
    img.save(img_io, format='JPEG')
    img_file = InMemoryUploadedFile(img_io, None, str(image), 'image/jpeg',
                                    img_io.len, None)

    return img_file
