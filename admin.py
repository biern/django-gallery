from django.contrib import admin

from models import Photo


class PhotoAdmin(admin.ModelAdmin):
    """
    Very basic admin interface
    """

    fields = ('user', 'image', 'public')
    list_display = ('image', )

admin.site.register(Photo, PhotoAdmin)
