import argparse
import logging
import csv
import os
import uuid
from NAB_filter.inaturalist.inat_file import iNatFile
from NAB_filter.rules.rules import load_rules, check_obs


def find_notable_records(infile, rules_file, outfile, append, raw):
    """
    Reads the data file line-by-line, filtering any records which match at least one of the rules in the rules file.
    Records which are matched are written out to outfile.
    """
    temp_file_name = 'unsorted_obs_{}.txt'.format(uuid.uuid4())
    data_file = iNatFile(infile)
    if append:
        mode = 'a'
    else:
        mode = 'w'
    with open(temp_file_name, mode, encoding='utf8', errors='ignore', newline='',) as temp:
        writer = csv.writer(temp)
        rule_dict = load_rules(rules_file)
        species_dict = {}
        if raw:
            headers = data_file.get_headers()
            writer.writerow(headers)
        else:
            filtered_headers = data_file.get_out_headers()
            writer.writerow(filtered_headers)
        current_species = ''
        for iNat_line in data_file.read_file():
            species_name = iNat_line.get_common_name()
            if current_species != species_name:
                logging.debug('Parsing records for: {}'.format(species_name))
                current_species = species_name
            if check_obs(iNat_line, rule_dict) and not iNat_line.get_captive_cultivated():
                if raw:
                    writer.writerow(iNat_line.get_raw_line())
                else:
                    writer.writerow(iNat_line.get_filtered_line())
                if species_name not in species_dict:
                    species_dict[species_name] = None
    
    with open(temp_file_name, 'r', encoding='utf8', errors='ignore') as temp, open(outfile, mode, encoding='utf8', errors='ignore', newline='') as out:
        writer = csv.writer(out)
        if mode == 'w':
            if raw:
                headers = data_file.get_headers()
                writer.writerow(headers)
            else:
                filtered_headers = data_file.get_out_headers()
                writer.writerow(filtered_headers)
        reader = csv.reader(temp)
        next(reader)
        if raw:
            sorted_file = sorted(reader, key=lambda row: (int(row[35]), row[30], row[2]))
        else:
            sorted_file = sorted(reader, key=lambda row: (int(row[6]), row[4], row[1]))
        writer.writerows(sorted_file)

    try:
        os.remove(temp_file_name)
    except Exception as err:
        logging.error("Could not remove temp file due to: {}".format(err))
                
        logging.debug('Extracted the following species from dataset: {}'.format(list(dict.fromkeys(species_dict))))

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s:%(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='file path to the eBird dataset')
    parser.add_argument('-r', '--rules', help='file path to the rules csv')
    parser.add_argument('-o', '--outfile', help='file path to write records to')
    parser.add_argument('-a', '--append', help='use when you want to append instead of overwrite outfile',
                        action='store_true')
    parser.add_argument('-e', '--raw', help='use when you want to write the raw line instead of the filtered line',
                        action='store_true')
    args = parser.parse_args()
    find_notable_records(args.infile, args.rules, args.outfile, args.append, args.raw)
    
  