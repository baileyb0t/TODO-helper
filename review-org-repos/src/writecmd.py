#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
import argparse
#}}}

SELECTED = [
'archivedAt',
'createdAt',
'description',
'diskUsage',
'id',
'isArchived',
'isEmpty',
'isPrivate',
'issues',
'languages',
'name',
'primaryLanguage',
'pullRequests',
'pushedAt',
'sshUrl',
'stargazerCount',
'updatedAt',
'url',
'visibility',
'watchers',
]

# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", default='HRDAG')
    parser.add_argument("--shcript", default='get_summary.sh')
    parser.add_argument("--jsonfile", default='summary.json')
    args = parser.parse_args()
    return args


def writesh(fname, data):
    with open(fname, 'w') as f:
        f.write(data)
        f.close()
    return 1
#}}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    tracking = ",".join(SELECTED)
    cmd = ['gh', 'repo' , 'list',
           args.org, '-L', '100',
           '--json', tracking,
           '>', args.jsonfile]
    cmd = " ".join(cmd)
    assert writesh(fname=args.shcript, data=cmd)
# }}}

# done.
