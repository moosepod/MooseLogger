"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from qso.models import Ruleset, ContactLog, Operator
from qso import views

def make_operator():
    return Operator.objects.create(callsign='KC2ZUF')

def make_ruleset():
    return Ruleset.objects.create(name='QSO Party')

def make_contactlog(owner=None, ruleset=None):
    return ContactLog.objects.create(name='Flarp',
                                     owner=owner or make_operator(),
                                     ruleset=ruleset or make_ruleset())
class OperatorTests(TestCase):
    def test_unicode(self):
        o = Operator(callsign='KC2ZUF')
        self.assertEquals('KC2ZUF', unicode(o))

    def test_save(self):
        Operator.objects.create(callsign='KC2ZUF')

        try:
            Operator.objects.create(callsign='KC2ZUF')
            self.fail('Should have thrown exception')
        except Exception:
            pass

        Operator.objects.create(callsign='AA7AAA/AE')

class RulesetTests(TestCase):
    def test_unicode(self):
        r = Ruleset(name='QSO Party')
        self.assertEquals('QSO Party', unicode(r))

    def test_save(self):
        Operator.objects.create(callsign='QSO Party')

        try:
            Operator.objects.create(callsign='QSO Party')
            self.fail('Should have thrown exception')
        except Exception:
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

class ViewSecurityTests(TestCase):
    def test_home(self):
        c = Client()
        response = c.get(reverse('home'))
        self.assertEquals(200, response.status_code)
