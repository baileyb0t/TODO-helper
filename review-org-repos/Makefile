# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:		 BP
# Maintainers: BP
# Copyright:	 2024, HRDAG, GPL v2 or later
# =========================================

shcript := output/get_summary.sh
json := output/base.json
base := output/base.parquet
repodir := output/repos
outall := output/summary_all.parquet
outrecent := output/summary_recent.parquet

.PHONY: all clean clones

all: $(outrecent)

clean:
	-rm $(shcript)
	-rm $(json)
	-rm $(base)
	-rm $(outall)
	-rm $(outrecent)

$(shcript): \
	src/writecmd.py
	-mkdir output
	python $< \
		--org='HRDAG'\
		--json=$(json)\
		--shcript=$@

$(json): $(shcript)
	bash $(shcript)

$(base): \
	src/parse_summary.py \
	$(json)
	python $< \
		--input=$(json)\
		--output=$@

clones: \
	src/clone.py \
	$(base)
	python $< \
		--input=$(base)\
		--outdir=$(repodir)

$(outrecent): \
	src/review_cloned.py \
	$(base)
	python $< \
		--input=$(base)\
		--repodir=$(repodir)\
		--outall=$(outall)\
		--outrecent=$@

# done.
