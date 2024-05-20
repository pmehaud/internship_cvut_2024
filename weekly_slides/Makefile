LATEX_CMD=pdflatex

all: main.pdf

pdf: main.pdf

main.pdf: clean main.tex
	$(LATEX_CMD) main
	# make clean

clean:
	rm -f *.ps *.dvi *.aux *.toc *.idx *.ind *.ilg *.log *.out *.brf *.blg *.bbl main.pdf # *.snm *.nav