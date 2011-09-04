import urllib2

from django.shortcuts import render_to_response
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from qrz.models import QRZRecord

class CallsignLookupView(View):
    def load_url(self, url):
        return """<?xml version="1.0" encoding="iso8859-1" ?> <QRZDatabase version="1.18" xmlns="http://www.qrz.com"> <Callsign> <call>W6TWT</call> <dxcc>291</dxcc> <fname>Leo G</fname> <name>Laporte</name> <addr1>PO BOX 1018</addr1> <addr2>Petaluma</addr2> <state>CA</state> <zip>94953</zip> <country>United States</country> <lat>38.261520</lat> <lon>-122.639077</lon> <grid>CM88qg</grid> <county>Sonoma</county> <ccode>271</ccode> <fips>06097</fips> <land>United States</land> <efdate>2011-08-25</efdate> <expdate>2021-08-09</expdate> <p_call>KJ6QGP</p_call> <class>G</class> <codes>HVIE</codes> <email>leo@w6twt.org</email> <url>http://w6twt.org</url> <u_views>2461</u_views> <bio>http://www.qrz.com/db/W6TWT</bio> <image>http://files.qrz.com/t/w6twt/6053489932_ea6d3cf828_m.jpeg</image> <moddate>2011-08-26 16:03:47</moddate> <MSA>7500</MSA> <AreaCode>707</AreaCode> <TimeZone>Pacific</TimeZone> <GMTOffset>-8</GMTOffset> <DST>Y</DST> <eqsl>1</eqsl> <mqsl>1</mqsl> <cqzone>0</cqzone> <ituzone>0</ituzone> <locref>2</locref> <born>1956</born> <lotw>1</lotw> <user>W6TWT</user> </Callsign> <Session> <Key>96830e1178bdd2b44c2fc913d1ab579c</Key> <Count>10</Count> <SubExp>Mon Sep 3 00:00:00 2012</SubExp> <GMTime>Sat Sep 3 20:18:38 2011</GMTime> <Remark>cpu:	0.053s </Remark> </Session> </QRZDatabase>"""

    def xload_url(self, url):
        usock = urllib2.urlopen(url)
        data = usock.read()
        usock.close()

        return data

    def dispatch(self, request, *args, **kwargs):
        context = {'error': None,
                   'qrz': None}
        
        callsign = kwargs.get('callsign')

        url = 'http://www.qrz.com/xml?s=96830e1178bdd2b44c2fc913d1ab579c;callsign=%s' % callsign

        qrz = QRZRecord(xml_data=self.load_url(url))
        if qrz.error:
            context['error'] = qrz.error
        else:
            context['qrz'] = qrz

        return render_to_response('callsign_lookup.html',
                                  context,
                                  RequestContext(request))


