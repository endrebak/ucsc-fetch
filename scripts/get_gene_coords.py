#!/usr/bin/env python
"""
Get chromosome coordinates from UCSC tables

Usage:
    python get_gene_coords.py -l genelist.txt -d hg19

genelist.txt is a file containing a list of Gene Ids to be retrieved, one per line.

Reference: http://biostar.stackexchange.com/questions/3121/genomic-cordinates-from-ucsc
"""

import subprocess
import sys
import logging
import optparse
logging.basicConfig(level=logging.DEBUG)

def get_options():
    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option('-l', '-g', '-f', '--list', '--list_of_genes', '--genes', dest='genes', 
            help='file containing the list of gene. One symbol per line', default=False)
    parser.add_option('-d', '--database', dest='database',
            help='database version (e.g. hg18 or hg19). Default: hg19', default='hg19')
    (options, args) = parser.parse_args()
    
    if options.genes == '':
        parser.print_help()
        parser.error('get_gene_coords.py: genes file not defined.')

    try:
        genelist_path = options.genes
        genelist_h = open(genelist_path, 'r')
    except:
        print __doc__
        parser.error("Can not open genes file")

    genelist = genelist_h.read().split()
    logging.debug(genelist)

    return (genelist, options.database)

# READING GENE LIST FILE

def query_ucsc(genelist, database):
    """
    Query UCSC MySQL database to get coordinates of a list of genes.

    Print results to STDOUT
    """
    # QUERYING UCSC
    genelist_str = '("' + '", "'.join(genelist) + '")'
    #command = """mysql  -h  genome-mysql.cse.ucsc.edu -A -u genome -D hg18 -e 'select distinct X.geneSymbol,G.chrom,G.txStart,G.txEnd from knownGene as G, kgXref as X where X.geneSymbol in %s and X.kgId=G.name ' """ % genelist_str
    #command = """mysql  -h  genome-mysql.cse.ucsc.edu -A -u genome -D hg19 -e 'select distinct X.geneSymbol,G.chrom,G.txStart,G.txEnd from knownGene as G, kgXref as X where X.geneSymbol in %s and X.kgId=G.name ' """ % genelist_str
    command = """mysql  -h  genome-mysql.cse.ucsc.edu -A -u genome -D %s -e 'select distinct X.geneSymbol,G.chrom,G.txStart,G.txEnd from knownGene as G, kgXref as X where X.geneSymbol in %s and X.kgId=G.name ' """ % (database, genelist_str)
    logging.debug(command)


    # PARSING RESULTS to remove redundant entries (TODO: use Mysql function)

    # I don't have a recent version of the subprocess installed, so I don't have subprocess.check_output
    temp_output_h = open("temp_output.txt", "w")
    subprocess.check_call(command, shell=True, stdout=temp_output_h)
    temp_output_h.close()


    temp_output_h = open("temp_output.txt", "r")
    temp_output_h.seek(0)
    temp_output_h.readline()

    all_genes = {}
    for line in temp_output_h:
        (gene, chrom, start, end) = line.split()
        start = int(start)
        end = int(end)
        logging.debug(start < end)
        if not all_genes.has_key(gene):
            all_genes[gene] = [gene, chrom, start, end]
        else:
            if start < all_genes[gene][2]:
                logging.debug((gene, "(start)", start, all_genes[gene][2]))
                all_genes[gene][2] = start

            if end > all_genes[gene][3]:
                logging.debug((gene, "(end)", end, all_genes[gene][3]))
                all_genes[gene][3] = end

    # PRINTING OUTPUT

    for (gene, values) in all_genes.items():
        print '%s,Human,hg18,%s,%s,%s,"",10000,10000' % tuple(values)


def main():
    (genelist, database) = get_options()
    print genelist, database
    query_ucsc(genelist, database)

if __name__ == '__main__':
    main()

