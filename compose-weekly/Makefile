# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================
# TODO-helper/import/Makefile

# ---- dependencies {{{
weeklydir := $(HOME)/git/my-TODO/individual/weekly
jsondir := $(HOME)/git/my-TODO/individual/weekly/json
rules := hand/rules.yml
cal := ../calendar/output/mpb.ics

curdate := $(shell date '+%Y-%m-%d')
basejson := $(jsondir)/$(curdate)-base.json
curjson := $(jsondir)/$(curdate).json
curmd := $(weeklydir)/$(curdate).md
# }}}

# ---- standard {{{
.PHONY: all

all: $(curmd)

# }}}

# ---- task-specific {{{
$(basejson): \
		src/start-simple.py \
		$(rules) \
		$(dailydir)
	python3 $< \
		--rules=$(rules) \
		--date=$(curdate) \
		--outputdir=$(dailydir) \
		--output=$@

$(curjson): \
		src/add-scheduled-meetings.py \
		$(rules) \
		$(basejson) \
		$(cal)
	python3 $< \
		--rules=$(rules) \
		--json=$(basejson) \
		--ics=$(cal) \
		--output=$@

$(curmd): \
		src/add-repo-activity.py \
		$(rules) \
		$(curjson) \
		$(cal)
	python3 $< \
		--rules=$(rules) \
		--injson=$(curjson) \
		--ics=$(cal) \
		--outjson=$(curjson) \
		--outmd=$@
	rm $(basejson)
# }}}

# done.
