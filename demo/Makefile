# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:#
# Authors:     BP
# Maintainers: BP
# Copyright:   2022, GPL v2 or later
# =========================================
# TODO-helper/import/Makefile

# ---- dependencies {{{
HERE := $(shell git rev-parse --show-toplevel)
input := $(HERE)/demo/hand/code-review.md
output := $(HERE)/demo/output/
# }}}

# ---- standard {{{
.PHONY: all clean sample_import sample_collect_active

all: sample_import sample_collect_active

clean: 
	-rm -r output/*
# }}}

# ---- task-specific {{{
sample_import: \
		$(HERE)/import/src/import.py \
		$(input)
	-mkdir output
	python3 $< \
		--input=$(input) \
		--output=$(output)
# }}}

sample_collect_active: \
		$(HERE)/review/src/collect_active.py \
		$(output)
	-mkdir output
	python3 $< \
		--input=$(output) \
		--output=$(output)active.parquet
# }}}
 
# done.
