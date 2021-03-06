Fork of the brilliant Giovanni Dall'Olio's UCSC-fetch. Use the original, this
repo is me jotting down things I'd like to change eventually whilst making some
minor changes.

- make python3 compatible (see https://github.com/hickford/MechanicalSoup )
- replace much of config options with command line arguments
- choose report output filename
- remove binary files from repo
- choose pdf names
- use bigwig from command line (by using git lfs and git config)
- allow to use bed file together instead of region file (can have metadata as 7th col, genome/species/upstream/downstream set on command line)
- create report sorted in order of input?
- install instructions that show pip commands
- know the time it will take so use click library to show time left and progress bar
- wait after downloading so that you do not need to wait 15 secs for single picture
- add a note on how to display custom bigwig files as full


---

=============
UCSC fetch
=============


A script to fetch screenshots from the UCSC browser


Usage:
++++++

    $: python fetch_ucsc.py --regions <regions file> --tracks <tracks file> --browser_config <browser config file> [--output-folder <output folder>]

In order to use this script, you need to edit and customize three files: the
Regions file, the Tracks file, and the Browser config file. Most of these have
default values included in this distribution, but **be sure to change your email
address** in the Browser config file, otherwise the script will refuse to work.

1. the Regions file
-------------------

The regions file is a tab-separated file containing the regions to be displayed,
one per line. The script will generate a separate .pdf file for each entry in this file.

Example:

::

    #label, organism, assembly, chromosome, start, end, description, upstream, downstream
    IL10, human, hg18, chr1, 205007571, 205012462, "involved in immunity", 10000, 1000
    PRNP, human, hg18, chr20, 4615157, 4630234, "Prion Protein", 10000, 10000
    HSPB4, human, hg18, chr21, 43462210, 43465982, "Heat-shock protein", 10000, 10000

Look at params/regions/default.txt for an example Regions file.

2. the Tracks file
-------------------

The tracks file contains the configuration of which tracks to show, and of which
database and organism to use. For each entry in the Regions file, the script will generate a pdf with the same tracks for each.

Example:

::

    [visual_options]

    [custom_tracks]
    track1 = http://pastebin.com/raw.php?i=CKCuYGmX

    [tracks]
    wgRna=hide
    wgEncodeReg=hide
    cpgIslandExt=hide
    ensGene=hide
    mrna=hide
    intronEst=hide
    mgcGenes=hide
    cons44way=hide
    snp130=hide
    snpArray=hide
    refGene=hide
    wgEncodeRegMarkPromoter=full
    knownGene=full
    rmsk=hide
    phyloP46wayPlacental=hide

Or save visual settings (track height, mode, or track data from track hubs, etc.) as session, and set as shared. See example figure 'reports/session1_session1_default.pdf' from calling fetch_ucsc.py with parameters "-r params/regions/session1.txt -t params/tracks_options/session1.txt".

Example:

::

    [session]
    UserName=ucscfetch
    UserSessionName=hg19SessionEx1


Look at params/tracks_options/default.txt for an example Regions file.

3. the Browser config file
---------------------------

The Browser config file contains the URL to the UCSC browser, your email
address, and options to set an HTTP Proxy.

You can change the UCSC URL to point to a custom UCSC browser installation, if
you have.

It is **important** to define an email address. This will be shown in the log
files of the UCSC server, and will be used by UCSC administrators in case they
need to contact you about usage policy. Be careful not to exceed with the
queries, as this may create problems to other users of the UCSC browser.

Example:

::

    [browser]
    ucsc_base_url = http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg18
    username =
    password =
    user-agent = Mechanize client to get screenshots from the UCSC browser. Home
    page: https://bitbucket.org/dalloliogm/ucsc-fetch
    email =
    httpproxy =
    httproxy_port =
    httproxy_password =

Look at params/browser_config/default.txt for an example Regions file.



REQUISITES
------------

You will need:

 * The python mechanize library http://wwwsearch.sourceforge.net/mechanize/
 * For the reports, you will need a tool to convert Restructured Text to PDF , e.g. rst2pdf (http://code.google.com/p/rst2pdf/ )
