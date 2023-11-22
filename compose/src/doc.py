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

    def __init__(self, prefix, text, path, dailyday=False, suffix='\n',):
        self.head = Line(prefix=prefix, text=text, suffix=suffix)
        self.path = path
        self.filename = path[path.rfind('/'):]
        self.dailyday = dailyday


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


    def insert(self, prefix, text, suffix='\n'):
        """
        insert at the end of the Doc
        """
        new_line = Line(prefix=prefix, text=text, suffix=suffix)
        cur_line = self.head
        while cur_line.next: cur_line = cur_line.next
        cur_line.next = new_line
        return 1

    
    def to_dict(self):
        out = {tup[0]:tup[1] for tup in self.__dict__.items() 
               if ('head' not in tup[0]) & ('file' not in tup[0])}
        out['lines'] = {"0": {tup[0]:tup[1] for tup in self.head.__dict__.items()
                            if tup[0] != 'next'}}
        cur_line = self.head
        for i in range(1, len(self)):
            cur_line = cur_line.next
            out['lines'][str(i)] = {tup[0]:tup[1] for tup in cur_line.__dict__.items() 
                               if tup[0] != 'next'}
        return out


    def to_json(self, jsonfile):
        json_data = json.dumps(self.to_dict(), sort_keys=True, indent=4)
        with open(jsonfile, 'w') as f:
            f.write(json_data)
            f.close()
        return f'{jsonfile} written successfully'
    
    
    def to_md(self, mdfile):
        with open(mdfile, 'w') as f:
            f.write(self.__repr__())
            f.close()
        return 1
    
    
def read_json(jsonfile):
    with open(jsonfile, 'r') as f:
        data = json.load(f)
    return data


def from_json(jsonfile):
    json_data = read_json(jsonfile)
    n_lines = max([int(k) for k in json_data['lines'].keys()])
    head_data = json_data['lines']['0']
    self = Doc(prefix=head_data['prefix'], 
               text=head_data['text'], 
               suffix=head_data['suffix'], 
               path=json_data['path'], 
               dailyday=json_data['dailyday'])
    for i in range(1, n_lines+1):
        line_data = json_data['lines'][str(i)]
        self.insert(prefix=line_data['prefix'], 
                    text=line_data['text'], 
                    suffix=line_data['suffix'])
    return self