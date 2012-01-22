"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from adif import ADIFParser, ADIFRecord, ADIFException

class ADIFParserTests(TestCase):
	def test_none(self):
		p = ADIFParser(None)
		self.assertFalse(p.next_record())
	
	def test_empty(self):
		p = ADIFParser('')
		self.assertFalse(p.next_record())

        def test_no_records(self):
		p = ADIFParser('Here\'s a file\n with some text but no actual record!')
		self.assertFalse(p.next_record())

	def test_unclosed_tag(self):
		p = ADIFParser('<abc')
		self.assertRaises(ADIFException, p.next_record)

	def test_tag_without_colon(self):
		p = ADIFParser('<abc>')
		self.assertRaises(ADIFException, p.next_record)

	def test_tag_without_colon_alt(self):
		p = ADIFParser('<abc333>')
		self.assertRaises(ADIFException, p.next_record)

	def test_tag_without_number(self):
		p = ADIFParser('<abc:>')
		self.assertRaises(ADIFException, p.next_record)

	def test_preamature_end(self):
		p = ADIFParser('<abc:3>ab')
		self.assertRaises(ADIFException, p.next_record)

	def test_tag(self):
		p = ADIFParser('<abc:2>cde')
		t = p._next_tag()
		self.assertEquals('abc',t.tag)
		self.assertEquals('cd',t.content)

	def test_tag_case_sensitivty(self):
		p = ADIFParser('<ABc:2>CDe')
		t = p._next_tag()
		self.assertEquals('abc',t.tag)
		self.assertEquals('CD',t.content)
