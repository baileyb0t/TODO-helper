# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================
# TODO-helper/import/Makefile

# ---- dependencies {{{
dailydir := $(HOME)/git/my-TODO/individual/daily
jsondir := $(HOME)/git/my-TODO/individual/daily/json
rules := hand/rules.yml
cal := frozen/Bailey_Passmore_m.bailey.passmore@gmail.com.ics

curdate := $(shell date '+%Y-%m-%d')
curjson := $(jsondir)/$(curdate).json
curmd := $(dailydir)/$(curdate).md
# }}}

# ---- standard {{{
.PHONY: all

all: $(curjson) $(curmd)

# }}}

# ---- task-specific {{{
$(curjson): \
		src/start-simple.py \
		$(rules) \
		$(dailydir)
	python3 $< \
		--rules=$(rules) \
		--date=$(curdate) \
		--outputdir=$(dailydir) \
		--output=$@

$(curmd): \
		src/add-scheduled-meetings.py \
		$(rules) \
		$(curjson) \
		$(cal)
	python3 $< \
		--rules=$(rules) \
		--json=$(curjson) \
		--ics=$(cal) \
		--output=$@
# }}}
 
# done.
