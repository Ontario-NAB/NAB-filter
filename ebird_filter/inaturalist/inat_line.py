import datetime
from shapely.geometry import Point
from distutils.util import strtobool

class iNatLine():
    """
    Utility class to get data from an iNaturalist data file line.
    """
    def __init__(self, raw_line, headers):
        self.headers = headers
        self.raw_line = raw_line
        self.line_dict =  dict(zip(headers, raw_line))
    
    def get_field(self, name):
        return self.line_dict[name]
    
    def get_geo_point(self):
        lat = self.get_field('latitude')
        lon = self.get_field('longitude')
        point = Point(float(lat), float(lon))
        return point
    
    def get_date(self):
        return datetime.datetime.strptime(self.get_field('observed_on'), "%Y-%m-%d")
    
    def get_common_name(self):
        return self.get_field('common_name')
    
    def get_county(self):
        try:
            return self.get_field('place_county_name')
        except KeyError:
            return ''
    
    def get_url(self):
        return self.get_field('url')
    
    def get_captive_cultivated(self):
        return strtobool(self.get_field('captive_cultivated'))
    
    def pretty_print(self):
        header_line = ','.join(self.headers)
        return '\n'.join([header_line, self.join_raw_line()])
    
    def join_raw_line(self):
        return '{}\n'.format(','.join(self.raw_line))
    
    def get_raw_line(self):
        return self.raw_line
    
    def get_filtered_line(self):
        return [self.get_common_name(), self.get_field('observed_on'), self.get_field('latitude'), self.get_field('longitude'), self.get_county(), self.get_url()]
        