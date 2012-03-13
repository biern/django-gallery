from django import forms

from gallery.models import Photo


class PhotoAddForm(forms.ModelForm):
    """
    Form for adding image to logged in user's gallery
    """

    class Meta:
        model = Photo
        fields = ('image', 'public')


class PhotoEditForm(forms.ModelForm):
    """
    Basic edit image form
    """

    class Meta:
        model = Photo
        fields = ('public', )

# TODO: Crop form + widgets
