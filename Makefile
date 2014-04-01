# define your own email address in a browser_config file first
sessionEx1:
	python fetch_ucsc.py -r params/regions/session1.txt -t params/tracks_options/session1.txt -u params/browser_config/default.txt

test:
	python fetch_ucsc.py -r params/regions/default.txt -t params/tracks_options/default.txt -u params/browser_config/default.txt

# NOTE: the following uses a custom browser configuration file that is not included in the repository. This is how I debug the script from my personal computer; but if you want to use these scripts you should define your own email address in a browser_config file.
example1:
	python fetch_ucsc.py -r params/regions/example1.txt -t params/tracks_options/example1.txt -u params/browser_config/exampleconfig.txt -l 6x2 --title example1 -s 
example2:
	python fetch_ucsc.py -r params/regions/example2.txt -t params/tracks_options/example2.txt -u params/browser_config/exampleconfig.txt -l 6x2 --title example2 -s 
drosophila_example:
	python fetch_ucsc.py -r params/regions/drosophila1.txt -t params/tracks_options/drosophila1.txt -u params/browser_config/drosophila.txt -l 6x2 --title drosophila_example1 -s
ibe:
	ipython fetch_ucsc.py -- -s -l2x2 -r params/regions/ibe.txt -t params/tracks_options/ibe.txt -u params/browser_config/ibe.txt

results/chr1.pdf: params/tracks_options/ibe.txt params/regions/all_chromosomes_hg18.txt
	python fetch_ucsc.py -r params/regions/all_chromosomes_hg18.txt -t params/tracks_options/ibe.txt -u params/browser_config/ibe.txt

genotype_space:
	python fetch_ucsc.py -r params/regions/all_chromosomes_hg19.txt -t params/tracks_options/genotype_space.txt -u params/browser_config/genotypespace_ibe.txt -l 1x1  -s


#all_chromosomes_report:
#	python fetch_ucsc.py -r params/regions/all_chromosomes_hg18.txt -t params/tracks_options/default.txt -u params/browser_config/default.txt
CHROMOSOMES = 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 X Y M

all_chromosomes_report: results/all_chromosomes_report.pdf
results/all_chromosomes_report.pdf: results/chr1.pdf
	pdftk $(addprefix results/chr, $(addsuffix .pdf, $(CHROMOSOMES))) cat output results/all_chromosomes_1p.pdf
	python scripts/pdfpages.py results/all_chromosomes_1p.pdf -n2x2
	mv all_chromosomes_1p-pdf-pages.pdf results/all_chromosomes_report.pdf
	rm results/all_chromosomes_1p.pdf
