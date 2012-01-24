"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from adif import ADIFParser, ADIFRecord, ADIFException

class ADIFExporterTests(TestCase):
	def test_none(self):
		self.fail('test exporter')

class ADIFTagTests(TestCase):
	def test_test(self):
		self.fail('test tag types')

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

	def test_tag_parse(self):
		p = ADIFParser('<call:4>W2PE <class:2>2A')
		t = p._next_tag()
		self.assertEquals('call', t.tag)
		self.assertEquals('W2PE', t.content)
		t = p._next_tag()
		self.assertEquals('class',t.tag)
		self.assertEquals('2A', t.content)
	
	def test_eor(self):
		p = ADIFParser('<eor> abc')
		t = p._next_tag()
		self.assertEquals('eor', t.tag)
	
	def test_eoh(self):
		p = ADIFParser('<eoh> efg')
		t = p._next_tag()
		self.assertEquals('eoh', t.tag)

	def test_record_parse(self):
		p = ADIFParser('<call:4>W2PE <class:2>2A<eor>')
		r = p.next_record()
		self.assertEquals('W2PE',r.call)
		self.assertEquals('2A',r.class_r)

	def test_data_type(self):
		self.fail('need to test data type')
