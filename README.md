# eBird Dataset Filter
This small Python script allows you to filter observations from the eBird dataset based on species common name, date, and location. It also allows filtering only unconfirmed records if you need to find a record that hasn't been reviewed or accepted.

As inputs, the script requires an eBird database file, which can be obtained from eBird, a rules file, which is written by the user, and an output file to which the matching records from the eBird database file are written.

## Usage
To install the requirements for this script, run:

    pip3 install .\
To run the script:

    python3 .\ebird_filter\filter_ebird_dataset.py -i 'path/to/eBird/database/file' -r 'path/to/rules/file' -o 'path/to/output/file'

To filter only unaccepted observations, add the -u flag to the command:

    python3 .\ebird_filter\filter_ebird_dataset.py -i 'path/to/eBird/database/file' -r 'path/to/rules/file' -o 'path/to/output/file' -u

 ## The Rules File
 This is a comma-separated value file that defines the criteria for filtering records. Each line contains four columns: species common name, start month, start day, end month, end day, and location. The first line of the file is the header line and is not parsed by the script, rules should start on the second line of the file.

The common name of the species in the rules file is compared against the common name present in the eBird database file. While case does not matter, the spelling must match what eBird uses. The same species may have more than one rule in the file. Each record from the eBird database file is matched at most once to prevent duplication in the case of multiple overlapping rules for the same species.

The start month and end month are integer values (1-12) used to match species only at certain times of the year. If the species should be matched throughout the year, leave these fields blank. If the start month field is left blank, but the end month is provided, the start month is assumed to be January (1). Similarly, if the start month is provided but the end month is left blank, the end month is assumed to be December (12). Months crossing a year are supported (e.g. start month = 12, end month = 3).

Similarly, the start day and end day are integer values used to narrow down the date range further. For example, passing start month of 1, start day of 15, end month of 3, and end day of 16 matches all records from January 15 to March 16 inclusive. If start day is left blank it defaults to 1, if end day is left blank it defaults to the last day of the month in the year the observation being compared was made.

The location field is a string of bar (|)  separated latitude, longitude pairs creating a polygon. A rule with location is matched when the location of the record from the eBird database file is within the polygon defined by the rules file (and all other parts of the rule for this line match). The coordinates of the polygon should be enclosed within double quotes (") so as to allow commas to separate the latitude and longitude values. If a location match is not necessary for the rule, leave this field blank.

Examples of rules lines are below:
The following rule will always match Barnacle Goose no matter where or when it was reported:

    Barnacle Goose,,,,,
The above rule is equivalent to the following three rules:

    Barnacle Goose,1,,12,,
    Barnacle Goose,,,12,,
    Barnacle Goose,1,,,,
The following rule will match King Eider anywhere it is reported from June 5th to September 10th inclusive:

    King Eider,6,5,9,10,
Similarly, this next rule will match Common Gallinule anywhere between December and March inclusive:

    Common Gallinule,12,,3,,
Finally, the below rule will match any Golden Eagle record from June to August inclusive that is reported within the defined polygon:

    Golden Eagle,6,,8,,"46.64729622613731, -84.49540784620643|46.496246353072785, -76.54130628370643|44.17996842330521, -69.81767347120643|41.17630767122074, -83.30888440870643"
## Obtaining an eBird Database File
To download all or a custom portion of the eBird database, follow the instructions here: [eBird database download](https://ebird.org/science/download-ebird-data-products) for downloading the eBird Basic Dataset (EBD). This requires an eBird account and justification for the download.