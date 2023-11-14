#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================

class Line:
    def __init__(self, prefix, text, suffix='\n'):
        self.prefix = prefix                    # ie. '# '
        self.text = text                        # ie. 'Meetings'
        self.suffix = suffix
        self.next = None

    def __str__(self):
        """
        string representation of a Line
        for use in notes section
        where meetings and tasks are subheader lines
        """
        return f'{self.prefix}{self.text}{self.suffix}'

    def __repr__(self):
        """
        string-like representation of a Line
        for use when it is necessary to preserve or encode all info in object
        reverse of repr() is eval()
        """
        return f'Line({self.prefix}, {self.text}, {self.suffix})'


