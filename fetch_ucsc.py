#!/usr/bin/env python
"""A script to fetch screenshots from the UCSC browser

Usage:
======
    
    python fetch_ucsc.py --regions <regions file> --tracks <tracks file> --ucsc_url <ucsc options file>

Input files:
============

 * regions file: contains a list of regions to be analyzed
 * tracks file: contains which tracks to include, and which options
 * browser options file: a file containing the url to the UCSC browser, and username/password for custom UCSC instances. All the options that depend on which UCSC you want to connect to or on your configuration

"""

import optparse
import sys 
import mechanize
import cookielib
import ConfigParser
import re



def get_options():
    parser = optparse.OptionParser()

    parser.add_option('-r', '--regions', '--regions_file', '--region', dest='regionsfile',
            help='CSV file containing list of regions to analyze', default='')
    parser.add_option('-t', '--tracks', '--params', dest='tracksfile',
            help='file containing list of tracks to show, and other parameters', default='')
    parser.add_option('-u', '--ucsc', '--ucsc_file', '--browser', '--config', '--browser_config', dest='browser_config_file',
            help='file containing URL to the UCSC browser, and eventually username and password', default='params/browser_config/default.txt')

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


def get_browser_config(optionsfile):
    """
    Scan a browser options file for parameters.

    example browser options file:

    :: 
        [browser]
        ucsc_base_url = http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg18
        username =
        password =
        User-agent = Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1
        email = 

        [proxy]
        proxy = 
        port =
        password = 
    """
    browseroptions = {}
    configparser = ConfigParser.ConfigParser()
    configparser.read(optionsfile)
#    print(configparser.items("browser"))
#    print configparser.options("browser")
    browseroptions = dict(configparser.items("browser"))

    if browseroptions['email'] == '':
        raise ConfigParser.Error('the email field is required. Please edit %s and add your email address' % optionsfile)

    return browseroptions
#    return configparser

def get_chromosome_positions(regionsfile):
    """
    Scan a config Regions file for parameters

    Example Regions file:

    :: 

        chromosome  start   end label
        chr1    10000    20000  sampleregion
    """

def get_tracks_options(tracksfile):
    """
    Parse a Tracks options file, to determine which tracks to turn off and on.

    Example Tracks file:

        [visual_options]

        [tracks]
        wgRna=hide
        cpgIslandExt=pack
        ensGene=hide
        mrna=hide
        intronEst=hide
        mgcGenes=hide
        hgt.psOutput=on
        cons44way=hide
        snp130=hide
        snpArray=hide
        wgEncodeReg=hide
        pix=1000
        refGene=pack
        knownGene=hide
        rmsk=hide

    Returns a string that can be attached to the base ucsc URL

    """
    parser = ConfigParser.ConfigParser()
    parser.read(tracksfile)
    parser.items("tracks")

def initialize_browser(browseroptions):
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
    br.addheaders = [('User-agent', browseroptions['user-agent'])]
    br.addheaders.append(('email', browseroptions['email']))

    if browseroptions["httpproxy"] != '':
        # proxy password not implemented
        br.setproxies({'http': "%s:%s" % (browseroptions['httproxy'], browseroptions['httproxy_port'])})

    if browseroptions['username'] != '':
        baseurl = re.findall('http://.*?/', browseroptions['ucsc_base_url'])[0]
        br.add_password(baseurl, browseroptions['username'], browseroptions['password'])

    return br

def get_screenshot(browseroptions):
    """
    Note: to get the screenshot, add &hgt.psOutput=on to the URL, and then download the third link
    """
    pass


#def main():
if __name__ == '__main__':
    (options, args) = get_options()
    browseroptions = get_browser_config(options.browser_config_file)
    print browseroptions
    br = initialize_browser(browseroptions)

#    main()
