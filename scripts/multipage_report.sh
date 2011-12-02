#!/usr/bin/env bash
# Wrapper that uses pdftk and pdfpages.py to convert all the pdf files in a folder to a 2x2 pages report
#
# Usage: 
#   $: bash multipage_report.sh inputfolder outputfilename


INPUTFOLDER=$1
OUTPUTFILE=$2

echo pdftk ${INPUTFOLDER}/*.pdf cat output ${OUTPUTFILE}_tmp.pdf
pdftk ${INPUTFOLDER}/*.pdf cat output ${OUTPUTFILE}_tmp.pdf
echo python pdfpages.py ${OUTPUTFILE}_tmp.pdf -n2x2
python pdfpages.py ${OUTPUTFILE}_tmp.pdf -n2x2
mv ${OUTPUTFILE}_tmp-pdf-pages.pdf $2.pdf
