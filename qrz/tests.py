"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from qrz.models import QRZRecord

class QRZViewTest(TestCase):
    def test_missing_callsign(self):
        self.fail()

    def test_url_failure(self):
        self.fail()

    def test_bad_session(self):
        self.fail()

    def test_good_lookup(self):
        self.fail()

    def test_template_error(self):
        self.fail()

    def test_template_noauth(self):
        self.fail()

    def test_template_with_us_record(self):
        self.fail()

    def test_template_with_dx_record(self):
        self.fail()

class QRZRecordTest(TestCase):
    def test_is_dx(self):
        self.fail()
    
    def test_licence_class_expanded(self):
        self.fail()

    def test_parse_error(self):
        qrz = QRZRecord(xml_data='asdfas')
        self.assertEquals(u'syntax error: line 1, column 0', qrz.error)

    def test_bad_session(self):
        qrz = QRZRecord(xml_data='<QRZDatabase xmlns="http://www.qrz.com" version="1.18"><Session><Error>Invalid session key</Error><GMTime>Sat Sep 3 21:15:09 2011</GMTime><Remark>cpu:	0.190s</Remark></Session></QRZDatabase>')
        self.assertFalse(qrz.error)
        self.assertFalse(qrz.is_authenticated)

    def test_parse(self):
        qrz = QRZRecord(xml_data='<?xml version="1.0" encoding="iso8859-1" ?> <QRZDatabase version="1.18" xmlns="http://www.qrz.com"> <Callsign> <call>KC2ZUF</call> <dxcc>291</dxcc> <name>A TEST RECORD</name> <fname>A Name</fname> <addr1>123 Fake St</addr1> <addr2>Fakeville</addr2> <state>NY</state> <zip>14043</zip> <country>United States</country> <lat>42.123456</lat> <lon>-78.987654</lon> <grid>FN02ld</grid> <county>Erie</county> <ccode>271</ccode> <fips>36029</fips> <land>United States</land> <efdate>2008-11-11</efdate> <expdate>2018-12-02</expdate> <trustee>KZ7AWP, FOO B QUUX</trustee> <class>C</class> <codes>HAB</codes> <email>fake@fake.com</email> <url>http://fake.fake.com</url> <u_views>4923</u_views> <bio>http://www.qrz.com/db/FAKEE</bio> <moddate>2011-02-18 17:31:07</moddate> <MSA>1280</MSA> <AreaCode>716</AreaCode> <eqsl>1</eqsl> <mqsl>1</mqsl> <TimeZone>Eastern</TimeZone> <GMTOffset>-5</GMTOffset> <DST>Y</DST> <cqzone>0</cqzone> <ituzone>0</ituzone> <locref>1</locref> <born>0000</born> <user>FA2KE</user> </Callsign> <Session> <Key>123456</Key> <Count>9</Count> <SubExp>Mon Sep 3 00:00:00 2012</SubExp> <GMTime>Sat Sep 3 20:03:52 2011</GMTime> <Remark>cpu:	0.077s </Remark> </Session> </QRZDatabase>')

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
