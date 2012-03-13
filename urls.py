from django.conf.urls.defaults import patterns, url

from gallery.views import UserGallery, UserOwnGallery, PhotoAddFormView, \
     PhotoEditFormView


urlpatterns = patterns('',
    # User views
    url(r'^usergallery/$', UserOwnGallery.as_view(),
        name='gallery-user'),
    url(r'^usergallery/(?P<username>\w+)/$',  # TODO: \w\d- and etc
        UserGallery.as_view(), name='gallery-user'),
    url(r'^add/$', PhotoAddFormView.as_view(),
        name='gallery-photo-add'),
    url(r'^edit/(?P<pk>\d+)/$', PhotoEditFormView.as_view(),
        name='gallery-photo-edit'),

    )
