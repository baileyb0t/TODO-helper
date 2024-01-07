# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================

icskey := ${HOME}/git/dotfiles/creds/google-cal-secret
ics := output/mpb.ics

.PHONY: all clean

all: $(ics)

clean:
	-rm -r output/*

$(ics): \
	src/getics.py \
	$(icskey)
	-mkdir output
	python3 $< \
		--creds=$(icskey) \
		--output=$@
