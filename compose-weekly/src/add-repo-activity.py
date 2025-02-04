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
from datetime import date, datetime
from dateutil.relativedelta import *
import git
import re
import doc
# }}}

# support methods {{{
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", default="hand/rules.yml")
    parser.add_argument("--injson", default=None)
    parser.add_argument("--ics", default="../calendar/output/mbp.ics")
    parser.add_argument("--outjson", default=None)
    parser.add_argument("--outmd", default=None)
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


def recentcommits(info, sdate, edate, author=None):
    """Authored datetime is preserved on rebase, and
    we want to include commits from this week that might have been rebasing an earlier commit."""
    newinfo = info
    for reponame, repoinfo in info.items():
        repo = git.Repo(repoinfo['path'])
        if author: newinfo[reponame]['n_other_recent'] = 0
        commits = []
        nother = 0
        for commit in repo.iter_commits():
            tzaware = commit.committed_date + commit.committer_tz_offset
            committed = datetime.fromtimestamp(tzaware)
            if (committed < edate) & (committed >= sdate):
                if author:
                    if author.lower() in commit.author.name.lower(): commits.append(commit)
                    else: newinfo[reponame]['n_other_recent'] += 1
                else: commits.append(commit)
        newinfo[reponame]['recent'] = commits
        if newinfo[reponame]['n_other_recent'] == 0: newinfo[reponame].pop('n_other_recent')
    assert newinfo
    return newinfo


def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))


def formatreponame(reponame, fixedwidth):
    formatted = '+-' + '-' * fixedwidth + '-+\n'
    for line in chunkstring(string=reponame, length=fixedwidth):
        formatted += '| {0:^{1}} |'.format(line, fixedwidth)
    formatted += '\n+-' + '-'*(fixedwidth) + '-+\n\n'
    return formatted


def formatmessage(msg):
    """I want the first work of the commit message to be title-cased, but not the rest of the message."""
    chunks = msg.strip().split()
    titled = chunks[0].title() + ' ' + ' '.join(chunks[1:])
    if titled[-1] != ".": titled += "."
    return titled


def summarize(reponame, commits):
    if not any(commits): return ""
    summary = ""
    for commit in commits:
        commitdt = datetime.fromtimestamp(commit.committed_date + commit.committer_tz_offset).strftime("%a %d %b")
        nchanges = commit.stats.total
        if commitdt not in summary: summary += f"_Committed: {commitdt}_\n"
        overview = f"* [{commit.hexsha[:8]}]: {formatmessage(msg=commit.message)}"
        overview += f" // Involves {nchanges['files']} file(s), {nchanges['lines']} lines\n"
        summary += overview
    return summary


def summarizerecent(repos):
    fullsummary = ""
    for reponame, repoinfo in repos.items():
        if not ((any(repoinfo['recent'])) | ('n_other_recent' in repoinfo.keys())): continue
        summary = formatreponame(reponame=f"`{reponame}`", fixedwidth=30)
        if any(repoinfo['recent']):
            recent = summarize(reponame=reponame, commits=repoinfo['recent'])
            summary += recent
        if 'n_other_recent' in repoinfo.keys():
            if repoinfo['n_other_recent'] > 0:
                summary += f"* {repoinfo['n_other_recent']} commits by other users.\n"
        summary += f"* {len(repoinfo['untracked'])} untracked files.\n"
        fullsummary = fullsummary + "\n" + summary
    return fullsummary
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
    today = datetime.now()
    aweekago = today - relativedelta(days=+7)
    repos = recentcommits(info=base, sdate=aweekago, edate=today, author="bailey")
    summary = summarizerecent(repos)

    notes.insert(prefix=formats['header'], text='Repo activity')
    notes.insert(prefix=formats['text'], text=summary)

    notes.to_json(args.outjson)
    notes.to_md(args.outmd)
# }}}
