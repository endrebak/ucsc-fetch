# source: http://biostar.stackexchange.com/questions/6149/batch-viewing-of-ucsc-browser-graphic/6155#6155

screenshotUCSC <- function(url, trackfile, chr, start, end, filename) {
        oldpen <- options("scipen")
        options(scipen=100)
        print(paste(url, "&hgt.customText=", trackfile, "&position=",chr,":",start,"-",end, sep=""))
        temp <- readLines(paste(url, "&hgt.customText=", trackfile, "&position=",chr,":",start,"-",end, sep=""))
        print(temp)
        pdfurl <- paste("http://genome.ucsc.edu/trash",gsub(".*trash","",gsub(".pdf.*","",temp[grep(".pdf", temp, fixed=TRUE)])), ".pdf", sep="")
        print(pdfurl)
        options(scipen=oldpen)
        download.file(pdfurl, filename, mode="wb", quiet=TRUE)  
}

library(multicore)
#mclapply(1:nrow(toPlot), function(i) screenshotUCSC("http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg18&wgRna=hide&cpgIslandExt=pack&ensGene=hide&mrna=hide&intronEst=hide&mgcGenes=hide&hgt.psOutput=on&cons44way=hide&snp130=hide&snpArray=hide&wgEncodeReg=hide&pix=1000&refGene=pack&knownGene=hide&rmsk=hide","URL_of_your_custom_track", toPlot$space[i], toPlot$start[i]-3000, toPlot$start[i]+2999, paste("Figures/Shots/Low_To_High_", i, ".pdf", sep="")), mc.cores=10)

screenshotUCSC("http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg18&wgRna=hide&cpgIslandExt=pack&ensGene=hide&mrna=hide&intronEst=hide&mgcGenes=hide&hgt.psOutput=on&cons44way=hide&snp130=hide&snpArray=hide&wgEncodeReg=hide&pix=1000&refGene=pack&knownGene=hide&rmsk=hide", "trackfile", "chr1", 100, 200, "ucsc_screenshot.pdf")
