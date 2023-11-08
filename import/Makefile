# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:#
# Authors:     BP
# Maintainers: BP
# Copyright:   2022, GPL v2 or later
# =========================================
# TODO-helper/import/Makefile

# ---- dependencies {{{
HERE := $(shell git rev-parse --show-toplevel)
demoin := $(HERE)/demo/hand/code-review.md
demodir := $(HERE)/demo/output

notedir := ~/git/my-TODO/individual
taskdir := ~/git/my-TODO/tasks
# }}}

# ---- standard {{{
.PHONY: all

all: import.done

# }}}

# ---- task-specific {{{
import.done: \
		src/import.py \
		$(notedir)
	-mkdir $(taskdir)
	python3 $< \
		--input=$(notedir) \
		--taskdir=$(taskdir)
    touch $@

demo.done: \
		src/import.py \
		$(demoin)
	-mkdir $(demodir)
	python3 $< \
		--input=$(demoin) \
		--taskdir=$(demodir)
    touch $@
# }}}
 
# done.
