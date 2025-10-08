#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================

# dependencies --- {{{
from os import listdir, path
from pathlib import Path
from sys import stdout
import argparse
import logging
import yaml
from pytz import timezone
from datetime import date, datetime
from dateutil.relativedelta import *
import pandas as pd
import git
import re
import doc

PACIFIC = timezone('US/Pacific')

ALT_AUTHORNAMES = (
    'bp', 'bailey', 'baileyb0t',
)
# }}}

# support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", default="hand/rules.yml")
    parser.add_argument("--injson", default=None)
    parser.add_argument("--ics", default="../calendar/output/mbp.ics")
    parser.add_argument("--outjson", default=None)
    parser.add_argument("--outmd", default=None)
    parser.add_argument("--outchanges", default=None)
    args = parser.parse_args()
    assert Path(args.rules).exists()
    assert Path(args.injson).exists()
    assert Path(args.ics).exists()
    return args


def get_logger(sname, file_name=None):
    logger = logging.getLogger(sname)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s " +
                                  "- %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    stream_handler = logging.StreamHandler(stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def read_yaml(fname):
    with open(fname, 'r') as f:
        rules = yaml.safe_load(f)
        f.close()
    return rules


def findrepos(gitdir):
    gitdir = path.expanduser(gitdir)
    info = {}
    for dirname in listdir(gitdir):
        dirpath = f"{gitdir}/{dirname}"
        if Path(f"{dirpath}/.git").exists(): info[dirname] = {'path': dirpath}
    assert info
    return info


def checkrepos(info):
    newinfo = info
    for reponame, repoinfo in info.items():
        repo = git.Repo(repoinfo['path'])
        newinfo[reponame]['dirty'] = repo.is_dirty()
        newinfo[reponame]['untracked'] = [
            f for f in repo.untracked_files if 'checkpoint' not in f]
    assert newinfo
    return newinfo


def recentcommits_byauthor(info, sdate, edate, author):
    """Authored datetime is preserved on rebase, and
    we want to include commits from this week that might have been rebasing an earlier commit."""
    newinfo = info
    for reponame, repoinfo in info.items():
        repo = git.Repo(repoinfo['path'])
        if author: newinfo[reponame]['n_other_recent'] = 0
        commits = []
        nother = 0
        for commit in repo.iter_commits():
            committed = PACIFIC.localize(datetime.fromtimestamp(commit.committed_date))
            if (committed <= edate) & (committed >= sdate):
                if any([authorname.lower() in str(commit.author).lower()
                        for authorname in ALT_AUTHORNAMES]):
                    commits.append(commit)
                else: newinfo[reponame]['n_other_recent'] += 1
        newinfo[reponame]['recent'] = commits
    assert newinfo
    return newinfo


def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))


def formatreponame(reponame, fixedwidth):
    formatted = '+-' + '-' * fixedwidth + '-+\n'
    for line in chunkstring(string=reponame, length=fixedwidth):
        formatted += '| {0:^{1}} |'.format(line, fixedwidth)
    formatted += '\n+-' + '-'*(fixedwidth) + '-+\n'
    return formatted


def formatmessage(msg):
    """I want the first word of the commit message to be title-cased, but not the rest of the message."""
    chunks = msg.strip().split()
    titled = chunks[0].title() + ' ' + ' '.join(chunks[1:])
    if titled[-1] != ".": titled += "."
    return titled


def summarize(reponame, commits):
    if not any(commits): return ""
    summary = ""
    for commit in commits:
        commitdt = PACIFIC.localize(datetime.fromtimestamp(commit.committed_date)).strftime("%a %d %b")
        nchanges = commit.stats.total
        if commitdt not in summary: summary += f"\n_Committed: {commitdt}_\n"
        overview = f"* [{commit.hexsha[:8]}]: {formatmessage(msg=commit.message)}"
        overview += f" // Involves {nchanges['files']} file(s), {nchanges['lines']} lines\n"
        summary += overview
    return summary


def recentcommits(info, sdate, edate):
    """Authored datetime is preserved on rebase, and
    we want to include commits from this week that might have been rebasing an earlier commit."""
    breakdown = []
    noupdates = []
    for reponame, repoinfo in info.items():
        repo = git.Repo(repoinfo['path'])
        commits = []
        nother = 0
        for commit in repo.iter_commits():
            commitdt = PACIFIC.localize(datetime.fromtimestamp(commit.committed_date))
            if (commitdt > edate) | (commitdt < sdate): continue
            info = {
                'repo': reponame,
                'commit_hash8': commit.hexsha[:8],
                'date': commitdt,
                'author': str(commit.author),
                'n_files': commit.stats.total['files'],
                'n_lines': commit.stats.total['lines'],
                'msg': formatmessage(msg=commit.message),
            }
            commits.append(info)
        if not any(commits): noupdates.append(reponame)
        else: breakdown += commits
    out = pd.DataFrame(breakdown)
    return out, noupdates


def summarizerecent(changes):
    summaries = []
    for repo in changes.repo.unique():
        header = formatreponame(reponame=f"`{repo}`", fixedwidth=35)
        summaries.append(header)
        repochanges = changes.loc[changes.repo == repo]
        for author in sorted(repochanges.author.unique()):
            authored = repochanges.loc[repochanges.author == author]
            authorsummary = f"""**{author}**: {
                authored.shape[0]:,} commit(s) // {
                authored.n_files.sum():,} file change(s) // {
                authored.n_lines.sum():,} line change(s).\n"""
            summaries.append(authorsummary)
    return "\n".join(summaries) + "\n"
# }}}

# main --- {{{
if __name__ == '__main__':
    logger = get_logger(__name__, "output/add-scheduled-meetings.log")
    args = get_args()

    rules = read_yaml(args.rules)
    formats = rules['format']
    notes = doc.from_json(args.injson)

    base = findrepos(gitdir="~/git")
    base = checkrepos(info=base)

    end_prevmo = PACIFIC.localize(
        datetime.now().replace(day=1) - relativedelta(days=1))
    e = (end_prevmo
        ).replace(hour=23, minute=59, second=59)
    s = (e - relativedelta(months=+2)
        ).replace(day=1, hour=0, minute=0, second=0)

    logger.info(f'processing activity between {s} and {e}')
    changes, noupdates = recentcommits(info=base, sdate=s, edate=e)

    # optional filtering
    hasauthor = changes.loc[changes.author.str.lower().isin(
        ALT_AUTHORNAMES), 'repo'].unique()

    summary = summarizerecent(changes)
    logger.info('formatting information about quiet repos')
    summary += formatreponame(reponame=f"**quiet** repositories", fixedwidth=25)
    for reponame in sorted(noupdates): summary += f"- {reponame}\n"
    summary = summary + "\n"

    notes.insert(prefix=formats['header'], text='Repo activity')
    notes.insert(prefix=formats['text'], text=summary)

    notes.to_json(args.outjson)
    notes.to_md(args.outmd)
    changes.to_csv(args.outchanges, index=False)
# }}}
