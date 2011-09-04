import urllib2

from django.shortcuts import render_to_response
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.core.cache import cache

from qrz.models import QRZRecord

class CallsignLookupView(View):
    def get_qrz_data(self, callsign,sid):
        key = 'qrz-%s:%s' % (callsign, sid)
        data = cache.get(key)
        if not data:
            data = self.load_url('http://www.qrz.com/xml?s=%s;callsign=%s' % (sid,callsign))
            cache.set(key, data)

        return data

#    @todo add timeout
    def load_url(self, url):
        usock = urllib2.urlopen(url)
        data = usock.read()
        usock.close()

        return data

    def dispatch(self, request, *args, **kwargs):
        context = {'error': None,
                   'qrz': None}
        
        callsign = kwargs.get('callsign')

        qrz = QRZRecord(xml_data=self.get_qrz_data(callsign,'a025a6fd800361a6db7146e94728943c'))
        if qrz.error:
            context['error'] = qrz.error
        else:
            context['qrz'] = qrz

        return render_to_response('callsign_lookup.html',
                                  context,
                                  RequestContext(request))


