# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:		 BP
# Maintainers: BP
# Copyright:	 2024, HRDAG, GPL v2 or later
# =========================================

shcript := output/get_summary.sh
summary := output/summary.json
output := output/summary.parquet
repodir := output/repos

.PHONY: all clean clones

all: $(output) # clones don't recommend doing this

clean:
	-rm -r output/*

$(shcript): \
	src/writecmd.py
	-mkdir output
	python $< \
		--org='HRDAG'\
		--json=$(summary)\
		--shcript=$@

$(summary): $(shcript)
	bash $(shcript)

$(output): \
	src/parse_summary.py \
	$(summary)
	python $< \
		--input=$(summary)\
		--output=$@

clones: \
	src/clone.py \
	$(output)
	python $< \
		--input=$(output)\
		--outdir=$(repodir)

# done.
