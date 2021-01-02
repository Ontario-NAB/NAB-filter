from ebird_filter.ebird_file.ebird_line import eBirdLine

class eBirdFile:
    """
    Small utility class to open and read an eBird data file.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.headers = self.read_headers()
    
    def read_file(self):
        with open(self.file_path, encoding='utf8', errors='ignore') as f:
            # Skip the first line as these are the headers.
            f.readline()
            for line in f:
                yield eBirdLine(line, self.headers)
    
    def read_headers(self):
        with open(self.file_path, encoding='utf8', errors='ignore') as f:
            headers = f.readline().split('\t')
        return headers
    
    def get_headers(self):
        return self.headers