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

from qso.models import Ruleset, ContactLog, Operator, Band, Mode, LogEntry
from qso import views

def make_operator():
    return Operator.objects.create(callsign='KC2ZUF')

def make_ruleset():
    return Ruleset.objects.create(name='QSO Party')

def make_contactlog(owner=None, ruleset=None):
    return ContactLog.objects.create(name='Flarp',
                                     owner=owner or make_operator(),
                                     ruleset=ruleset or make_ruleset())

def make_logentry(contact_log=None):
    return LogEntry.objects.create(when=datetime.datetime(2011,1,2,1,2,3), 
                                     de_callsign='W2PE',
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
        le = LogEntry(when=datetime.datetime(2011,1,2,1,2,3), de_callsign='W2PE')
        self.assertEquals('2011-01-02 01:02:03, W2PE', unicode(le))

    def test_save(self):
        cl = make_contactlog()
        op = make_operator()
        le = LogEntry.objects.create(when=datetime.datetime(2011,1,2,1,2,3), 
                                     de_callsign='W2PE',
                                     mode=Mode.objects.get(name='SSB'),
                                     band=Band.objects.get(name='20m'),
                                     contact_log=cl,
                                     operator=op)
        
        # Should be able to create a dupe
        LogEntry.objects.create(when=datetime.datetime(2011,1,2,1,2,3), 
                                     de_callsign='W2PE',
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
        v = views.ContactLogView(kwargs={'pk': cl.pk})
        self.assertEquals(cl, v.get_object())
        v.object = v.get_object()

        e = make_logentry(contact_log=cl)
        v = views.ContactLogView(kwargs={'pk': cl.pk})
        v.object = v.get_object()
        ctx = v.get_context_data()
        self.assertEquals(cl, ctx['contact_log'])
        self.assertEquals([e], list(x for x in ctx['log_entries']))

    def test_contact_log_template_empty(self):
        e = make_logentry()
        s = render_to_string('contact_log.html', {'log_entries': []})
        self.assertTrue('You have not logged any entries yet.' in s)
        self.assertFalse(e.de_callsign in s)

    def test_contact_log_template_list(self):
        e = make_logentry()
        s = render_to_string('contact_log.html', {'log_entries': [e]})
        self.assertFalse('You have not logged any entries yet.' in s)
        self.assertTrue(e.de_callsign in s)

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
