#!/usr/bin/env python
"""
Get chromosome coordinates from UCSC tables

Usage:
    python get_gene_coords.py genelist.txt

genelist.txt is a file containing a list of Gene Ids to be retrieved, one per line.

Reference: http://biostar.stackexchange.com/questions/3121/genomic-cordinates-from-ucsc
"""

import subprocess
import sys

# READING GENE LIST FILE
try:
    genelist_path = sys.argv[1]
    genelist_h = open(genelist_path, 'r')
except:
    print __doc__
    sys.exit("invalid file")

genelist = genelist_h.read().split()
print genelist



# QUERYING UCSC
genelist_str = '("' + '", "'.join(genelist) + '")'
command = """mysql  -h  genome-mysql.cse.ucsc.edu -A -u genome -D hg18 -e 'select distinct X.geneSymbol,G.chrom,G.txStart,G.txEnd from knownGene as G, kgXref as X where X.geneSymbol in %s and X.kgId=G.name ' """ % genelist_str



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
    print start < end
    if not all_genes.has_key(gene):
        all_genes[gene] = [gene, chrom, start, end]
    else:
        if start < all_genes[gene][2]:
            print gene, "(start)", start, all_genes[gene][2]
            all_genes[gene][2] = start

        if end > all_genes[gene][3]:
            print gene, "(end)", end, all_genes[gene][3]
            all_genes[gene][3] = end



# PRINTING OUTPUT

for (gene, values) in all_genes.items():
    print "%s\tHuman\thg18\t%s\t%s\t%s\t10000\t10000" % tuple(values)




if __name__ == '__main__':
    pass

