import calendar
import csv
from shapely.geometry.polygon import Polygon

def compare_day(obs_date, start_month, start_day, end_month, end_day):
    """
    Checks whether the day contained in obs_date falls between start_month and end_month.
    """
    obs_month = obs_date.month
    obs_day = obs_date.day

    if not start_day and not end_day:
        return True
    if not start_day and end_day:
        start_day = 1
    if not end_day and start_day:
        end_day = calendar.monthrange(obs_date.year, end_month)[1]

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
    obs_month =obs_date.month
    if end_month < start_month:
        return (obs_month >= start_month or obs_month <= end_month) and compare_day(obs_date, start_month, start_day, end_month, end_day)
    return (obs_month >= start_month and obs_month <= end_month)  and compare_day(obs_date, start_month, start_day, end_month, end_day)

def compare_location(point, polygon):
    """
    Checks whether the point defined by point falls within polygon.
    """
    if not polygon:
        return True
    return polygon.contains(point)

def check_rule(ebird_line, rule):
    """
    Returns True if the observation in ebird_line matches rule, False otherwise.
    """
    start_month, start_day, end_month, end_day, polygon = rule
    return compare_time(ebird_line.get_date(), start_month, end_month, start_day, end_day) and compare_location(ebird_line.get_geo_point(), polygon)

def check_obs(ebird_line, rule_dict):
    """
    Returns True if the observation in ebird_line matches at least one of the loaded rules, False otherwise.
    """
    common_name = ebird_line.get_common_name().strip().lower()
    return common_name in rule_dict and any([check_rule(ebird_line, rule) for rule in rule_dict[common_name]])

def load_rules(rules_file):
    """
    Reads the rules file into a dictionary which is used to filter dataset observations.
    Coordinate lists are transformed into the Polygon object equivalents.
    """
    rule_dict = {}
    with open(rules_file) as f:
        reader = csv.reader(f)
        headers = next(reader)
        for line_vals in reader:
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