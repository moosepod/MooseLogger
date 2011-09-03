from django.conf.urls.defaults import patterns, include, url

from qso.views import HomeView,ContactLogView

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^log/(?P<pk>\d+)/$', ContactLogView.as_view(), name='contact_log'),
)
