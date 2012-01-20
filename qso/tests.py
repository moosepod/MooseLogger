"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import datetime

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError


from qso.models import Ruleset, ContactLog, Operator, Band, Mode, Contact, QRZCredentials
from qso.forms import ContactForm
from qso import views

class MockForm(object):
    def as_p(self):
        return 'this is the form'

    def when(self):
        return 'this is the field when'

def make_operator():
    return Operator.objects.create(callsign='KC2ZUF')

def make_ruleset():
    return Ruleset.objects.create(name='QSO Party')

def make_contactlog(owner=None, ruleset=None):
    return ContactLog.objects.create(name='Flarp',
                                     owner=owner or make_operator(),
                                     ruleset=ruleset or make_ruleset())

def make_contact(contact_log=None):
    return Contact.objects.create(when=datetime.datetime(2011,1,2,1,2,3), 
                                     callsign='W2PE',
                                     mode=Mode.objects.get(name='SSB'),
                                     band=Band.objects.get(name='20m'),
                                     contact_log=contact_log or make_contactlog(),
                                     operator=make_operator())

class BandTest(TestCase):
    def test_unicode(self):
        b = Band(name='21m',band_bottom=7.0, band_top=8.0)
        self.assertEquals('21m', unicode(b))

    def test_save(self):
        Band.objects.create(name='21m',band_bottom=7.0, band_top=8.0)

        try:
            Band.objects.create(name='21m',band_bottom=7.0, band_top=8.0)
            self.fail('Should have thrown unique violation exception')
        except ValidationError:
            pass

    def test_save_range(self):
        try:
            Band.objects.create(name='20m',band_bottom=8.0, band_top=7.0)
            self.fail('Should have thrown validation error')
        except ValidationError:
            pass

    def test_band_for_frequency(self):
        self.assertEquals('160m',Band.objects.get_band_for_frequency(1.9).name)
        self.assertEquals('80m',Band.objects.get_band_for_frequency(3.7).name)
        self.assertEquals('60m',Band.objects.get_band_for_frequency(5.366).name)
        self.assertEquals('40m',Band.objects.get_band_for_frequency(7.25).name)
        self.assertEquals('30m',Band.objects.get_band_for_frequency(10.110).name)
        self.assertEquals('20m',Band.objects.get_band_for_frequency(14.125).name)
        self.assertEquals('17m',Band.objects.get_band_for_frequency(18.111).name)
        self.assertEquals('15m',Band.objects.get_band_for_frequency(21.205).name)
        self.assertEquals('12m',Band.objects.get_band_for_frequency(24.933).name)
        self.assertEquals('10m',Band.objects.get_band_for_frequency(28.488).name)
        self.assertEquals('6m',Band.objects.get_band_for_frequency(50.223).name)
        self.assertEquals('2m',Band.objects.get_band_for_frequency(146.0).name)
        self.assertEquals('1.25m',Band.objects.get_band_for_frequency(222.5).name)
        self.assertEquals('70cm',Band.objects.get_band_for_frequency(444.0).name)
        self.assertEquals('33cm',Band.objects.get_band_for_frequency(918.1).name)
        self.assertEquals('23cm',Band.objects.get_band_for_frequency(1240.0).name)
        self.assertFalse(Band.objects.get_band_for_frequency(60))

class ModeTest(TestCase):
    def test_unicode(self):
        m = Mode(name='SSB')
        self.assertEquals('SSB',unicode(m))

    def test_save(self):
        Mode.objects.create(name='SSB Test')

        try:
            Mode.objects.create(name='SSB Test')
            self.fail('Should have thrown unique violation exception')
        except IntegrityError:
            pass

class OperatorTests(TestCase):
    def test_unicode(self):
        o = Operator(callsign='KC2ZUF')
        self.assertEquals('KC2ZUF', unicode(o))

    def test_save(self):
        Operator.objects.create(callsign='KC2ZUF')

        # You can have multiple operators with the same callsign, in theory, since they get reused
        Operator.objects.create(callsign='KC2ZUF')

        Operator.objects.create(callsign='AA7AAA/AE')

class QRZCredentialsTests(TestCase):
    def test_unicode(self):
	qrz = QRZCredentials(username='KA9AAA')
	self.assertEquals('KA9AAA',unicode(qrz))

    def test_save(self):
	c = Operator.objects.create(callsign='KC2ZUF')
        qrz = QRZCredentials(username='KA9AAA',operator=c,password='test')
	qrz.save()

class RulesetTests(TestCase):
    def test_unicode(self):
        r = Ruleset(name='QSO Party')
        self.assertEquals('QSO Party', unicode(r))

    def test_save(self):
        Ruleset.objects.create(name='Foo QSO Party')

        try:
            Ruleset.objects.create(name='Foo QSO Party')
            self.fail('Should have thrown exception')
        except DatabaseError:
            pass

class LogFormTests(TestCase):
    def test_validate_when_present(self):
        f = ContactForm(data={'when': '2011-01-02 03:04'})
        self.assertFalse(f.is_valid())
        self.assertFalse(f.errors.get('when'))

    def test_validate_when_missing(self):
        f = ContactForm(data={'when': None})
        self.assertFalse(f.is_valid())
        self.assertFalse(f.errors.get('when'))

    def test_validate_callsign(self):
        f = ContactForm(data={'callsign': None})
        self.assertFalse(f.is_valid())
        self.assertEquals([u"Please provide the contact's callsign."], f.errors.get('callsign'))

    def test_validate_frequency(self):
        f = ContactForm(data={'frequency': None})
        self.assertFalse(f.is_valid())
        self.assertFalse(f.errors.get('frequency'))

        f = ContactForm(data={'frequency': 'asdf'})
        self.assertFalse(f.is_valid())
        self.assertEquals([u"Please enter frequency in the format 7.123"], f.errors.get('frequency'))

        f = ContactForm(data={'frequency': '-1.0'})
        self.assertFalse(f.is_valid())
        self.assertEquals([u"Frequency must be positive."], f.errors.get('frequency'))

    def test_validate_mode(self):
        f = ContactForm(data={'mode': None})
        self.assertFalse(f.is_valid())
        self.assertEquals([u"Please select a mode."], f.errors.get('mode'))

    def test_validate_band(self):
        f = ContactForm(data={'band': None})
        self.assertFalse(f.is_valid())
        self.assertEquals([u"Please select a band or enter a frequency."], f.errors.get('__all__'))
        
        f = ContactForm(data={'frequency': '7.1'})
        self.assertFalse(f.is_valid())
        self.assertFalse(f.errors.get('__all__'))
        
    def test_validate_rst_sent(self):
        f = ContactForm(data={'rst_sent': None})
        self.assertFalse(f.is_valid())
        self.assertFalse(f.errors.get('rst_sent'))

        for bad_rst in ('abc','5','5999','69','00','3a'):
            f = ContactForm(data={'rst_sent': bad_rst})
            self.assertFalse(f.is_valid())
            self.assertEquals([u'RST Sent should be in the format 59 or 599.'],f.errors.get('rst_sent'))
        
        f = ContactForm(data={'rst_sent': '599'})
        self.assertFalse(f.is_valid())
        self.assertFalse(f.errors.get('rst_sent'))

    def test_validate_rst_received(self):
        f = ContactForm(data={'rst_received': None})
        self.assertFalse(f.is_valid())
        self.assertFalse(f.errors.get('rst_received'))

        for bad_rst in ('abc','5','5999','69','00','3a'):
            f = ContactForm(data={'rst_received': bad_rst})
            self.assertFalse(f.is_valid())
            self.assertEquals([u'RST Received should be in the format 59 or 599.'],f.errors.get('rst_received'))
        
        f = ContactForm(data={'rst_received': '599'})
        self.assertFalse(f.is_valid())
        self.assertFalse(f.errors.get('rst_received'))

    def test_contest_exchange_sent(self):
        f = ContactForm(data={'contest_exchange_sent': None})
        self.assertFalse(f.is_valid())
        self.assertFalse(f.errors.get('contest_exchange_sent'))

    def test_contest_exchange_received(self):
        f = ContactForm(data={'contest_exchange_received': None})
        self.assertFalse(f.is_valid())
        self.assertFalse(f.errors.get('contest_exchange_received'))

    def test_save(self):
        cl = make_contactlog()
        operator = make_operator()

        f = ContactForm(data={'callsign': 'W2PE',
                              'mode': Mode.objects.get(name='CW').id,
                              'band': Band.objects.get(name='20m').id,
                              'frequency': '14.125',
                              'when': '2011-01-02 03:04',
                              'rst_sent': '59',
                              'rst_received': '599',
                              'contest_exchange_sent': '1/NY',
                              'contest_exchange_received': '33/WV'})

        self.assertTrue(f.is_valid())
        self.assertEquals(0, Contact.objects.filter(callsign='W2PE').count())

        contact = f.save(contact_log=cl,operator=operator)

        self.assertEquals(1, Contact.objects.filter(callsign='W2PE').count())
        self.assertEquals('W2PE', contact.callsign)
        self.assertEquals('2011-01-02 03:04:00', unicode(contact.when))
        self.assertEquals(cl, contact.contact_log)
        self.assertEquals(operator, contact.operator)
        self.assertEquals('CW', contact.mode.name)
        self.assertEquals('20m', contact.band.name)
        self.assertEquals('59', contact.rst_sent)
        self.assertEquals('599', contact.rst_received)
        self.assertEquals('1/NY', contact.contest_exchange_sent)
        self.assertEquals('33/WV', contact.contest_exchange_received)
        self.assertEquals('14.125', contact.frequency)
        
    def test_save_set_when(self):
        cl = make_contactlog()
        operator = make_operator()

        f = ContactForm(data={'callsign': 'W2PE',
                              'mode': Mode.objects.get(name='CW').id,
                              'band': Band.objects.get(name='20m').id})

        self.assertTrue(f.is_valid())
        self.assertEquals(0, Contact.objects.filter(callsign='W2PE').count())

        contact = f.save(contact_log=cl,operator=operator)

        self.assertEquals(1, Contact.objects.filter(callsign='W2PE').count())
        self.assertEquals('W2PE', contact.callsign)
            
        d = datetime.datetime.utcnow()
        self.assertEquals(d.year, contact.when.year)
        self.assertEquals(d.month, contact.when.month)
        self.assertEquals(d.day, contact.when.day)
        self.assertEquals(d.hour, contact.when.hour)
        self.assertEquals(d.minute, contact.when.minute)

    def test_save_set_band(self):
        cl = make_contactlog()
        operator = make_operator()

        f = ContactForm(data={'callsign': 'W2PE',
                              'frequency': '14.243',
                              'mode': Mode.objects.get(name='CW').id})
        self.assertTrue(f.is_valid())
        self.assertEquals(0, Contact.objects.filter(callsign='W2PE').count())

        contact = f.save(contact_log=cl,operator=operator)

        self.assertEquals(1, Contact.objects.filter(callsign='W2PE').count())
        self.assertEquals('W2PE', contact.callsign)
        self.assertEquals('20m', contact.band.name)

        f = ContactForm(data={'callsign': 'W2PE',
                              'frequency': '1.000',
                              'mode': Mode.objects.get(name='CW').id})
        self.assertFalse(f.is_valid())
        self.assertEquals({'__all__': [u'Please select a band or enter a frequency.']}, f.errors)

    def test_get_fieldless_errors(self):
        f = ContactForm()  
        self.assertFalse(f.get_fieldless_errors())

        f = ContactForm({'asd':'asdfsafd'})
        self.assertEquals([u'Please select a band or enter a frequency.'], f.get_fieldless_errors())

class ContactLogTests(TestCase):
    def test_unicode(self):
        o = Operator(callsign='KC2ZUF')
        r = Ruleset(name='QSO Party')
        l = ContactLog(name='Flarp',owner=o,ruleset=r)

        self.assertEquals('Flarp', unicode(l))

    def test_save(self):
        cl = make_contactlog()

        # Should be able to create another identical log w/o exception
        make_contactlog(owner=cl.owner, ruleset=cl.ruleset)

class LogEntryTests(TestCase):
    def test_unicode(self):
        le = Contact(when=datetime.datetime(2011,1,2,1,2,3), callsign='W2PE')
        self.assertEquals('2011-01-02 01:02:03, W2PE', unicode(le))

    def test_save(self):
        cl = make_contactlog()
        op = make_operator()
        le = Contact.objects.create(when=datetime.datetime(2011,1,2,1,2,3), 
                                     callsign='W2PE',
                                     mode=Mode.objects.get(name='SSB'),
                                     band=Band.objects.get(name='20m'),
                                     contact_log=cl,
                                     operator=op)
        
        # Should be able to create a dupe
        Contact.objects.create(when=datetime.datetime(2011,1,2,1,2,3), 
                                     callsign='W2PE',
                                     mode=Mode.objects.get(name='SSB'),
                                     band=Band.objects.get(name='20m'),
                                     contact_log=cl,
                                     operator=op)

class ViewTests(TestCase):
    def test_home_template_empty(self):
        s = render_to_string('home.html', {})
        self.assertTrue('You have not set up any contact logs.' in s)
        self.assertFalse('Flarp' in s)

    def test_home_template_not_empty(self):
        s = render_to_string('home.html', {'logs': [make_contactlog()]})
        self.assertFalse('You have not set up any contact logs.' in s)
        self.assertTrue('Flarp' in s)
    
    def test_home_queryset(self):
        v = views.HomeView()
        self.assertEquals([], list(v.get_queryset()))
        cl = make_contactlog()
        self.assertEquals([cl], list(v.get_queryset()))
    
    def test_contact_log(self):
        cl = make_contactlog()
        v = views.ContactLogView()
        ctx = v.get_context_data(pk=cl.pk)
        self.assertEquals(cl, ctx['contact_log'])
        
        e = make_contact(contact_log=cl)
        v = views.ContactLogView()
        ctx = v.get_context_data(pk=cl.pk)
        self.assertEquals(cl, ctx['contact_log'])
        self.assertEquals([e], list(x for x in ctx['contacts']))

    def test_contact_log_template_empty(self):
        e = make_contact()
        s = render_to_string('contact_log.html', {'contacts': [],'form':MockForm()})
        self.assertTrue('You have not logged any entries yet.' in s)
        self.assertTrue('this is the field when' in s)
        self.assertFalse(e.callsign in s)

    def test_contact_log_template_list(self):
        e = make_contact()
        s = render_to_string('contact_log.html', {'contacts': [e],'form':MockForm()})
        self.assertFalse('You have not logged any entries yet.' in s)
        self.assertTrue(e.callsign in s)
        self.assertTrue('this is the field when' in s)

    def test_contact_log_template_form(self):
        e = make_contact()
        f = MockForm()
        f.errors = {'mode': 'A mode error'}
        s = render_to_string('contact_log.html', {'contacts': [e],'form':f})
        self.assertTrue('A mode error' in s)



class ViewSecurityTests(TestCase):
    def test_home(self):
        c = Client()
        response = c.get(reverse('home'))
        self.assertEquals(200, response.status_code)

    def test_contact_log(self):
        cl = make_contactlog()
        c = Client()
        response = c.get(reverse('contact_log',kwargs={'pk': cl.pk}))
        self.assertEquals(200, response.status_code)
