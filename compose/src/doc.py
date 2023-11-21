#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================

# dependencies --- {{{
import json
from line import Line
# }}}

# Reminder:
#     Line(prefix, text, suffix='\n')
class Doc():
    """
    Loosely based on a linked list, which might be overdoing it,
    the idea is to be flexible about formatting (prefix, suffix of Line)
    while making it easier to capture content (text of Line)
    including tag(s), timeline for TODO items,
    and also maintaining structure/flow of daily note document

    if it turns out that self.next is not a useful attribute,
    and we are still only interested in inserting at the end of existing Doc,
    then maybe using index/size as self.end can achieve the same thing
    while preserving the flexible construction of the Doc
    """

    def __init__(self, prefix, text, path, from_md=False):
        self.head = Line(prefix=prefix, text=text)
        self.path = path
        self.filename = path[path.rfind('/'):path.rfind('.')]


    def __repr__(self):
        """
        assume this is about previewing the Doc object
        """
        cur_line = self.head
        comp = f"{cur_line}"
        if not cur_line.next: return comp
        while cur_line.next: 
            cur_line = cur_line.next
            comp += f"{cur_line}"
        return comp


    def __len__(self):
        size = 1
        cur_line = self.head
        if not cur_line.next: return size
        while cur_line.next:
            size += 1
            cur_line = cur_line.next
        return size


    def __dict__(self):
        out = {k:v for k,v in self.__dict__.items() if k != 'head'}
        out['lines'] = {0: self.head}
        cur_line = self.head
        for i in range(1, len(self)):
            cur_line = cur_line.next
            out['lines'][i] = {k:v for k,v in cur_line.__dict__.items() if k != 'next'}
            
        return 


    def insert(self, prefix, text):
        """
        insert at the end of the Doc
        """
        new_line = Line(prefix=prefix, text=text)
        cur_line = self.head
        while cur_line.next: cur_line = cur_line.next
        cur_line.next = new_line


    def to_json(fname, doc):

        return f'{fname} written successfully'
