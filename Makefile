test:
	python fetch_ucsc.py -r params/regions/default.txt -t params/tracks_options/default.txt -u params/browser_config/default.txt

ibe:
	ipython fetch_ucsc.py -- -s -l2x2 -r params/regions/ibe.txt -t params/tracks_options/ibe.txt -u params/browser_config/ibe.txt

results/chr1.pdf: params/tracks_options/ibe.txt params/regions/all_chromosomes_hg18.txt
	python fetch_ucsc.py -r params/regions/all_chromosomes_hg18.txt -t params/tracks_options/ibe.txt -u params/browser_config/ibe.txt


#all_chromosomes_report:
#	python fetch_ucsc.py -r params/regions/all_chromosomes_hg18.txt -t params/tracks_options/default.txt -u params/browser_config/default.txt
CHROMOSOMES = 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 X Y M

all_chromosomes_report: results/all_chromosomes_report.pdf
results/all_chromosomes_report.pdf: results/chr1.pdf
	pdftk $(addprefix results/chr, $(addsuffix .pdf, $(CHROMOSOMES))) cat output results/all_chromosomes_1p.pdf
	python scripts/pdfpages.py results/all_chromosomes_1p.pdf -n2x2
	mv all_chromosomes_1p-pdf-pages.pdf results/all_chromosomes_report.pdf
	rm results/all_chromosomes_1p.pdf
