from NAB_filter.inaturalist.inat_line import iNatLine
import csv

class iNatFile:
    """
    Small utility class to open and read an iNaturalist data file.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.headers = self.read_headers()
    
    def read_file(self):
        with open(self.file_path, encoding='utf8', errors='ignore') as f:
            reader = csv.reader(f)
            # Skip the first line as these are the headers.
            next(reader)
            for line in reader:
                yield iNatLine(line, self.headers)
    
    def read_headers(self):
        with open(self.file_path, encoding='utf8', errors='ignore') as f:
            reader = csv.reader(f)
            headers = next(reader)
        return headers
    
    def get_headers(self):
        return self.headers
    
    def get_out_headers(self):
        return ['common_name', 'observed_on', 'latitude', 'longitude', 'place_county_name', 'url']