from django.conf.urls.defaults import patterns, include, url

from qrz.views import CallsignLookupView

urlpatterns = patterns('',
    # Examples:
    url(r'^lookup/(?P<callsign>.+)/$', CallsignLookupView.as_view(), name='callsign_lookup'),
)
