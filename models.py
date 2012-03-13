# -*- coding: utf-8 -*-
"""
django-gallery provides default :class:`Photo` model.
"""
import pyexiv2
import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from thumbs import ImageWithThumbsField


THUMBNAIL_SIZES = ((100, 100),)
"""
Sizes of thumbs to generate when uploading an image
"""


def upload_to(instance, filename):
    """
    Creates separate directory for every user's gallery
    """
    return "{}/{}".format(
        instance.user, filename)


class Photo(models.Model):
    """
    Represents user added image.

    Reads and saves image exif data if available (accessed with attrs
    :attr:`exif_available`, :attr:`exif_data`) and creates thumbnails
    according to `THUMBNAIL_SIZES`
    """

    user = models.ForeignKey(User)
    date = models.DateField('Czas dodania', auto_now_add=True)
    width = models.IntegerField('Szerokość')
    height = models.IntegerField('Wysokość')
    image = ImageWithThumbsField(
        'Obraz', upload_to=upload_to,
        height_field='height', width_field='width',
        sizes=THUMBNAIL_SIZES)
    public = models.BooleanField('Publiczny', default=False)

    exif_available = models.BooleanField('exif dostępny', default=False)
    exif_data = models.TextField('informacje exif', blank=True, default="")

    class Meta:
        ordering = ['date']

    def save(self, *args, **kwargs):
        # 2x save, pewnie da się zrobić to lepiej, ale czasu brak :-(
        res = super(Photo, self).save(*args, **kwargs)
        self.update_exif(self.image)
        super(Photo, self).save(*args, **kwargs)
        return res

    # TODO: Może kiedyś
    # @models.permalink
    # def get_absolute_url(self):
    #     return ('gallery-photo', [self.id])

    def update_exif(self, image):
        """
        Update model exif data based on image.

        """
        path = os.path.join(settings.MEDIA_ROOT, str(image))
        data = pyexiv2.metadata.ImageMetadata(path)
        data.read()
        self.exif_data = ""
        for k in data.exif_keys:
            self.exif_data += "{}: {}".format(k, data[k])

        if self.exif_data:
            self.exif_available = True
