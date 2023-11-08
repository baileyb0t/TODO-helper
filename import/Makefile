# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================
# TODO-helper/import/Makefile

# ---- dependencies {{{
HERE := $(shell git rev-parse --show-toplevel)
demoin := $(HERE)/demo/hand/code-review.md
demodir := $(HERE)/demo/output
demo := $(demodir)/demo.done

notedir := ~/git/my-TODO/individual
taskdir := ~/git/my-TODO/tasks
import := $(taskdir)/import.done
# }}}

# ---- standard {{{
.PHONY: all

all: $(import)

# }}}

# ---- task-specific {{{
$(import): \
		src/import.py \
		$(notedir)
	-mkdir $(taskdir)
	python3 $< \
		--input=$(notedir) \
		--taskdir=$(taskdir)
	touch $@

$(demo): \
		src/import.py \
		$(demoin)
	-mkdir $(demodir)
	python3 $< \
		--input=$(demoin) \
		--taskdir=$(demodir)
	touch $@
# }}}
 
# done.
