MAIN    = main
TEXFILE = $(MAIN).tex
PDFFILE = $(MAIN).pdf
ARCHIVE = arxiv-submission.tar.gz

.PHONY: pdf clean arxiv-package

## Build the PDF (pdflatex + bibtex + pdflatex x2) and copy to repo root.
pdf: $(PDFFILE)
	cp $(PDFFILE) ../paper.pdf
	@echo "PDF written to ../paper.pdf"

$(PDFFILE): $(TEXFILE) bibliography.bib
	pdflatex -interaction=nonstopmode $(MAIN)
	bibtex $(MAIN)
	pdflatex -interaction=nonstopmode $(MAIN)
	pdflatex -interaction=nonstopmode $(MAIN)

## Remove all build artifacts (does NOT remove ../paper.pdf).
clean:
	rm -f *.aux *.log *.out *.toc *.synctex.gz *.fls *.fdb_latexmk \
	      *.bbl *.blg *.dvi *.lof *.lot *.idx *.ilg *.ind \
	      *.nav *.snm *.vrb *.bcf *.run.xml *-blx.bib
	rm -f $(PDFFILE)
	@echo "Build artifacts removed."

## Package source for arXiv submission.
## Includes main.tex, bibliography.bib, the pre-compiled main.bbl, and figures/.
## Bundling main.bbl is a safety net: arXiv's Submission 1.5 system normally
## runs BibTeX server-side, but shipping the resolved .bbl removes a class of
## failure modes (engine-version drift, missing .bst on the server, etc.).
arxiv-package: pdf
	tar -czf $(ARCHIVE) \
	    $(TEXFILE) \
	    bibliography.bib \
	    $(MAIN).bbl \
	    figures/
	@echo "arXiv submission package: $(ARCHIVE)"
	@echo "Contents:"
	@tar -tzf $(ARCHIVE) | sed 's/^/  /'

## Show available targets.
help:
	@echo "Targets:"
	@echo "  make pdf            Build PDF (runs pdflatex + bibtex cycle)"
	@echo "  make clean          Remove build artifacts"
	@echo "  make arxiv-package  Create arxiv-submission.tar.gz"
