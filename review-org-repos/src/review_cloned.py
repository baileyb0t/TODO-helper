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
import os
from datetime import datetime
from dateutil.relativedelta import *
import git
import pandas as pd
#}}}

# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--repodir", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.input).exists()
    assert Path(args.repodir).exists()
    return args


def setuplogging(logfile):
    logger.add(logfile,
               colorize=True,
               format="<green>{time:YYYY-MM-DD⋅at⋅HH:mm:ss}</green>⋅<level>{message}</level>",
               level="INFO")
    return 1


def setupwindows(infodict, tzaware):
    infodict['today-7d'] = tzaware - relativedelta(days=+7)
    infodict['today-30d'] = tzaware - relativedelta(days=+30)
    infodict['today-6m'] = tzaware - relativedelta(months=+6)
    infodict['today-1y'] = tzaware - relativedelta(years=+1)
    return infodict


def getcommits(repo, nrecent):
    """{nrecent} can be None to return all commits in history."""
    return [commit for commit in repo.iter_commits()][:nrecent]


def getcommitinfo(commit):
    tzaware = commit.committed_date + commit.committer_tz_offset
    commit_dt = datetime.fromtimestamp(tzaware)
    author = f"{commit.author.name} <{commit.author.email}>"
    return (commit_dt, author)


def getlastinfo(repo):
    lastcommit = repo.commit()
    return getcommitinfo(lastcommit)


def getnrecentinfo(repo, timestamps, info, nrecent=None):
    info['ncommits_last_7d'] = 0
    info['ncommits_last_30d'] = 0
    info['ncommits_last_6m'] = 0
    info['ncommits_last_1y'] = 0
    commits = getcommits(repo=repo, nrecent=nrecent)
    info['ncommits_authors'] = {}
    for commit in commits:
        (dt, author) = getcommitinfo(commit=commit)
        if dt > timestamps['today-7d']: info['ncommits_last_7d'] += 1
        if dt > timestamps['today-30d']: info['ncommits_last_30d'] += 1
        if dt > timestamps['today-6m']: info['ncommits_last_6m'] += 1
        else: info['ncommits_last_1y'] += 1
        if author not in info['ncommits_authors'].keys(): info['ncommits_authors'][author] = 1
        else: info['ncommits_authors'][author] += 1
    return info


def getreposummary(name, timestamps, nrecent):
    logger.info(f'summarizing: `{name}`')
    repo = git.Repo(name) # Need to be in the directory with the repo or pass the Path to it
    (lastdt,lastauthor) = getlastinfo(repo=repo)
    summary = {
        'name': name,
        'yearlast': lastdt.year,
        'agelast': timestamps['today'] - lastdt,
    }
    if summary['agelast'].days < 30:
        summary = getnrecentinfo(
            repo=repo,
            timestamps=timestamps,
            info=summary,
            nrecent=nrecent
        )
    return summary
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    setuplogging("output/review_cloned.log")

    logger.info('setting up before review')
    less = pd.read_parquet(args.input)
    assert 'name' in less.columns, f"\
    Expecting to find `name` field in data, but found {less.columns}."
    timestamps = {'today': datetime.now()}
    timestamps = setupwindows(infodict=timestamps, tzaware=timestamps['today'])
    owd = os.getcwd()
    os.chdir(args.repodir)

    logger.info(f'begin summarizing repos in {args.repodir}')
    summaries = [
        getreposummary(name=reponame, timestamps=timestamps, nrecent=100)
        for reponame in less.name.values]
    summarydf = pd.DataFrame(summaries)
    both = pd.merge(less, summarydf, on='name')

    logger.info('writing update repo summary data')
    os.chdir(owd)
    both.to_parquet(args.output)

    logger.info('done')
# }}}

# done.
