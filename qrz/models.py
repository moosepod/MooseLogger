from django.db import models
from xml.parsers.expat import ExpatError
import StringIO

import elementtree.ElementTree as ET

### See http://www.qrz.com/XML/current_spec.html for spec

class QRZRecord(object):
    def __init__(self, xml_data=None):
        self.error = None
        self.call = None           # call
        self.fname = None          # fname
        self.name = None           # name
        self.addr1 = None          # addr1
        self.addr2 = None          # addr2
        self.state = None          # state 
        self.zip = None            # zip
        self.country = None        # country
        self.lat = None            # lat
        self.lon = None            # lon
        self.grid = None           # grid
        self.county = None         # county
        self.license_class = None  # class
        self.will_qsl = None       # mqsl
        self.will_eqsl = None      # eqsl
        self.is_authenticated = False

        if xml_data:    
            self.load_from_xml(xml_data)

    def is_dx(self):
        if not self.country: 
            return False

        return 'united states' != self.country.lower()

    def find_qrz_value(self, root, tag):
        node = root.find('{http://www.qrz.com}%s' % tag)

        if node == None:
            return None

        return node.text

    def load_from_xml(self, xml_data):
        try:
            tree = ET.parse(StringIO.StringIO(xml_data))
            doc = tree.getroot()

            try:
                session = [n for n in doc.getchildren() if n.tag == '{http://www.qrz.com}Session'][0]
            except IndexError:
                session = None

            try:
                callsign = [n for n in doc.getchildren() if n.tag == '{http://www.qrz.com}Callsign'][0]
            except IndexError:
                callsign = None

            if not callsign:
                self.is_authenticated = False
                error = self.find_qrz_value(session,'Error')
                if error != 'Invalid session key':
                    self.error = error
            else:
                self.is_authenticated = True

                self.call = self.find_qrz_value(callsign,'call')
                self.name = self.find_qrz_value(callsign,'name')
                self.fname = self.find_qrz_value(callsign,'fname')
                self.addr1 = self.find_qrz_value(callsign,'addr1')
                self.addr2 = self.find_qrz_value(callsign,'addr2')
                self.state = self.find_qrz_value(callsign,'state')
                self.zip = self.find_qrz_value(callsign,'zip')
                self.country = self.find_qrz_value(callsign,'country')
                self.lat = self.find_qrz_value(callsign,'lat')
                self.lon = self.find_qrz_value(callsign,'lon')
                self.grid = self.find_qrz_value(callsign,'grid')
                self.county = self.find_qrz_value(callsign,'county')
                self.license_class = self.find_qrz_value(callsign,'class')
                self.will_qsl = self.find_qrz_value(callsign,'mqsl')
                self.will_eqsl = self.find_qrz_value(callsign,'eqsl')
        except Exception, e:
            self.error = unicode(e)
