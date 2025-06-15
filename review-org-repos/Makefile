# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:		 BP
# Maintainers: BP
# Copyright:	 2024, HRDAG, GPL v2 or later
# =========================================

shcript := output/get_summary.sh
json := output/summary.json
summary := output/summary_base.parquet
repodir := output/repos
output := output/summary.parquet

.PHONY: all clean clones

all: $(output)

#clean:
#	-rm -r output/*

$(shcript): \
	src/writecmd.py
	-mkdir output
	python $< \
		--org='HRDAG'\
		--json=$(json)\
		--shcript=$@

$(json): $(shcript)
	bash $(shcript)

$(summary): \
	src/parse_summary.py \
	$(json)
	python $< \
		--input=$(json)\
		--output=$@

clones: \
	src/clone.py \
	$(summary)
	python $< \
		--input=$(summary)\
		--outdir=$(repodir)

$(output): \
	src/review_cloned.py \
	$(summary)
	python $< \
		--input=$(summary)\
		--repodir=$(repodir)\
		--output=$@

# done.
