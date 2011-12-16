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
try:
    import mechanize
except ImportError:
    print "You need to install the mechanize module. Get it at http://wwwsearch.sourceforge.net/mechanize/ or through easy_install"
    sys.exit(1)
import cookielib
import ConfigParser
import re
import time
import csv
import os
import subprocess
import logging


def get_options():
    parser = optparse.OptionParser(usage="usage: %prog -r <regions file> -t <tracks file> -b <browser config file> [-o <output folxder>]")

    parser.add_option('-r', '--regions', '--regions_file', '--region', dest='regionsfile',
            help='CSV file containing list of regions to analyze', default='')
    parser.add_option('-t', '--tracks', '--params', dest='tracksfile',
            help='file containing list of tracks to show, and other parameters', default='')
    parser.add_option('-u', '-b', '--ucsc', '--ucsc_file', '--browser', '--config', '--browser_config', dest='browser_config_file',
            help='file containing URL to the UCSC browser, and eventually username and password', default='params/browser_config/default.txt')
    parser.add_option('-o', '-f', '--output', '--output-folder', '--folder', dest='outputfolder',
            help='output folder (default=results)', default='results/')
    parser.add_option('-s', '--skip-existing', '-e', '--skip-downloaded', dest='skip_existing', action='store_true',
            help='Skip downloading UCSC screenshots that have already been downloaded. Useful for debugging purposes, or if you need to add a region to list of regions that you have already downloaded in a previous run.', 
            default=False)
    parser.add_option('-l', '--layout', dest='layout', 
            help='Output layout: how to dispose multiple screenshots in a single page. must be a string in the format "numberxnumber", e.g. 3x2, where 3 is the number of rows, and 2 is the number of columns',
            default='2x2')
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            help='set debug mode on', default=False)
    (options, args) = parser.parse_args()
    
    if options.debug is True:
        logging.basicConfig(format='%(levelname)s:%(pathname)s (line %(lineno)s): %(message)s', level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)

#    print options.inputfile
    # required options
    if options.regionsfile == '':
        parser.print_help()
        parser.error('fetch_ucsc.py: regions file not defined.')
    if options.tracksfile == '':
        parser.print_help()
        parser.error('fetch_ucsc.py: tracks not defined.')
    if not re.match('^\d+x\d+$', options.layout):
        parser.print_help()
        parser.error('fetch_ucsc.py: incorrect layout')

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
#    browseroptions = dict(configparser.items("browser") + configparser.items("output"))
    browseroptions = dict(configparser.items("browser"))

    if browseroptions['email'] == '':
        raise ConfigParser.Error('the email field is required. Please edit %s and add your email address' % optionsfile)

    return browseroptions
#    return configparser

def get_regions(regionsfile):
    """
    Scan a config Regions file for parameters

    Example Regions file:

    :: 

        #label, chromosome, start, end
        sampleregion, chr1, 10000, 20000
        gene1, chr2, 2000, 3000

    Optionally, the region files can contain three additional columns: description, upstream and downstream.
    The description is a short text used in the multi-page report to describe information about the region. It must be delimited by double quotes (")
    The last two parameters, upstream and downstream, can be used to zoom out of the region. It is useful if you have a set of gene coordinates, and want to include some margins without having to calculate them manually.

    ::

        #label, organism, assembly, chromosome, start, end, description, upstream, downstream
        sampleregion, human, hg18, chr1, 10000, 20000, "an example region", 0, 0
        gene1, chr2, human, hg18, 2000, 3000, "my favorite gene", 0, 0
        gene1_1000window, human, hg18, chr2, 2000, 3000, "my favorite gene with a 1k zoom out", 1000, 1000

    """
    regions = {}

    
    regionsfile_contents = open(regionsfile, 'r')

    scanner = csv.reader(regionsfile_contents, delimiter=',', skipinitialspace=True)

    for fields in scanner:
        if fields == []:
            logging.debug("no fields")
            continue
        if fields[0].startswith('#'):
            logging.debug("comment")
            continue
        logging.debug(fields)
        description = ''
        upstream = downstream = 0
        (label, organism, assembly, chromosome, start, end) = fields[0:6]
        if len(fields) > 6:
            description = fields[6]
        if len(fields) > 7:
            upstream = int(fields[7])
#            logging.debug(upstream)
        if len(fields) > 8:
            downstream = int(fields[8])
#            logging.debug(downstream)

        if not chromosome.startswith('chr'):
            chromosome = 'chr' + chromosome
        
        start = int(start) - upstream
        end = int(end) + downstream
        if regions.has_key(label):
            raise Exception("duplicated entry in Regions file")
        regions[label] = {'label': label, 'organism': organism, 'assembly': assembly, 'chromosome': chromosome, 
                'start': start, 'end': end, 'description': description}

    return regions


def get_tracks_options(tracksfile):
    """
    Parse a Tracks options file, to determine which tracks to turn off and on.

    Example Tracks file:

    ::

        [visual_options]

        [custom_tracks]
        mycustomtrack = http://url_to_track

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
    parser.optionxform = str

    parser.read(tracksfile)
#    parser.items("tracks")
#    print parser.items('tracks')

    tracksfile_string = ''
    if parser.items('tracks'): 
        tracksfile_string += '&' + '&'.join(['='.join(i) for i in parser.items('tracks')])
    if parser.items('visual_options'):
        tracksfile_string += '&' + '&'.join(['='.join(i) for i in parser.items('visual_options')])

    tracksfile_string += '&hgt.customText=' + '&hgt.customText='.join([x[1] for x in parser.items("custom_tracks")])

    return tracksfile_string

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

def get_screenshot(options, br, browseroptions, tracksoptions_string, chromosome, organism, assembly, start, end, label):
    """
    Get a screenshot from a UCSC browser installation. 

    Note: to manually get a screenshot from UCSC, just add &hgt.psOutput=on to the URL, and then download the third link
    """
    
    outputfilename = "%s/%s.pdf" % (options.outputfolder, label)
    
    print "\ngetting screenshot for %s.... " % label
    target_url = browseroptions['ucsc_base_url'] + '?org=%s&db=%s' % (organism, assembly) + '&position=%s:%s-%s' % (chromosome, start, end) + tracksoptions_string + '&hgt.psOutput=on'

    if options.skip_existing and os.path.exists(outputfilename):
        print "\nOutput file %s already exists, and skip_existing is true. So I am not downloading this file." % (outputfilename)
    else:
        # wait interval between different searches. 
        query_interval = int(browseroptions['query_interval'])
        print "\nWaiting %s seconds between each query, following UCSC guidelines (http://genome.ucsc.edu/FAQ/FAQdownloads.html#download2)" % query_interval
        print "Press Ctrl-C to cancel."
        sys.stdout.write("[" + "-" * query_interval + "]\n ")
        for i in xrange(query_interval):
            time.sleep(1) # do real work here
            # update the bar
            sys.stdout.write("x")
            sys.stdout.flush()

#        time.sleep(query_interval)

        # connecting to browser
        logging.debug(target_url)
        br.open(target_url)

        pdf_url = br.click_link(url_regex=re.compile(".*\.pdf"), nr=0)
        response = br.open(pdf_url)
        
        pdf_contents = response.read()
        
        outputfolder = options.outputfolder
        if outputfolder == '':
            outputfolder = 'results'
        try:
            os.makedirs(outputfolder)
        except OSError:
            pass
        pdf_file = open('%s/%s.pdf' % (outputfolder, label), 'w')
        pdf_file.write(pdf_contents)
        pdf_file.close()

    print "\ndone"
    browser_url = target_url.replace('&hgt.psOutput=on', '')
    return browser_url

def write_report(regions, reportoutputfilename, layout, sort_regions=True):
    """use RestructuredText to write a multi-page report


    Inputs:

    * regions -> the regions to be arranged
    * reportoutputfilename -> where to store the report
    * layout -> 2-elements tuple containing x and y per page (e.g. (2, 2))
    * [sort_regions] -> do you want regions to be sorted alphabetically?

    Example Output (if installed, rst2pdf is used to convert to pdf):
    
    ::
        reportoutputfilename, page 1
        ==============================

        .. csv-table::
    
            gene1, gene2
            results/gene1.pdf , results/gene2.pdf
            gene3, gene4
            results/gene3.pdf , results/gene4.pdf
            gene5, gene6
            results/gene5.pdf , results/gene6.pdf
        
        reportoutputfilename, page 2
        ==============================

        .. csv-table::
    
            gene7, gene8
            results/gene7.pdf , results/gene8.pdf

        (layout is (3, 2))

    """
#    regions = sorted(['.. image:: ../results/' + region[0] + '.pdf' for region in regions], reverse=True)
#    print regions
    if sort_regions:
        regions_keys = sorted(regions.keys(), reverse=True)
    else: 
        # untested
        regions_keys = regions.keys()
        regions.keys.reverse()
#    print regions

    newpage_template = '''======================================================================================================
%s, page %s
======================================================================================================

    .. csv-table::
        :delim: |
'''
    report_text = newpage_template % (reportoutputfilename.rsplit('/')[1], 1)
    lastline = False
    current_page = 1

    while regions_keys:
        for row in xrange(layout[0]): 
            report_text += '\n\t'
            thisrow_regionkeys = []
            for column in xrange(layout[1]):
                try:
                    thisrow_regionkeys.append(regions_keys.pop())
                except IndexError:
                    lastline = True
#                    print "raised Index Error", thisrow_regionkeys

#            print thisrow_regionkeys
            report_text += ' | '.join(['`%s <%s>`_ (%s)' % (regions[region_key]['label'], regions[region_key]['browser_url'], regions[region_key]['description']) for region_key in thisrow_regionkeys]) + '\n\t'
            report_text += ' | '.join(['.. image:: ../results/' + regions[region_key]['label'] + '.pdf' for region_key in thisrow_regionkeys])
            report_text += '\n\t | '
            report_text += '\n\t | '
#        if lastline is not True:
#        print "lastline", lastline
        current_page += 1
        if regions_keys != []:
            report_text += '\n\n' + newpage_template % (reportoutputfilename.rsplit('/')[1], current_page)

#    print report_text
    report = open(reportoutputfilename + '.rst', 'w')
    report.write(report_text)
    report.close()

#    print reportoutputfilename
    # rst2pdf options: -s (apply stylesheet), -b 1 (break pages), -q (quiet execution)
    try:
        subprocess.call(['rst2pdf', reportoutputfilename + '.rst', '-s', './scripts/simple.css', '-b', '1', '-q'])
        print "\n\nSaved multi-page report at %s.pdf\n\n" % reportoutputfilename
    except:
        print "Error when calling rst2pdf. Please check that rst2pdf is installed correctly. http://code.google.com/p/rst2pdf/"


def main():
#if __name__ == '__main__':
    (options, args) = get_options()
    browseroptions = get_browser_config(options.browser_config_file)
#    print browseroptions
    br = initialize_browser(browseroptions)

    trackoptions_string = get_tracks_options(options.tracksfile)

    regions = get_regions(options.regionsfile)
    for (label, region) in regions.items():
#        (label, organism, assembly, chromosome, start, end, description) = region
        browser_url = get_screenshot(options, br, browseroptions, trackoptions_string, region['chromosome'], region['organism'], region['assembly'], 
                region['start'], region['end'], region['label'])
        regions[label]['browser_url'] = browser_url
#        print browser_url
        print

    reportfilename = "reports/%s_%s_%s" % (options.regionsfile.rsplit('/', 1)[-1].split('.')[0],
            options.browser_config_file.rsplit('/', 1)[-1].split('.')[0],
            options.tracksfile.rsplit('/', 1)[-1].split('.')[0])

    layout = [int(x) for x in options.layout.split('x')]
    write_report(regions, reportfilename, layout)

if __name__ == "__main__":
    import doctest
    if doctest.testmod(optionflags=doctest.ELLIPSIS |\
                                   doctest.NORMALIZE_WHITESPACE).failed == 0:
        main()

#    main()
