import urllib2

from django.conf import settings

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

    def setup_context(self, **kwargs):
        context = {'error': None,
                   'qrz': None}
        
        callsign = kwargs.get('callsign')

        if not callsign:
            qrz= QRZRecord()
            qrz.error = 'Missing callsign.'
        else:
            if callsign == 'TESTING' and settings.DEBUG:
                # Some kind of dependency injection would probably work better here, but this is 
                # the expedient way to do things
                data = 'asdfa'
            else:
                data = self.get_qrz_data(callsign,'a025a6fd800361a6db7146e94728943c')
            
            if data:
                qrz = QRZRecord(xml_data=data)
            else:
                qrz = QRZRecord()
                qrz.is_authenticated = False
                qrz.error = 'Unable to connect to QRZ.com'
        
        context['qrz'] = qrz

        return context

    def dispatch(self, request, *args, **kwargs):
        return render_to_response('callsign_lookup.html',
                                  self.setup_context(**kwargs),
                                  RequestContext(request))


