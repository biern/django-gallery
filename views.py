# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView

from gallery.models import Photo
from gallery.forms import PhotoAddForm, PhotoEditForm
from gallery import utils


class UserGalleryBase(ListView):
    context_object_name = 'photo_list'


class UserOwnGallery(UserGalleryBase):
    """
    Shows currently logged in user his/her gallery.
    Private photos are shown as well.
    """

    template_name = 'gallery/user_own_gallery.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserOwnGallery, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Photo.objects.filter(user=self.request.user)


class UserGallery(UserGalleryBase):
    """
    Shows user's public gallery
    """

    template_name = 'gallery/user_gallery.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Photo.objects.filter(user=user, public=True)


class PhotoAddFormView(CreateView):
    """
    Shows form for adding new photo
    """

    form_class = PhotoAddForm
    model = Photo

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return redirect('gallery-user')


class CropImageMixin(object):
    """
    Provieds cropping methods.
    """

    def is_crop(self, request):
        """
        Return True if request seems to be crop request.
        """

        return request.POST.get('crop') and request.POST.get('coords')

    def crop_photo(self, photo):
        """
        Crops photo according to data stored in POST (uses 'coords' key)
        """

        img = utils.cropped_django_image(
            photo.image, map(int, self.request.POST.get('coords').split(',')))
        photo.image = img
        photo.save()


class PhotoEditFormView(CropImageMixin, UpdateView):
    """
    Provieds basic photo editing options, also handles crop requests.
    On successful edit returns to gallery view.
    """

    form_class = PhotoEditForm
    context_object_name = 'photo'
    template_name = 'gallery/photo_form_edit.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.kwargs = kwargs
        self.object = obj = self.get_object()
        if self.is_crop(request):
            self.crop_photo(obj)
            return redirect('gallery-photo-edit', obj.id)

        return super(PhotoEditFormView, self).\
          dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filter by logged in user
        """

        return Photo.objects.filter(
            user=self.request.user)

    def get_success_url(self):
        """
        Return to gallery on success
        """

        return reverse('gallery-user')
