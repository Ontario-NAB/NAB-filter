import datetime
import calendar
import argparse
import logging
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


COMPARISON_FIELDS = ['COMMON NAME', 'OBSERVATION COUNT', 'COUNTY', 'LOCALITY',
                     'LATITUDE', 'LONGITUDE', 'OBSERVATION DATE', 'TIME OBSERVATIONS STARTED',
                     'OBSERVER ID', 'APPROVED', 'REVIEWED', 'REASON']

def compare_day(obs_date, start_month, start_day, end_month, end_day):
    """
    Checks whether the day contained in obs_date falls between start_month and end_month.
    """
    obs_month = datetime.datetime.strptime(obs_date, "%Y-%m-%d").month
    obs_day = datetime.datetime.strptime(obs_date, "%Y-%m-%d").day

    if not start_day and not end_day:
        return True
    if not start_day and end_day:
        start_day = 1
    if not end_day and start_day:
        end_day = calendar.monthrange(datetime.datetime.now().year, end_month)[1]

    if obs_month == start_month and obs_month == end_month:
        return obs_day >= start_day and obs_day <= end_day
    if obs_month == start_month:
        return obs_day >= start_day
    if obs_month == end_month:
        return obs_day <= end_day
    return True

def compare_time(obs_date, start_month, end_month, start_day, end_day):
    """
    Checks whether the month contained in obs_date falls between start_month and end_month.
    """
    if not start_month and not end_month:
        return True
    if not start_month and end_month:
        start_month = 1
    if not end_month and start_month:
        end_month = 12
    end_month = int(end_month)
    start_month = int(start_month)
    obs_month = datetime.datetime.strptime(obs_date, "%Y-%m-%d").month
    if end_month < start_month:
        return (obs_month >= start_month or obs_month <= end_month) and compare_day(obs_date, start_month, start_day, end_month, end_day)
    return (obs_month >= start_month and obs_month <= end_month)  and compare_day(obs_date, start_month, start_day, end_month, end_day)

def compare_location(lat, lon, polygon):
    """
    Checks whether the point defined by lat, lon falls within polygon.
    """
    if not polygon:
        return True
    point = Point(float(lat), float(lon))
    return polygon.contains(point)

def check_rule(obs_line, rule):
    """
    Returns True if the observation in obs_line matches rule, False otherwise.
    """
    obs_date = obs_line['OBSERVATION DATE']
    lat = obs_line['LATITUDE']
    lon = obs_line['LONGITUDE']
    start_month, start_day, end_month, end_day, polygon = rule
    return compare_time(obs_date, start_month, end_month, start_day, end_day) and compare_location(lat, lon, polygon)

def check_obs(obs_line, rule_dict):
    """
    Returns True if the observation in obs_line matches at least one of the loaded rules, False otherwise.
    """
    common_name = obs_line['COMMON NAME'].strip().lower()
    return common_name in rule_dict and any([check_rule(obs_line, rule) for rule in rule_dict[common_name]])

def load_rules(rules_file):
    """
    Reads the rules file into a dictionary which is used to filter dataset observations.
    Coordinate lists are transformed into the Polygon object equivalents.
    """
    rule_dict = {}
    with open(rules_file) as f:
        headers = f.readline().split(',')
        for line in f:
            line_vals = line.strip().split(',', 5)
            coord_list = line_vals[5].strip('"').split('|') if line_vals[5] else None
            if coord_list:
                coord_inputs = [tuple([float(x.split(",")[0]), float(x.split(",")[1].strip())]) for x in coord_list]
                polygon = Polygon(coord_inputs)
            else:
                polygon = None
            common_name = line_vals[0].strip().lower()
            if common_name not in rule_dict:
                rule_dict[common_name] = [[line_vals[1], line_vals[2], line_vals[3], line_vals[4], polygon]]
            else:
                rule_dict[common_name].append([line_vals[1], line_vals[2], line_vals[3], line_vals[4], polygon])
        return rule_dict

def find_notable_records(infile, rules_file, outfile, unaccepted):
    """
    Reads the data file line-by-line, filtering any records which match at least one of the rules in the rules file.
    Records which are matched are written out to outfile.
    If the unaccepted flag is set, only those records which have not been accepted AND which match at least one rule are written to the file.
    """
    with open(infile, encoding='utf8', errors='ignore') as f, open(outfile, 'w', encoding='utf8', errors='ignore') as out:
        rule_dict = load_rules(rules_file)
        species_dict = {}
        header_line = f.readline()
        headers = header_line.split('\t')
        out.write(header_line)
        current_species = ''
        for line in f:
            line_dict = dict(zip(headers, line.split('\t')))
            compare_dict = { comp_key: line_dict[comp_key] for comp_key in COMPARISON_FIELDS}
            species_name = compare_dict['COMMON NAME']
            if current_species != species_name:
                logging.debug('Parsing records for: {}'.format(species_name))
                current_species = species_name
            if check_obs(compare_dict, rule_dict):
                if unaccepted:
                    if not int(compare_dict['APPROVED']):
                        out.write(line)
                else:
                    out.write(line)
                if species_name not in species_dict:
                    species_dict[species_name] = None
                
        logging.debug('Extracted the following species from dataset: {}'.format(list(dict.fromkeys(species_dict))))

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s:%(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='file path to the eBird dataset')
    parser.add_argument('-r', '--rules', help='file path to the rules csv')
    parser.add_argument('-o', '--outfile', help='file path to write records to')
    parser.add_argument('-u', '--unaccepted', help='use when parsing unaccepted records',
                        action='store_true')
    args = parser.parse_args()
    find_notable_records(args.infile, args.rules, args.outfile, args.unaccepted)
    
  