#
# ADIF format, more at http://www.adif.org/adif227.htm
#
# Iterating char-by-char is not very pythonic, but was the shortest path to
# getting a basic parser in place
#

class ADIFRecord(object):
	ADIF_MAPPING = {'call' : 'call',
			'class': 'class_r'}
 
	def __init__(self):
		super(ADIFRecord,self).__init__()
		self.call = None
		self.class_r = None

	def set_attribute(self,name,value):
		attr = ADIFRecord.ADIF_MAPPING.get(name)
		if not attr:
			raise ADIFException('Unknown attribute %s' % name)
		setattr(self,attr,value)		

class ADIFTag(object):
	def __init__(self):
		self.tag = ''
		self.content_length_str = ''
		self.content = ''
	
	def content_length(self):
		return int(self.content_length_str)

class ADIFException(Exception):
	pass

class ADIFParser(object):
	WAITING_FOR_TAG_STATE = 0
	TAG_NAME_STATE        = 1
	CONTENT_LENGTH_STATE  = 2
	CONTENT_STATE         = 3

	def __init__(self, adif_str, *args,**kwargs):
		super(ADIFParser,self).__init__(*args,**kwargs)
		if adif_str == None:
			adif_str = ''
		self.adif_str = adif_str
		self.index = 0
		self.length = len(adif_str) 
		self.state = ADIFParser.WAITING_FOR_TAG_STATE
		self.current_tag = None
		self.content_end_index = 0

	""" Return the next ADIF record, or None if there are no more valid record """
	def next_record(self):
		record = ADIFRecord()
		while 1:
			tag = self._next_tag()
			if not tag:
				return None
			if tag.tag == 'eor':
				return record
			else:
				record.set_attribute(tag.tag,tag.content)

	def _next_tag(self):
		self.state = ADIFParser.WAITING_FOR_TAG_STATE
		while self._handle_next_char():
			pass		
		return self.current_tag

	def _handle_next_char(self):
		index = self.index
		self.index += 1
		if index >= self.length:
			if self.state != ADIFParser.WAITING_FOR_TAG_STATE:
				raise ADIFException('Premature end of record at index %d' % index)
			return False

		c = self.adif_str[index]
		if self.state == ADIFParser.WAITING_FOR_TAG_STATE:
			if c == '<':
				self.state = ADIFParser.TAG_NAME_STATE
				self.current_tag = ADIFTag()
		elif self.state == ADIFParser.TAG_NAME_STATE:
			if c == '<':
				raise ADIFException('Unexpected < in middle of tag at index %d' % index)		
			elif c == '>':
				if self.current_tag.tag in ('eor','eoh'):	
					return False
				raise ADIFException('Tag with no content length at index %d' % index)
			elif c == ':':
				self.state = ADIFParser.CONTENT_LENGTH_STATE
			else:
				self.current_tag.tag += c.lower()
		elif self.state == ADIFParser.CONTENT_LENGTH_STATE:
			if c == '>':
				if len(self.current_tag.content_length_str) == 0:
					raise ADIFException('Tag without content length at index %d' %  index)
				self.state = ADIFParser.CONTENT_STATE
				self.content_end_index = index+self.current_tag.content_length() + 1
			elif c not in ('0','1','2','3','4','5','6','7','8','9'):
				raise ADIFException('Non-numeric char in length in tag at index %d' % index)
			else:
				self.current_tag.content_length_str += c
		elif self.state == ADIFParser.CONTENT_STATE:
			if index < self.content_end_index:
				self.current_tag.content+= c
			
			if index + 1 >= self.content_end_index:
				self.state = ADIFParser.WAITING_FOR_TAG_STATE
				return False
		
		return True
