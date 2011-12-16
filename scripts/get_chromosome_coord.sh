echo "SELECT chrom, size FROM chromInfo where chrom rlike 'chr[[:alnum:]]{1,2}$';" |mysql --user=genome -D hg18 --host=genome-mysql.cse.ucsc.edu -A| tail -n +2

# the following will be good for hg19
# echo "SELECT chrom, chromEnd FROM (SELECT * FROM gap ORDER BY chromEnd DESC) as t1 WHERE TYPE = 'telomere' GROUP BY chrom;" |mysql --user=genome -D hg19 --host=genome-mysql.cse.ucsc.edu -A| tail -n +2
