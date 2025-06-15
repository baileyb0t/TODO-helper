#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
from pathlib import Path
from sys import stdout
import argparse
from loguru import logger
from datetime import date, datetime
from dateutil.relativedelta import *
import pandas as pd
#}}}

# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.input).exists()
    return args


def setuplogging(logfile):
    logger.add(logfile,
               colorize=True,
               format="<green>{time:YYYY-MM-DD⋅at⋅HH:mm:ss}</green>⋅<level>{message}</level>",
               level="INFO")
    return 1


def reformatlangs(x):
    assert type(x) == list
    if not any(x): return None
    formatted = []
    for langdict in x:
        if pd.isna(langdict['size']): continue
        # docs aren't super clear about the units of the reported fields
        # but from SO posts it seems like this 'size' is probably in bytes
        info = (langdict['size'], langdict['node']['name'])
        formatted.append(info)
    if len(formatted) == 0: return None
    return formatted


def setupjson(jsonfile):
    repos = pd.read_json(jsonfile)
    repos.createdAt = pd.to_datetime(repos.createdAt)
    repos.updatedAt = pd.to_datetime(repos.updatedAt)
    repos['year_created'] = repos.createdAt.dt.year
    repos.primaryLanguage = repos.primaryLanguage.apply(lambda x: x['name'] if x else None)
    repos.languages = repos.languages.apply(reformatlangs)
    repos.issues = repos.issues.apply(lambda x: x['totalCount'])
    repos.pullRequests = repos.pullRequests.apply(lambda x: x['totalCount'])
    repos.watchers = repos.watchers.apply(lambda x: x['totalCount'])
    repos.description = repos.description.replace('', None)
    repos.rename(columns={
        'issues': 'nissues',
        'pullRequests': 'npullRequests',
        'stargazerCount': 'nstargazers',
        'watchers': 'nwatchers',
        'diskUsage': 'disk_usage_KB',
        'sshUrl': 'sshurl',
        }, inplace=True)
    return repos
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    setuplogging("output/parse_summary.log")
    repos = setupjson(jsonfile=args.input)
    less = repos[[
        'year_created', 'name', 'updatedAt',
        'visibility', 'isPrivate', 'isArchived', 'isEmpty',
        'nwatchers', 'nstargazers',
        'languages', 'disk_usage_KB',
        'sshurl',
        'description',
        ]].sort_values([
        'year_created', 'updatedAt',
        ], ascending=False).reset_index(drop=True)
    less.to_parquet(args.output)
    logger.info('done')
# }}}

# done.
