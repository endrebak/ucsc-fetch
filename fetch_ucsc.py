#!/usr/bin/env python
"""A script to fetch screenshots from the UCSC browser

Usage:
======
    
    python fetch_ucsc.py --regions <regions file> --tracks <tracks file> --ucsc_url <ucsc options file>

Input files:
============

 * regions file: contains a list of regions to be analyzed
 * tracks file: contains which tracks to include, and which options
 * uscs file: a file containing the url to the UCSC browser, and username/password for custom UCSC instances

"""

import optparse
import sys 


def get_options():
    parser = optparse.OptionParser()

    parser.add_option('-r', '--regions', '--regions_file', '--region', dest='regionsfile',
            help='CSV file containing list of regions to analyze', default='')
    parser.add_option('-o', '-t', '--options', '--tracks', '--config', '--params', dest='tracksfile',
            help='file containing list of tracks to show, and other parameters', default='')
    parser.add_option('-u', '--ucsc', '--ucsc_file', dest='ucsc_file',
            help='file containing URL to the UCSC browser, and eventually username and password', default='params/ucsc.default')

    (options, args) = parser.parse_args()

#    print options.inputfile
    # required options
    if options.regionsfile == '':
        parser.print_help()
        print('fetch_ucsc.py: regions file not defined.')
#        raise optparse.OptParseError('regions file missing')
        sys.exit(1)
    if options.tracksfile == '':
        parser.print_help()
        print('fetch_ucsc.py: tracks not defined.')
        sys.exit(1)

    return (options, args)






if __name__ == '__main__':
    get_options()

