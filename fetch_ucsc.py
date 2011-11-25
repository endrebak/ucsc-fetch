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
import mechanize
import cookielib


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

def initialize_browser():
    """
    initialize a Browser object.

    Acknowledgements to: http://stockrt.github.com/p/emulating-a-browser-in-python-with-mechanize/
    """

    br = mechanize.Browser()
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
#    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
#    br.set_debug_http(True)
#    br.set_debug_redirects(True)
#    br.set_debug_responses(True)

    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.addheaders.append(('email', 'giovanni.dallolio@upf.edu'))

    return br


basicurl = """http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg18&
    wgRna=hide
    &cpgIslandExt=pack
    &ensGene=hide
    &mrna=hide
    &intronEst=hide
    &mgcGenes=hide
    &hgt.psOutput=on
    &cons44way=hide
    &snp130=hide
    &snpArray=hide
    &wgEncodeReg=hide
    &pix=1000
    &refGene=pack
    &knownGene=hide
    &rmsk=hide"""

if __name__ == '__main__':
    get_options()
    initialize_browser()

