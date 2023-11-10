#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================

# dependencies --- {{{
from datetime import date
from Line import Line
# }}}

class Doc(object):

    def __init__(self, section='general', \
                 data=date.today().strftime('%A, %d %B %Y')):
        self.data = Line(section, data)
