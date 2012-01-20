"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from qrz.models import QRZRecord
from qrz.views import CallsignLookupView

BAD_SESSION = '<QRZDatabase xmlns="http://www.qrz.com" version="1.18"><Session><Error>Invalid session key</Error><GMTime>Sat Sep 3 21:15:09 2011</GMTime><Remark>cpu:	0.190s</Remark></Session></QRZDatabase>'
GOOD_RECORD = '<?xml version="1.0" encoding="iso8859-1" ?> <QRZDatabase version="1.18" xmlns="http://www.qrz.com"> <Callsign> <call>KC2ZUF</call> <dxcc>291</dxcc> <name>A TEST RECORD</name> <fname>A Name</fname> <addr1>123 Fake St</addr1> <addr2>Fakeville</addr2> <state>NY</state> <zip>14043</zip> <country>United States</country> <lat>42.123456</lat> <lon>-78.987654</lon> <grid>FN02ld</grid> <county>Erie</county> <ccode>271</ccode> <fips>36029</fips> <land>United States</land> <efdate>2008-11-11</efdate> <expdate>2018-12-02</expdate> <trustee>KZ7AWP, FOO B QUUX</trustee> <class>C</class> <codes>HAB</codes> <email>fake@fake.com</email> <url>http://fake.fake.com</url> <u_views>4923</u_views> <bio>http://www.qrz.com/db/FAKEE</bio> <moddate>2011-02-18 17:31:07</moddate> <MSA>1280</MSA> <AreaCode>716</AreaCode> <eqsl>1</eqsl> <mqsl>1</mqsl> <TimeZone>Eastern</TimeZone> <GMTOffset>-5</GMTOffset> <DST>Y</DST> <cqzone>0</cqzone> <ituzone>0</ituzone> <locref>1</locref> <born>0000</born> <user>FA2KE</user> </Callsign> <Session> <Key>123456</Key> <Count>9</Count> <SubExp>Mon Sep 3 00:00:00 2012</SubExp> <GMTime>Sat Sep 3 20:03:52 2011</GMTime> <Remark>cpu:	0.077s </Remark> </Session> </QRZDatabase>'

class QRZViewTest(TestCase):

    def test_missing_callsign(self):
        view = CallsignLookupView()
        view.get_qrz_data = lambda x,y: None
        self.assertEquals('Missing callsign.', view.setup_context()['qrz'].error)

    def test_url_failure(self):
        view = CallsignLookupView()
        view.load_url = lambda x: None
        ctx = view.setup_context(callsign='KC2ZUF')
        self.assertFalse(ctx['qrz'].is_authenticated)
        self.assertEquals('Unable to connect to QRZ.com',ctx['qrz'].error)

    def test_bad_session(self):
        view = CallsignLookupView()
        view.get_qrz_data = lambda x,y: BAD_SESSION
        ctx = view.setup_context(callsign='KC2ZUF')
        self.assertFalse(ctx['qrz'].is_authenticated)
        self.assertFalse(ctx['qrz'].error)

    def test_good_lookup(self):
        view = CallsignLookupView()
        view.get_qrz_data = lambda x,y: GOOD_RECORD
        ctx = view.setup_context(callsign='KC2ZUF')
        self.assertTrue(ctx['qrz'].is_authenticated)
        self.assertFalse( ctx['qrz'].error)
        self.assertEquals('KC2ZUF', ctx['qrz'].call)

    def test_template_error(self):
        qrz = QRZRecord()
        qrz.error = 'Cannot foo.'
        self.assertEquals( u'<b>Error:</b> Cannot foo.\n',render_to_string('callsign_lookup.html',{'qrz': qrz}))

    def test_template_noauth(self):
        qrz = QRZRecord()
        qrz.is_authenticated = False
        qrz.error = None
        self.assertEquals(u'\n<p>You need to log into QRZ.com to use this feature.</p>\n\n',render_to_string('callsign_lookup.html',{'qrz': qrz}))      
  
    def test_template_with_us_record(self):
        qrz = QRZRecord()
        qrz.is_authenticated = True
        qrz.error = None
        qrz.country = 'United States'
        qrz.fname = 'Foo'
        qrz.name = 'Bar'
        qrz.state = 'MI'
        qrz.addr2 = 'Paris'
        qrz.zip = '12345'
        qrz.grid = 'AB01LD'
        qrz.license_class = 'E'
        qrz.will_qsl = True
        qrz.will_eqsl = True

        self.assertEquals( u'\n\n<p>Foo Bar<br/>\nParis, MI 12345<br/>\nExtra | AB01LD | Will QSL | Will eQSL<br/>\n<a href="http://qrz.com/db/?callsign=None" target="_qrz">View on QRZ.com</a>\n</p>\n\n\n',render_to_string('callsign_lookup.html',{'qrz': qrz}))

    def test_template_with_dx_record(self):
        qrz = QRZRecord()
        qrz.is_authenticated = True
        qrz.error = None
        qrz.country = 'France'
        qrz.fname = 'Foo'
        qrz.name = 'Bar'
        qrz.addr2 = 'Paris'
        qrz.grid = 'AB01LD'
        qrz.licence_class = None

        self.assertEquals( u'\n\n<p>Foo Bar<br/>\n\nParis, France\n<br/>\nOther | AB01LD <br/>\n<a href="http://qrz.com/db/?callsign=None" target="_qrz">View on QRZ.com</a>\n</p>\n\n\n',render_to_string('callsign_lookup.html',{'qrz': qrz}))

class QRZRecordTest(TestCase):
    def test_is_dx(self):
        qrz = QRZRecord()
        qrz.country = 'United States'
        self.assertFalse(qrz.is_dx())

        qrz.country = 'united states'
        self.assertFalse(qrz.is_dx())
    
        qrz.country = 'Canada'
        self.assertTrue(qrz.is_dx())

    def test_licence_class_expanded(self):
        qrz = QRZRecord()
        qrz.license_class = None
        self.assertEquals('Other', qrz.license_class_expanded())
        qrz.license_class = 'G'
        self.assertEquals('General', qrz.license_class_expanded())
        qrz.license_class = 'A'
        self.assertEquals('Advanced', qrz.license_class_expanded())
        qrz.license_class = 'N'
        self.assertEquals('Novice', qrz.license_class_expanded())
        qrz.license_class = 'T'
        self.assertEquals('Technician', qrz.license_class_expanded())
        qrz.license_class = 'E'
        self.assertEquals('Extra', qrz.license_class_expanded())

    def test_parse_error(self):
        qrz = QRZRecord(xml_data='asdfas')
        self.assertEquals(u'syntax error: line 1, column 0', qrz.error)

    def test_bad_session(self):
        qrz = QRZRecord(xml_data=BAD_SESSION)
        self.assertFalse(qrz.error)
        self.assertFalse(qrz.is_authenticated)

    def test_parse(self):
        qrz = QRZRecord(xml_data=GOOD_RECORD)

        self.assertFalse(qrz.error)
        self.assertTrue(qrz.is_authenticated)
        self.assertEquals('A TEST RECORD',qrz.name)
        self.assertEquals('KC2ZUF',qrz.call)
        self.assertEquals('A Name',qrz.fname)
        self.assertEquals('123 Fake St',qrz.addr1)
        self.assertEquals('Fakeville',qrz.addr2)
        self.assertEquals('NY',qrz.state)
        self.assertEquals('14043',qrz.zip)
        self.assertEquals('Erie',qrz.county)
        self.assertEquals('42.123456',qrz.lat)
        self.assertEquals('-78.987654',qrz.lon)
        self.assertEquals('FN02ld',qrz.grid)
        self.assertEquals('United States',qrz.country)
        self.assertEquals('C',qrz.license_class)
        self.assertEquals('1',qrz.will_qsl)
        self.assertEquals('1',qrz.will_eqsl)

class ViewSecurityTests(TestCase):
    def test_callsign_lookup(self):
        c = Client()
        response = c.get(reverse('callsign_lookup',kwargs={'callsign':'TESTING'}))
        self.assertEquals(200, response.status_code)

