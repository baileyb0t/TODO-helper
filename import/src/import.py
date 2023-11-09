# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2022, GPL v2 or later
# =========================================
# TODO-helper/import/src/import.py

# ---- dependencies {{{
from pathlib import Path, PosixPath
from sys import stdout
from os.path import isfile, isdir
import argparse
import logging
import subprocess
import re
import pandas as pd
#}}}

# ---- support methods {{{
def get_args():
    """
    this is a relatively generic method for arg handling
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--taskdir", default=None)
    args = parser.parse_args()
    assert Path(args.input).exists()
    assert Path(args.taskdir).exists()
    return args


def get_logger(sname, file_name=None):
    """
    generic method for logging so progress can be tracked
    """
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


def read_textlike(fname):
    """    
    designed for md files (i hardcode '.md' in other places, maybe change the name?)
    filters for lines with 'TODO' mark
    probably a more efficient way than list comp but most notes are just daily files
    so, not worried about too much data loaded on initial file read(s)
    """
    with open(fname, 'r') as f:
        lines = [line for line in f.readlines() if 'todo' in line.lower()]
    if all(pd.isna(lines)): return None
    return lines


def prep_notes(arg):
    if isfile(arg): return PosixPath(arg)
    if isdir(arg): return [path for path in Path(arg).rglob('*.md')]
    return None


def load_input(arg):
    notes = pd.DataFrame({'source': prep_notes(arg)})
    notes['filename'] = notes.source.astype(str).apply(lambda x: x[x.rfind("/")+1:])
    logger.info('digesting files')
    notes['TODO_line'] = notes.source.apply(read_textlike)
    notes = notes.explode("TODO_line").dropna().reset_index(drop=True)
    return notes


def add_tags(df):
    assert 'TODO_line' in df.columns
    df['tag'] = df.TODO_line.apply(
        lambda x: re.findall(patterns['tag'], x) if x else None)
    df = df.explode('tag').fillna('untagged')
    return df


def add_timelines(df):
    df['timeline'] = df.TODO_line.apply(
        lambda x: re.findall(patterns['timeline'], x) if x else None)
    df = df.explode('timeline')
    return df


def clean_TODO(line):
    clean = line.strip()
    if clean[:2] == '- ': clean = clean[2:]
    return clean


def exists_or_mkdir(path):
    """
    need to be able to create new dirs for new tags
    """
    if not Path(path).exists():
        logger.info(f"{path} does not exist. Adding now...")
        subprocess.call(['mkdir', path])
        logger.info("added path.")
    return 1
#}}}

# ---- main {{{
if __name__ == '__main__':

    # setup --- {{{
    # general
    args = get_args()
    logger = get_logger(__name__, f"{args.taskdir}/import.log")
    
    # re
    patterns = {
        "tag": "\(([a-z0-9\-\_]+)\)",
        "timeline": "\[(by[a-z0-9:\s\/\-]*|before[a-z0-9:\s\/\-]*)\]",
    }
    # }}}

    # core routine --- {{{
    logger.info('loading args')
    notes = load_input(args.input)
    
    logger.info('applying minor fixes to legacy notes')
    notes.TODO_line = notes.TODO_line.str.replace('[tech]', '(tech)', regex=False)
    
    logger.info('capturing TODO tags')
    notes = add_tags(notes)
    
    logger.info('capturing TODO timelines')
    notes = add_timelines(notes)
    
    notes['task'] = notes.TODO_line.apply(clean_TODO)
    notes.task = notes.task.str.replace(patterns['tag'], '', regex=True)
    notes[['started', 'last_update', 'completed']] = False
    # }}}

    # outputting tasks --- {{{
    logger.info('preparing to write tasks')
    notes['tagpath'] = notes.tag.apply(lambda tag: f'{args.taskdir}/{tag}')
    assert notes.tagpath.value_counts().head(1).values == \
        notes.tag.value_counts().head(1).values
    assert notes.tagpath.apply(exists_or_mkdir).all()
    
    # TODO: make it so it doesn't overwrite existing dfs?
    # also TODO: this script could be modified to scan non-note files (like scripts) for TODOs
    notes.source = notes.source.astype(str)
    for tag in notes.tag.unique():
        logger.info(f'writing for tag:\t{tag}')
        subset = notes.loc[notes.tag == tag]
        logger.info(f'{subset.shape[0]} TODO records tagged')
        writepath = f'{subset.tagpath.values[0]}/todo.parquet'
        if isfile(writepath): logger.info(f'WARNING: {writepath} already exists and is being overwritten.')
        subset.drop(columns='tagpath').to_parquet(writepath)
    # }}}
    
    logger.info("done.")

#}}}
# done.
