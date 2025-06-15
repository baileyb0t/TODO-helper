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
    parser.add_argument("--outall", default=None)
    parser.add_argument("--outrecent", default=None)
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
        elif dt > timestamps['today-30d']: info['ncommits_last_30d'] += 1
        elif dt > timestamps['today-6m']: info['ncommits_last_6m'] += 1
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


def formatlanguages(x):
    if x in [None, [None]]: return None
    return " | ".join([f"{llist[1]} ({llist[0]:,} bytes)" for llist in x])


def format_ncommitinfo(row):
    ncommits = f"N commits (last 7d | 30d | 6m | 1y): {row.ncommits_last_7d:.0f} | {
    row.ncommits_last_30d:.0f} | {row.ncommits_last_6m:.0f} | {row.ncommits_last_1y:.0f}"
    return ncommits


def formatsummary(row):
    base = f"""-----\n\n{row.title} ({row.disk_usage_KB})\t\t{row.stats}\n\n"""
    base += f"- {row.lifespan}\n"
    base += f"- {row.ncommits}\n"
    base += f"- {row.ncommits_authors}\n\n"
    #if row.description: base += f"{row.description}\n\n=====\n"
    return base


def unpacktext(proctext):
    issues = proctext.split('\n')
    nopen, nclosed = 0, 0
    opened_years = {}
    for iss in issues:
        if not iss: continue
        num, status, title, dt = iss.replace('\t\t', '\t').split('\t')
        if status == 'OPEN':
            nopen += 1
            year = dt[:4]
            if year not in opened_years.keys(): opened_years[year] = 1
            else: opened_years[year] += 1
    info = {'nopen': nopen, 'nclosed': nclosed, 'opened_years': opened_years}
    return info


def formatrecent(df):
    copy = df.copy()
    copy['title'] = copy.name.apply(lambda x: f"`{x}`")
    copy.disk_usage_KB = copy.disk_usage_KB.apply(lambda x: f"{x}KB")
    copy['stats'] = copy[['visibility', 'nwatchers', 'nstargazers']].apply(
        lambda row: f"{row.visibility.title()} | {row.nwatchers} 👀 | {row.nstargazers} ⭐️", axis=1)
    copy.languages = copy.languages.apply(formatlanguages)
    copy['lifespan'] = copy[['year_created', 'nyears_active']].apply(lambda row: f"Created: {
        row.year_created} | Years Active: {row.nyears_active}" if row.nyears_active > 0 else f"Created: {
        row.year_created} | Years Active: Less than 1", axis=1)
    copy['ncommits'] = copy[[c for c in copy.columns if 'ncommits_last' in c]].apply(
        lambda row: format_ncommitinfo(row=row), axis=1)
    copy.ncommits_authors = copy.ncommits_authors.apply(
        lambda x: " | ".join([f"{v} commits by {k}" for k,v in x.items()]))
    strcols = [
        'title', 'disk_usage_KB', 'stats',
        'languages', 'lifespan', 'description',
        'ncommits', 'ncommits_authors']
    less = copy[strcols].copy()
    less['formatted'] = less.apply(formatsummary, axis=1)
    return less
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

    both['nyears_active'] = both.yearlast - both.year_created
    both['recently_active'] = both.ncommits_last_6m.notna()
    origcols = both.columns

    logger.info('formatting for report')
    recent = both.loc[both.recently_active]
    recent = formatrecent(df=recent)

    logger.info('writing update repo summary data')
    os.chdir(owd)
    both[origcols].to_parquet(args.outall)
    recent.to_parquet(args.outrecent)

    logger.info('done')
# }}}

# done.
