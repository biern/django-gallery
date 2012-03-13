# -*- coding: utf-8 -*-
"""
Provieds basic tests
"""

import os

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from gallery.models import Photo
from gallery.forms import PhotoEditForm, PhotoAddForm


PATH_MANA = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         'test_images/mana_energy_potion_sixpack_package.jpg')
PATH_GRODEK = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'test_images/grodek.jpg')


class GalleryTestCase(TestCase):
    urls = 'gallery.urls'
    # Fixtures tak łatwo nie przejdą, obrazy wszukiwane są w site_media,
    # które w apce trudno jest t
    # fixtures = ['images.yaml']

    def login_user(self):
        self.client.login(username='admin', password='admin')

    def setUp(self):
        # Typowy użytkownik, nick admin nic nie znaczy
        self.admin = User.objects.create_user(
            username='admin', password='admin', email='admin@admin.admin')
        # Tworzenie zdjęć ręcznie zamiast używania fixtures - muszę zostać
        # zuploadowane do odpowiedniego katalogu
        self.photo_mana = Photo(user=self.admin,
                                image=ImageFile(open(PATH_MANA, 'rb')),
                                public=False)
        self.photo_mana.save()
        self.photo_grodek = Photo(user=self.admin,
                                  image=ImageFile(open(PATH_GRODEK, 'rb')),
                                  public=True)
        self.photo_grodek.save()


class TestPhoto(GalleryTestCase):
    fixtures = []

    def test_sanity(self):
        """
        Creating a simple photo without exif.
        """
        photo = Photo(user=self.admin,
                      image=ImageFile(open(PATH_MANA, 'rb')),
                      public=True)
        photo.save()
        self.assertFalse(photo.exif_available)

    def test_invalid(self):
        """
        Creating invalid Photo raises integrity error
        """

        def invalid():
            photo = Photo(user=self.admin,
                          image=None,
                          public=True)
            photo.save()

        self.assertRaises(IntegrityError, invalid)

    def test_exif(self):
        photo = Photo(user=self.admin,
                      image=ImageFile(open(PATH_GRODEK, 'rb')),
                      public=True)
        photo.save()
        self.assertTrue(photo.exif_available)


class TestFormViews(GalleryTestCase):
    def test_form(self):
        """
        Test add form
        """

        upload_file = open(PATH_GRODEK, 'rb')
        post_dict = {'public': 'false'}
        file_dict = {'image':
                     SimpleUploadedFile(upload_file.name, upload_file.read())}
        form = PhotoAddForm(post_dict, file_dict)
        self.assertTrue(form.is_valid())

    def test_form_crop(self):
        """
        Test cropping image with provided form
        """

        photo_id = 1

        post_dict = {'crop': 'true', 'coords': '100,100,150,150' }
        self.login_user()
        self.client.post(reverse('gallery-photo-edit',
                                  args=[photo_id]), post_dict)
        photo = Photo.objects.get(id=photo_id)
        self.assertEqual(photo.width, 50)
        self.assertEqual(photo.height, 50)


class TestGalleryViews(GalleryTestCase):

    def test_user_own_gallery(self):
        """
        Check if all photos (public + private) are shown in my gallery
        """

        self.login_user()
        resp = self.client.get(reverse('gallery-user'))
        self.assertEqual(resp.status_code, 200)
        # Check if all (public and private) images are shown
        self.assertEqual(len(resp.context['photo_list']), 2)

    def test_user_gallery(self):
        """
        Check if only public photos are shown in other user's gallery
        """

        resp = self.client.get(
            reverse('gallery-user', kwargs={'username': 'admin' }))
        self.assertEqual(resp.status_code, 200)
        # Check if only public images are shown
        self.assertEqual(len(resp.context['photo_list']), 1)
