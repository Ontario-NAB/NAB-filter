import argparse
import logging
from ebird_filter.ebird.ebird_file import eBirdFile
from ebird_filter.rules.rules import load_rules, check_obs


def find_notable_records(infile, rules_file, outfile, unaccepted, append):
    """
    Reads the data file line-by-line, filtering any records which match at least one of the rules in the rules file.
    Records which are matched are written out to outfile.
    If the unaccepted flag is set, only those records which have not been accepted AND which match at least one rule are written to the file.
    """
    data_file = eBirdFile(infile)
    if append:
        mode = 'a'
    else:
        mode = 'w'
    with open(outfile, mode, encoding='utf8', errors='ignore') as out:
        rule_dict = load_rules(rules_file)
        species_dict = {}
        out.write('\t'.join(data_file.get_headers()))
        current_species = ''
        for ebird_line in data_file.read_file():
            species_name = ebird_line.get_common_name()
            if current_species != species_name:
                logging.debug('Parsing records for: {}'.format(species_name))
                current_species = species_name
            if check_obs(ebird_line, rule_dict):
                if unaccepted:
                    if not ebird_line.get_unaccepted():
                        out.write(ebird_line.get_raw_line())
                else:
                    out.write(ebird_line.get_raw_line())
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
    parser.add_argument('-a', '--append', help='use when you want to append instead of overwrite outfile',
                        action='store_true')
    args = parser.parse_args()
    find_notable_records(args.infile, args.rules, args.outfile, args.unaccepted, args.append)
    
  