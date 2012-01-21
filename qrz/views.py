import urllib2
import re

from django.conf import settings

from django.shortcuts import render_to_response
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.core.cache import cache

from qrz.models import QRZRecord

class CallsignLookupView(View):
    def __init__(self,*args,**kwargs):
	super(CallsignLookupView, self).__init__(*args,**kwargs)
        self.qrz_agent='MooseLoggerV0.1'
        self.qrz_url='http://www.qrz.com/xml'        

    def get_qrz_data(self, callsign,sid):
        key = 'qrz-%s:%s' % (callsign, sid)
        data = cache.get(key)
        if not data:
            data = self.load_url('%s?s=%s;callsign=%s' % (self.qrz_url, sid,callsign))
            cache.set(key, data)

        return data

    def login(self, username,password):
        print '>>>',username,password
	data = self.load_url('%s?username=%s;password=%s;agent=%s' % (self.qrz_url,username,password,self.qrz_agent))
	print ':::: ',data
	rx = re.compile('<Key>([^<]*)</Key>')
	m = rx.search(data)
	if m:
	    return m.group(1)
 
        return None		

# @todo add timeout
    def load_url(self, url):
        usock = urllib2.urlopen(url)
        data = usock.read()
        usock.close()

        return data

    def setup_context(self, session, **kwargs):
        context = {'error': None,
                   'qrz': None}
        
        session_id = session.get('qrz_session_id')
        if not session_id:
	    username,password = session.get('qrz_info')
	    session_id = self.login(username,password)
            session['qrz_session_id'] = session_id
	    
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
                data = self.get_qrz_data(callsign,session_id)
            
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
                                  self.setup_context(request.session,**kwargs),
                                  RequestContext(request))


