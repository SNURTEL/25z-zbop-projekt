MAIN    ?= main
TEXSRC  := $(MAIN).tex $(wildcard tex/*.tex)
OUTDIR  ?= .

.PHONY: all pdf clean clean-all

all: pdf

pdf: $(MAIN).pdf

$(MAIN).pdf: $(TEXSRC)
	latexmk -synctex=1 -interaction=nonstopmode -file-line-error -shell-escape -lualatex -outdir=$(OUTDIR) $(MAIN).tex
	latexmk -synctex=1 -interaction=nonstopmode -file-line-error -shell-escape -lualatex -outdir=$(OUTDIR) $(MAIN).tex

clean:
	latexmk -C -outdir=$(OUTDIR)
	$(RM) $(MAIN).run.xml $(MAIN).bcf $(MAIN).tdo

clean-all: clean
	$(RM) $(MAIN).pdf
